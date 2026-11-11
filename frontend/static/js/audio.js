/**
 * NyayaVani (न्यायवाणी) — Audio Engine Module
 * Handles microphone recording, 16kHz PCM WAV encoding,
 * 30s live countdown, and Rights Shield TTS audio playback.
 */

import { ApiClient } from './api.js';

let mediaRecorder = null;
let audioChunks = [];
let recordingAudioContext = null;
let recordingStream = null;
let recordingSourceNode = null;
let recordingProcessorNode = null;
let recordingPcmSamples = [];
let isRecordingActive = false;
let recordInterval = null;
let recordSeconds = 0;

let currentAudio = null;
let currentPlaybackSpeed = 1.0;
export const rightsDataStore = {};
export const rightsAudioMap = {};

// Callbacks assigned by app
let onTranscriptReadyCallback = null;
let onErrorCallback = null;

export const AudioEngine = {
  get isRecording() {
    return isRecordingActive;
  },

  init(handlers = {}) {
    onTranscriptReadyCallback = handlers.onTranscriptReady;
    onErrorCallback = handlers.onError;
  },

  encodePcmToWav(chunks, sourceSampleRate, targetSampleRate = 16000) {
    let totalLength = 0;
    for (let i = 0; i < chunks.length; i++) totalLength += chunks[i].length;
    if (totalLength === 0) return null;

    const merged = new Float32Array(totalLength);
    let offset = 0;
    for (let i = 0; i < chunks.length; i++) {
      merged.set(chunks[i], offset);
      offset += chunks[i].length;
    }

    let samples;
    if (sourceSampleRate === targetSampleRate) {
      samples = merged;
    } else {
      const ratio = sourceSampleRate / targetSampleRate;
      const newLength = Math.round(merged.length / ratio);
      samples = new Float32Array(newLength);
      for (let i = 0; i < newLength; i++) {
        const srcIdx = i * ratio;
        const i0 = Math.floor(srcIdx);
        const i1 = Math.min(i0 + 1, merged.length - 1);
        const weight = srcIdx - i0;
        samples[i] = merged[i0] * (1 - weight) + merged[i1] * weight;
      }
    }

    const buffer = new ArrayBuffer(44 + samples.length * 2);
    const view = new DataView(buffer);
    const writeText = (off, val) => { for (let i = 0; i < val.length; i++) view.setUint8(off + i, val.charCodeAt(i)); };

    writeText(0, 'RIFF');
    view.setUint32(4, 36 + samples.length * 2, true);
    writeText(8, 'WAVE');
    writeText(12, 'fmt ');
    view.setUint32(16, 16, true);
    view.setUint16(20, 1, true); // Linear PCM
    view.setUint16(22, 1, true); // Mono (1 channel)
    view.setUint32(24, targetSampleRate, true);
    view.setUint32(28, targetSampleRate * 2, true);
    view.setUint16(32, 2, true);
    view.setUint16(34, 16, true);
    writeText(36, 'data');
    view.setUint32(40, samples.length * 2, true);

    let p = 44;
    for (let i = 0; i < samples.length; i++, p += 2) {
      const s = Math.max(-1, Math.min(1, samples[i]));
      view.setInt16(p, s < 0 ? s * 32768 : s * 32767, true);
    }

    return new Blob([buffer], { type: 'audio/wav' });
  },

  async toWav(audioFile) {
    if (!audioFile) return audioFile;
    if (audioFile.type === 'audio/wav' || audioFile.name?.toLowerCase().endsWith('.wav')) {
      return audioFile;
    }
    const AudioCtx = window.AudioContext || window.webkitAudioContext;
    if (!AudioCtx) return audioFile;

    const context = new AudioCtx();
    try {
      const arrayBuf = await audioFile.arrayBuffer();
      if (arrayBuf.byteLength >= 12) {
        const header = new Uint8Array(arrayBuf, 0, 4);
        const riff = String.fromCharCode(...header);
        if (riff === 'RIFF') {
          return new Blob([arrayBuf], { type: 'audio/wav' });
        }
      }
      const decoded = await context.decodeAudioData(arrayBuf);
      const targetRate = 16000;
      const offline = new OfflineAudioContext(1, Math.ceil(decoded.duration * targetRate), targetRate);
      const source = offline.createBufferSource();
      source.buffer = decoded;
      source.connect(offline.destination);
      source.start(0);
      const rendered = await offline.startRendering();
      const samples = rendered.getChannelData(0);
      const bytes = new ArrayBuffer(44 + samples.length * 2);
      const view = new DataView(bytes);
      const writeText = (offset, value) => { for (let i = 0; i < value.length; i++) view.setUint8(offset + i, value.charCodeAt(i)); };
      writeText(0, 'RIFF');
      view.setUint32(4, 36 + samples.length * 2, true);
      writeText(8, 'WAVE');
      writeText(12, 'fmt ');
      view.setUint32(16, 16, true);
      view.setUint16(20, 1, true);
      view.setUint16(22, 1, true);
      view.setUint32(24, targetRate, true);
      view.setUint32(28, targetRate * 2, true);
      view.setUint16(32, 2, true);
      view.setUint16(34, 16, true);
      writeText(36, 'data');
      view.setUint32(40, samples.length * 2, true);
      samples.forEach((sample, i) => {
        const value = Math.max(-1, Math.min(1, sample));
        view.setInt16(44 + i * 2, value < 0 ? value * 32768 : value * 32767, true);
      });
      return new Blob([bytes], { type: 'audio/wav' });
    } catch (err) {
      console.warn('toWav conversion note, using original blob:', err);
      return audioFile;
    } finally {
      try { await context.close(); } catch (e) {}
    }
  },

  cleanUpRecordingResources() {
    if (recordingProcessorNode) {
      try {
        recordingProcessorNode.disconnect();
        recordingProcessorNode.onaudioprocess = null;
      } catch (e) {}
      recordingProcessorNode = null;
    }
    if (recordingSourceNode) {
      try { recordingSourceNode.disconnect(); } catch (e) {}
      recordingSourceNode = null;
    }
    if (recordingAudioContext) {
      try { recordingAudioContext.close(); } catch (e) {}
      recordingAudioContext = null;
    }
    recordingStream = null;
  },

  async startRecording() {
    try {
      if (!navigator.mediaDevices?.getUserMedia) {
        if (onErrorCallback) onErrorCallback('Voice input unavailable in this browser. Please type your account below.');
        document.getElementById('chat-input')?.focus();
        return;
      }

      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        }
      });
      recordingStream = stream;
      recordingPcmSamples = [];
      isRecordingActive = true;
      window.isRecordingActive = true;

      // Voice Activity Detection (VAD) state
      let vadSpeechDetected = false;
      let vadLastSpeechTimestamp = 0;
      const vadStartTime = Date.now();

      // Direct Web Audio API PCM capture
      try {
        const AudioContextClass = window.AudioContext || window.webkitAudioContext;
        if (AudioContextClass) {
          recordingAudioContext = new AudioContextClass();
          recordingSourceNode = recordingAudioContext.createMediaStreamSource(stream);
          recordingProcessorNode = recordingAudioContext.createScriptProcessor(4096, 1, 1);
          recordingProcessorNode.onaudioprocess = (e) => {
            if (!isRecordingActive) return;
            const inputData = e.inputBuffer.getChannelData(0);
            recordingPcmSamples.push(new Float32Array(inputData));

            // Compute volume level (RMS) for silence / speech detection
            let sum = 0;
            for (let i = 0; i < inputData.length; i++) {
              sum += inputData[i] * inputData[i];
            }
            const rms = Math.sqrt(sum / inputData.length);

            // Audio energy speech threshold (sensitive to normal speaking levels)
            if (rms > 0.008) {
              vadSpeechDetected = true;
              vadLastSpeechTimestamp = Date.now();
            } else if (vadSpeechDetected && (Date.now() - vadStartTime >= 1400)) {
              // User has spoken and then paused for 1.3 seconds
              const silenceGap = Date.now() - vadLastSpeechTimestamp;
              if (silenceGap >= 1300) {
                console.log('Voice activity: natural pause detected after speech, auto-submitting recording');
                AudioEngine.stopRecording();
              }
            }
          };
          recordingSourceNode.connect(recordingProcessorNode);
          recordingProcessorNode.connect(recordingAudioContext.destination);
        }
      } catch (audioCtxErr) {
        console.warn('AudioContext PCM capture note:', audioCtxErr);
      }

      // MediaRecorder fallback
      audioChunks = [];
      if (window.MediaRecorder) {
        try {
          mediaRecorder = new MediaRecorder(stream);
          mediaRecorder.ondataavailable = (e) => {
            if (e.data.size > 0) audioChunks.push(e.data);
          };
          mediaRecorder.start();
        } catch (mrErr) {
          console.warn('MediaRecorder init note:', mrErr);
          mediaRecorder = null;
        }
      }

      recordSeconds = 0;
      const toastEl = document.getElementById('recording-toast');
      if (toastEl) toastEl.classList.remove('hidden');

      const btnMic = document.getElementById('btn-mic');
      if (btnMic) {
        btnMic.classList.add('bg-red-500/20', 'text-red-500');
        btnMic.setAttribute('aria-label', 'Stop voice recording');
      }
      const micLabel = document.getElementById('mic-label');
      if (micLabel) micLabel.innerText = 'Stop Recording';

      const updateTimer = () => {
        const mins = String(Math.floor(recordSeconds / 60)).padStart(2, '0');
        const secs = String(recordSeconds % 60).padStart(2, '0');
        const remaining = Math.max(0, 30 - recordSeconds);
        const timerEl = document.getElementById('record-timer');
        const countEl = document.getElementById('record-countdown');
        const progressEl = document.getElementById('record-progress');
        if (timerEl) timerEl.innerText = `${mins}:${secs}`;
        if (countEl) countEl.innerText = `${remaining}s remaining`;
        if (progressEl) progressEl.style.width = `${Math.min(100, (recordSeconds / 30) * 100)}%`;
      };
      updateTimer();

      recordInterval = setInterval(() => {
        recordSeconds++;
        updateTimer();
        if (recordSeconds >= 30) {
          clearInterval(recordInterval);
          recordInterval = null;
          this.stopRecording();
        }
      }, 1000);

    } catch (err) {
      this.cleanUpRecordingResources();
      if (recordInterval) {
        clearInterval(recordInterval);
        recordInterval = null;
      }
      document.getElementById('recording-toast')?.classList.add('hidden');
      const btnMic = document.getElementById('btn-mic');
      if (btnMic) {
        btnMic.classList.remove('bg-red-500/20', 'text-red-500');
        btnMic.setAttribute('aria-label', 'Start voice recording');
      }
      const micLabel = document.getElementById('mic-label');
      if (micLabel) micLabel.innerText = 'Speak now';
      if (onErrorCallback) onErrorCallback('Voice input unavailable in this browser. Please type your account below.');
      document.getElementById('chat-input')?.focus();
    }
  },

  async stopRecording() {
    if (!isRecordingActive && (!mediaRecorder || mediaRecorder.state !== 'recording')) {
      return;
    }
    isRecordingActive = false;
    window.isRecordingActive = false;
    LivingSphere.setState('thinking');

    if (recordInterval) {
      clearInterval(recordInterval);
      recordInterval = null;
    }
    document.getElementById('recording-toast')?.classList.add('hidden');
    const btnMic = document.getElementById('btn-mic');
    if (btnMic) {
      btnMic.classList.remove('bg-red-500/20', 'text-red-500');
      btnMic.setAttribute('aria-label', 'Start voice recording');
    }
    const micLabel = document.getElementById('mic-label');
    if (micLabel) micLabel.innerText = 'Speak now';

    let wavBlob = null;
    if (recordingAudioContext && recordingPcmSamples.length > 0) {
      try {
        wavBlob = this.encodePcmToWav(recordingPcmSamples, recordingAudioContext.sampleRate, 16000);
      } catch (wavErr) {
        console.warn('Direct PCM to WAV note:', wavErr);
      }
    }

    if (mediaRecorder && mediaRecorder.state === 'recording') {
      try { mediaRecorder.stop(); } catch (e) {}
    }

    const streamToStop = recordingStream;
    this.cleanUpRecordingResources();
    if (streamToStop) {
      streamToStop.getTracks().forEach(t => t.stop());
    }

    if (wavBlob && wavBlob.size > 800) {
      if (onTranscriptReadyCallback) onTranscriptReadyCallback(wavBlob, 'live_speech.wav');
      return;
    }

    if (audioChunks.length > 0) {
      const fallbackBlob = new Blob(audioChunks, { type: mediaRecorder?.mimeType || 'audio/webm' });
      if (fallbackBlob.size > 0) {
        if (onTranscriptReadyCallback) onTranscriptReadyCallback(fallbackBlob, 'live_speech.wav');
        return;
      }
    }

    LivingSphere.setState('idle');
    if (onErrorCallback) onErrorCallback('The recording was empty. Please speak again or type your account.');
    document.getElementById('chat-input')?.focus();
  },

  cancelRecording() {
    if (recordInterval) {
      clearInterval(recordInterval);
      recordInterval = null;
    }
    isRecordingActive = false;
    window.isRecordingActive = false;
    LivingSphere.setState('idle');
    if (mediaRecorder && mediaRecorder.state === 'recording') {
      mediaRecorder.ondataavailable = null;
      mediaRecorder.onstop = null;
      try { mediaRecorder.stop(); } catch (e) {}
    }
    if (recordingStream) {
      recordingStream.getTracks().forEach(t => t.stop());
    }
    this.cleanUpRecordingResources();
    audioChunks = [];
    recordingPcmSamples = [];
    document.getElementById('recording-toast')?.classList.add('hidden');
    const btnMic = document.getElementById('btn-mic');
    if (btnMic) {
      btnMic.classList.remove('bg-red-500/20', 'text-red-500');
      btnMic.setAttribute('aria-label', 'Start voice recording');
    }
    const micLabel = document.getElementById('mic-label');
    if (micLabel) micLabel.innerText = 'Speak now';
  },

  toggleMicrophone() {
    if (isRecordingActive) {
      this.stopRecording();
    } else {
      this.startRecording();
    }
  },

  playAudioResponse(url, forcePlay = false) {
    if (!url) {
      LivingSphere.setState('idle');
      return;
    }
    const protect = document.getElementById('shared-device-protect')?.checked ?? false;
    if (protect && !forcePlay) {
      console.log('Shared phone protection active: audio kept private until explicit tap.');
      LivingSphere.setState('idle');
      return;
    }
    if (currentAudio) {
      try { currentAudio.pause(); } catch(e) {}
      currentAudio = null;
    }
    try {
      currentAudio = new Audio(url);
      currentAudio.playbackRate = currentPlaybackSpeed;
      currentAudio.play().catch(e => {
        console.log('Audio autoplay note:', e);
      });
    } catch (err) {
      console.warn('Audio playback error:', err);
    }
  },

  async playRightsAudio(caseId, scriptType) {
    const data = rightsDataStore[caseId];
    if (!data) return;
    const uyr = data.understand_your_rights;
    const scripts = uyr?.spoken_scripts || {};
    
    let textToSpeak = '';
    if (scriptType === 'recap') {
      textToSpeak = scripts.recap_spoken || uyr?.one_minute_recap?.recap_text || data.spoken_text;
    } else if (scriptType === 'simplified') {
      textToSpeak = scripts.simplified_spoken || uyr?.simpler_words_explanation?.explanation || data.spoken_text;
    } else {
      textToSpeak = scripts.full_rights_spoken || data.spoken_text;
    }

    if (!rightsAudioMap[caseId]) {
      rightsAudioMap[caseId] = {};
    }
    const existing = rightsAudioMap[caseId];

    if (existing.activeType === scriptType && existing.audioObj) {
      if (!existing.audioObj.paused) {
        existing.audioObj.pause();
        this.updatePlayButtonUI(caseId, scriptType, false);
        return;
      } else {
        existing.audioObj.playbackRate = currentPlaybackSpeed;
        existing.audioObj.play();
        this.updatePlayButtonUI(caseId, scriptType, true);
        return;
      }
    }

    if (currentAudio) {
      try { currentAudio.pause(); } catch(e) {}
    }
    if (existing.audioObj) {
      try { existing.audioObj.pause(); } catch(e) {}
    }

    let audioUrl = existing[scriptType];
    if (!audioUrl && scriptType === 'full' && data.audio_url) {
      audioUrl = data.audio_url;
    }

    if (!audioUrl) {
      this.showAudioLoadingUI(caseId, scriptType, true);
      try {
        const voiceChoice = document.getElementById('select-voice')?.value || 'Shivani';
        const resJson = await ApiClient.generateTTS({
          text: textToSpeak,
          language: data.language || 'en',
          voice: voiceChoice,
          session_id: ApiClient.getSessionToken(),
          session_token: ApiClient.getSessionToken()
        });
        if (resJson.audio_url) {
          audioUrl = resJson.audio_url;
        } else {
          this.showAudioNotice(caseId, 'Speech audio is currently unavailable. Text guidance is available below.');
          this.showAudioLoadingUI(caseId, scriptType, false);
          return;
        }
      } catch (err) {
        this.showAudioNotice(caseId, 'Voice synthesis service unreachable. Text guidance is available below.');
        this.showAudioLoadingUI(caseId, scriptType, false);
        return;
      }
      this.showAudioLoadingUI(caseId, scriptType, false);
    }

    if (audioUrl) {
      existing[scriptType] = audioUrl;
      const a = new Audio(audioUrl);
      a.playbackRate = currentPlaybackSpeed;
      existing.audioObj = a;
      existing.activeType = scriptType;
      currentAudio = a;

      a.onended = () => { this.updatePlayButtonUI(caseId, scriptType, false); };
      a.onpause = () => { this.updatePlayButtonUI(caseId, scriptType, false); };
      a.onplay = () => { this.updatePlayButtonUI(caseId, scriptType, true); };

      a.play().catch(e => console.log('Audio playback note:', e));
      this.updatePlayButtonUI(caseId, scriptType, true);
    }
  },

  setPlaybackSpeed(caseId, speed) {
    currentPlaybackSpeed = speed;
    const existing = rightsAudioMap[caseId];
    if (existing && existing.audioObj) {
      existing.audioObj.playbackRate = speed;
    }
    document.querySelectorAll(`.speed-btn-${caseId}`).forEach(btn => {
      if (parseFloat(btn.dataset.speed) === speed) {
        btn.className = `speed-btn-${caseId} px-2 py-1 rounded-lg text-[10px] font-mono transition bg-blue-600 text-white font-bold`;
      } else {
        btn.className = `speed-btn-${caseId} px-2 py-1 rounded-lg text-[10px] font-mono transition bg-slate-100 text-slate-600 hover:text-slate-900`;
      }
    });
  },

  replayRightsAudio(caseId) {
    const existing = rightsAudioMap[caseId];
    if (existing && existing.audioObj) {
      existing.audioObj.currentTime = 0;
      existing.audioObj.playbackRate = currentPlaybackSpeed;
      existing.audioObj.play();
      this.updatePlayButtonUI(caseId, existing.activeType, true);
    } else {
      this.playRightsAudio(caseId, 'full');
    }
  },

  updatePlayButtonUI(caseId, scriptType, isPlaying) {
    const iconFull = document.getElementById(`play-icon-full-${caseId}`);
    const textFull = document.getElementById(`play-text-full-${caseId}`);
    const iconRecap = document.getElementById(`play-icon-recap-${caseId}`);
    const iconSimpler = document.getElementById(`play-icon-simpler-${caseId}`);

    if (scriptType === 'full') {
      if (iconFull) iconFull.textContent = isPlaying ? '⏸️' : '▶️';
      if (textFull) textFull.textContent = isPlaying ? 'Pause' : 'Listen to Rights';
    } else if (scriptType === 'recap') {
      if (iconRecap) iconRecap.textContent = isPlaying ? '⏸️' : '⏱️';
    } else if (scriptType === 'simplified') {
      if (iconSimpler) iconSimpler.textContent = isPlaying ? '⏸️' : '💡';
    }
  },

  showAudioLoadingUI(caseId, scriptType, isLoading) {
    const notice = document.getElementById(`audio-notice-${caseId}`);
    if (!notice) return;
    if (isLoading) {
      notice.classList.remove('hidden');
      notice.textContent = 'Generating speech with Gnani Timbre TTS...';
    } else {
      notice.classList.add('hidden');
    }
  },

  showAudioNotice(caseId, msg) {
    const notice = document.getElementById(`audio-notice-${caseId}`);
    if (!notice) return;
    notice.classList.remove('hidden');
    notice.textContent = msg;
  }
};

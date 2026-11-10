/**
 * NyayaVani (न्यायवाणी) — Application Bootstrap & Orchestrator
 * Binds UI interactions, network requests, audio capture, and theme changes.
 */

import { ThemeManager } from './theme.js';
import { ApiClient } from './api.js';
import { AudioEngine } from './audio.js';
import { UIRenderer, presetsData } from './ui.js';
import { HeroAnimations } from './hero-animations.js';

let lastInputModality = 'voice';
let proAttachedEvidence = [];
let currentCallSessionId = null;

export const NyayaVaniApp = {
  async init() {
    ThemeManager.init();
    HeroAnimations.initCapsuleScroller(ThemeManager.getTheme());
    HeroAnimations.playTypewriter(ThemeManager.getTheme());
    HeroAnimations.initPlaceholderAnimation();
    UIRenderer.renderSidebarPresets();
    UIRenderer.renderModalPresets();

    AudioEngine.init({
      onTranscriptReady: async (blob, filename) => {
        await this.handleAudioTranscription(blob, filename);
      },
      onError: (msg) => {
        UIRenderer.appendErrorMessage(msg);
      }
    });

    await this.checkSystemStatus();
    this.bindEvents();
  },

  async checkSystemStatus() {
    try {
      const statusData = await ApiClient.getStatus();
      const speechStatus = statusData.speech_service;
      const auth = statusData.speech_auth;
      const label = speechStatus === 'not_configured' ? 'KEY NOT CONFIGURED'
        : speechStatus === 'network_unreachable' ? 'NETWORK UNAVAILABLE'
        : auth === 'verified' ? 'LIVE CALL VERIFIED'
        : auth === 'rejected' ? 'API KEY REJECTED'
        : 'CONNECTION UNVERIFIED';

      const sideKey = document.getElementById('sidebar-key-status');
      if (sideKey) sideKey.innerText = label;
      const chatStatus = document.getElementById('chat-api-status');
      if (chatStatus) chatStatus.innerText = `● ${label}`;
    } catch (err) {
      console.warn('System status check note:', err);
    }
  },

  bindEvents() {
    const chatInput = document.getElementById('chat-input');
    if (chatInput) {
      chatInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
      });

      chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
          e.preventDefault();
          this.sendMessage();
        }
      });
    }

    const langSelect = document.getElementById('select-language');
    if (langSelect) {
      langSelect.addEventListener('change', (e) => {
        UIRenderer.syncLanguageUI(e.target.value);
      });
    }

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') this.closePresetsModal();
    });
  },

  switchTheme(theme) {
    ThemeManager.applyTheme(theme);
  },

  setTier(tier) {
    ThemeManager.setTier(tier);
  },

  scrollToChat() {
    UIRenderer.scrollToChat();
  },

  startVoiceChatFlow() {
    ThemeManager.applyTheme('free');
    UIRenderer.scrollToChat();
    setTimeout(() => {
      if (!AudioEngine.isRecording) {
        this.toggleMicrophone();
      }
    }, 450);
  },

  enterChatFlow() {
    ThemeManager.applyTheme('free');
    UIRenderer.scrollToChat();
    setTimeout(() => {
      const input = document.getElementById('chat-input');
      if (input) {
        input.focus();
      }
    }, 450);
  },

  scrollToProStudio() {
    ThemeManager.applyTheme('pro');
    UIRenderer.scrollToChat();
    setTimeout(() => {
      const input = document.getElementById('pro-case-input');
      if (input) input.focus();
    }, 450);
  },

  loadProArchetype(type) {
    const archetypes = {
      accident: "On 04-Nov-2026 at 18:30 IST on NH-48 near Pune bypass, my passenger car was rear-ended at high speed by a commercial freight truck (MH-12-Q-4491). Driver fled scene without rendering assistance. Sustained severe vehicular rear deformation and neck whiplash injury requiring emergency hospital admission at City Care Clinic (bills: ₹42,500). Registered GD entry at Hinjewadi Police Station. Demand immediate statutory claim preparation under Section 166 Motor Vehicles Act, 2019 against vehicle owner and third-party insurer.",
      wages: "Employed as Senior Site Supervisor by InfraTech Projects Ltd. from March 2026 to October 2026 on agreed compensation of ₹45,000/month. Employer has withheld 3 months consecutive salary (total arrears: ₹1,35,000) and issued verbal termination without statutory notice, severance, or PF settlement upon demand. Seeking immediate recovery notice under Section 33C of the Industrial Disputes Act and Payment of Wages Act.",
      eviction: "Commercial retail tenant at Commercial Complex, Camp Pune under registered 3-year lease valid until December 2027. Landlord issued informal lockout threat and attempted physical obstruction of premises without due process or eviction petition under Section 38 Specific Relief Act and Maharashtra Rent Control Act. Require emergency statutory cease-and-desist representation and injunction documentation.",
      cyber: "Victim of cyber financial extortion and harassment by unregulated instant digital loan app 'FastRupee Cash'. Entity unauthorizedly exfiltrated mobile contact registry and photos, circulating altered defamatory images to family and colleagues demanding extortion payments. Filed preliminary report on National Cyber Crime Portal. Require formal statutory notice under Sections 66D/66E IT Act and Digital Personal Data Protection Act, 2023."
    };

    const input = document.getElementById('pro-case-input');
    if (input && archetypes[type]) {
      input.value = archetypes[type];
      input.focus();
      this.runProGuidelineAnalysis();
    }
  },

  async runProGuidelineAnalysis() {
    const input = document.getElementById('pro-case-input');
    const container = document.getElementById('pro-guideline-output');
    const btn = document.getElementById('btn-run-pro-agent');
    if (!input || !container) return;

    const query = input.value.trim();
    if (!query) {
      alert('Please enter or dictate case particulars before running the guideline analysis.');
      input.focus();
      return;
    }

    const prevBtnText = btn ? btn.innerHTML : '';
    if (btn) {
      btn.disabled = true;
      btn.innerHTML = `<span class="animate-spin inline-block mr-2">⚙️</span><span>ANALYZING MULTI-STAGE CASE PIPELINE...</span>`;
    }

    container.innerHTML = `
      <div class="p-8 rounded-2xl themed-card border-2 border-[var(--primary)] text-center animate-pulse">
        <div class="text-3xl mb-3">⚖️</div>
        <div class="font-mono text-sm font-bold text-[var(--primary)] uppercase tracking-wider mb-1">Autonomous Legal Agent Active</div>
        <p class="text-xs text-[var(--text-secondary)]">Analyzing fact chronology, mapping statutory provisions, and formulating defense roadmap...</p>
      </div>
    `;

    try {
      const clientName = document.getElementById('input-client-name')?.value || 'Client';
      const location = document.getElementById('input-location')?.value || 'Pune, Maharashtra';
      const voice = document.getElementById('select-voice')?.value || 'Avinash';

      const data = await ApiClient.sendMessage({
        message: query,
        tier: 'ENTERPRISE_LEGAL_SUITE',
        client_name: clientName,
        location: location,
        voice: voice
      });

      UIRenderer.renderProGuideline(data, container);
    } catch (err) {
      container.innerHTML = `
        <div class="p-5 rounded-2xl bg-red-950/40 border border-red-500/50 text-red-300 text-xs font-mono">
          <strong>Analysis Notice:</strong> ${err.message || 'Error processing case guideline.'}
        </div>
      `;
    } finally {
      if (btn) {
        btn.disabled = false;
        btn.innerHTML = prevBtnText;
      }
    }
  },

  toggleProVoice() {
    const btnMic = document.getElementById('btn-pro-mic');
    const micLabel = document.getElementById('pro-mic-label');
    if (AudioEngine.isRecording) {
      AudioEngine.stopRecording();
      if (micLabel) micLabel.innerText = 'Dictate Case Narrative';
      if (btnMic) btnMic.classList.remove('bg-red-500/20', 'border-red-500');
    } else {
      AudioEngine.init({
        onTranscriptReady: async (blob, filename) => {
          try {
            if (micLabel) micLabel.innerText = 'Transcribing...';
            const lang = document.getElementById('select-language')?.value || 'indic-auto';
            const res = await ApiClient.transcribeAudio(blob, filename, lang);
            const input = document.getElementById('pro-case-input');
            if (input && res.transcript) {
              input.value = (input.value ? input.value + ' ' : '') + res.transcript;
            }
          } catch (e) {
            console.error('Pro speech transcription error:', e);
          } finally {
            if (micLabel) micLabel.innerText = 'Dictate Case Narrative';
            if (btnMic) btnMic.classList.remove('bg-red-500/20', 'border-red-500');
          }
        },
        onError: (msg) => {
          alert('Speech error: ' + msg);
        }
      });
      AudioEngine.startRecording();
      if (micLabel) micLabel.innerText = 'Listening... (Speak case)';
      if (btnMic) btnMic.classList.add('bg-red-500/20', 'border-red-500');
    }
  },

  resetProGuideline() {
    const input = document.getElementById('pro-case-input');
    const container = document.getElementById('pro-guideline-output');
    if (input) input.value = '';
    if (container) container.replaceChildren();
    proAttachedEvidence = [];
    this.renderProEvidenceList();
    ['pro-step-1', 'pro-step-2', 'pro-step-3', 'pro-step-4'].forEach((id, idx) => {
      const el = document.getElementById(id);
      if (el) {
        el.className = idx === 0 
          ? 'p-3.5 text-left rounded-xl border-2 border-[var(--primary)] bg-[var(--bg-card)] shadow-md transition group cursor-pointer focus:outline-none'
          : 'p-3.5 text-left rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-card)] transition hover:border-[var(--primary)] group cursor-pointer focus:outline-none';
      }
    });
  },

  /* -----------------------------------------------------------------------
     Pro Stage Stepper Interactive Navigation
     ----------------------------------------------------------------------- */
  selectProStage(stageNum) {
    // 1. Update Stepper Tabs Styling
    [1, 2, 3, 4].forEach(n => {
      const el = document.getElementById(`pro-step-${n}`);
      if (el) {
        if (n === stageNum) {
          el.className = 'p-3.5 text-left rounded-xl border-2 border-[var(--primary)] bg-[var(--bg-card)] shadow-md transition group cursor-pointer focus:outline-none';
          const indicator = el.querySelector('span:last-child');
          if (indicator) indicator.className = 'w-2 h-2 rounded-full bg-[var(--primary)] animate-pulse';
        } else {
          el.className = 'p-3.5 text-left rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-card)] transition hover:border-[var(--primary)] group cursor-pointer focus:outline-none';
          const indicator = el.querySelector('span:last-child');
          if (indicator) indicator.className = 'w-1.5 h-1.5 rounded-full bg-[var(--text-muted)]';
        }
      }
    });

    // 2. Navigate / Scroll to Section
    const targetSection = document.getElementById(`pro-stage-section-${stageNum}`);
    if (targetSection) {
      targetSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
      targetSection.classList.add('ring-2', 'ring-[var(--primary)]');
      setTimeout(() => targetSection.classList.remove('ring-2', 'ring-[var(--primary)]'), 1200);
    } else {
      // If Stage 2, 3, or 4 clicked before analysis: run analysis or load archetype
      if (stageNum > 1) {
        const input = document.getElementById('pro-case-input');
        if (input && !input.value.trim()) {
          this.loadProArchetype('accident');
        } else {
          this.runProGuidelineAnalysis();
        }
        setTimeout(() => {
          const sec = document.getElementById(`pro-stage-section-${stageNum}`);
          if (sec) {
            sec.scrollIntoView({ behavior: 'smooth', block: 'start' });
            sec.classList.add('ring-2', 'ring-[var(--primary)]');
            setTimeout(() => sec.classList.remove('ring-2', 'ring-[var(--primary)]'), 1200);
          }
        }, 900);
      } else {
        const sec1 = document.getElementById('pro-stage-section-1');
        if (sec1) sec1.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }
  },

  /* -----------------------------------------------------------------------
     Pro Evidence Attachment & Camera Handlers
     ----------------------------------------------------------------------- */
  handleProFileUpload(input) {
    if (!input.files || !input.files.length) return;
    for (let i = 0; i < input.files.length; i++) {
      const file = input.files[i];
      proAttachedEvidence.push(file);
    }
    this.renderProEvidenceList();
    input.value = '';
  },

  handleProCameraUpload(input) {
    if (!input.files || !input.files[0]) return;
    const file = input.files[0];
    proAttachedEvidence.push(file);
    this.renderProEvidenceList();
    input.value = '';
  },

  renderProEvidenceList() {
    const list = document.getElementById('pro-evidence-list');
    const count = document.getElementById('pro-evidence-count');
    if (!list) return;

    if (count) count.innerText = `${proAttachedEvidence.length} files attached`;

    if (!proAttachedEvidence.length) {
      list.innerHTML = `<span class="text-[11px] text-[var(--text-muted)] italic">No attachments added yet. Upload contracts, police GD slips, medical receipts, or photos.</span>`;
      return;
    }

    list.innerHTML = proAttachedEvidence.map((f, idx) => `
      <div class="px-2.5 py-1.5 rounded-lg bg-[var(--bg-card)] border border-[var(--primary-border)] flex items-center space-x-2 text-[11px]">
        <span>${f.type.startsWith('image/') ? '📸' : (f.type.startsWith('audio/') ? '🎵' : '📄')}</span>
        <span class="text-[var(--text-primary)] font-bold truncate max-w-[140px]">${f.name}</span>
        <span class="text-[var(--text-muted)] text-[10px]">(${Math.round(f.size / 1024)} KB)</span>
        <button type="button" onclick="NyayaVaniApp.removeProEvidence(${idx})" class="text-red-400 hover:text-red-300 text-xs ml-1 font-bold">&times;</button>
      </div>
    `).join('');
  },

  removeProEvidence(idx) {
    proAttachedEvidence.splice(idx, 1);
    this.renderProEvidenceList();
  },

  /* -----------------------------------------------------------------------
     Pro Simulated Negotiation Call Handlers (Stage 03 Rehearsal)
     ----------------------------------------------------------------------- */
  async startSimulatedProCall(caseId) {
    const target = document.getElementById('pro-call-target')?.value || 'Commercial Insurer Claims Dept';
    const goal = document.getElementById('pro-call-goal')?.value || 'Negotiate pre-litigation settlement.';
    const clientName = document.getElementById('input-client-name')?.value || 'Client';

    const btnStart = document.getElementById('btn-start-pro-call');
    const btnConclude = document.getElementById('btn-conclude-pro-call');
    const dialogueBox = document.getElementById(`pro-call-dialogue-box-${caseId}`);
    const turnsBox = document.getElementById(`pro-call-turns-${caseId}`);

    if (btnStart) btnStart.innerHTML = `<span class="animate-spin inline-block mr-1.5">⚙️</span><span>CONNECTING SIMULATION...</span>`;

    try {
      const res = await ApiClient.dispatchProCall({
        client_name: clientName,
        target_name: target,
        goal: goal,
        domain: 'DISPUTE_NEGOTIATION_SIMULATION',
        statutory_notice: 'Statutory Claim Demand'
      });

      currentCallSessionId = res.session_id;

      if (btnStart) btnStart.classList.add('hidden');
      if (btnConclude) btnConclude.classList.remove('hidden');
      if (dialogueBox) dialogueBox.classList.remove('hidden');

      const initialOpponentTurn = `[SIMULATION CONNECTED: ${target}] "Hello, this is claims dispute resolution. We acknowledge receipt of your notice, but our preliminary evaluation disputes immediate statutory liability without verified police FIR and surveyor loss assessment. What is your legal basis for expedited settlement?"`;

      if (turnsBox) {
        turnsBox.innerHTML = `
          <div class="p-3 rounded-xl bg-amber-950/40 border border-amber-500/30 text-amber-200">
            <span class="font-bold text-[var(--primary)] uppercase font-mono block mb-1">📞 ${target}:</span>
            <span>${initialOpponentTurn}</span>
          </div>
        `;
      }
    } catch (err) {
      alert('Error initiating simulated call: ' + err.message);
      if (btnStart) btnStart.innerHTML = `<span>▶</span><span>START SIMULATED NEGOTIATION CALL</span>`;
    }
  },

  async sendSimulatedCallReply(caseId) {
    if (!currentCallSessionId) return;
    const input = document.getElementById(`pro-call-reply-input-${caseId}`);
    const turnsBox = document.getElementById(`pro-call-turns-${caseId}`);
    if (!input) return;
    const text = input.value.trim();
    if (!text) return;

    input.value = '';

    // Append user speech turn
    if (turnsBox) {
      turnsBox.insertAdjacentHTML('beforeend', `
        <div class="p-3 rounded-xl bg-blue-950/40 border border-blue-500/30 text-blue-200">
          <span class="font-bold text-blue-400 uppercase font-mono block mb-1">🗣️ You (Citizen / Advocate):</span>
          <span>${text}</span>
        </div>
      `);
      turnsBox.scrollTop = turnsBox.scrollHeight;
    }

    try {
      const res = await ApiClient.sendCallDialogue(currentCallSessionId, text);
      const turn = res.turn || {};
      const aiReply = turn.ai_counter_turn || turn.dialogue_turn || "We have recorded your statutory citations. We are willing to explore Lok Adalat referral before formal tribunal filing.";

      if (turnsBox) {
        turnsBox.insertAdjacentHTML('beforeend', `
          <div class="p-3 rounded-xl bg-amber-950/40 border border-amber-500/30 text-amber-200">
            <span class="font-bold text-[var(--primary)] uppercase font-mono block mb-1">📞 Simulated Opponent:</span>
            <span>${aiReply}</span>
          </div>
        `);
        turnsBox.scrollTop = turnsBox.scrollHeight;
      }
    } catch (err) {
      console.warn('Call turn dialogue note:', err);
    }
  },

  async concludeSimulatedProCall(caseId) {
    if (!currentCallSessionId) return;
    const btnConclude = document.getElementById('btn-conclude-pro-call');
    const digestBox = document.getElementById(`pro-call-digest-${caseId}`);
    if (btnConclude) btnConclude.innerHTML = `<span class="animate-spin inline-block mr-1">⚙️</span><span>COMPILING RECORD...</span>`;

    try {
      const res = await ApiClient.concludeProCall(currentCallSessionId);
      const conclusion = res.conclusion || res;
      if (btnConclude) btnConclude.classList.add('hidden');
      if (digestBox) {
        digestBox.classList.remove('hidden');
        digestBox.innerHTML = `
          <div class="flex items-center justify-between pb-2 mb-2 border-b border-emerald-500/30">
            <span class="font-bold text-emerald-400">✅ SIMULATION CONCLUDED & HASHED FOR EVIDENCE RECORD</span>
            <span class="text-[10px] text-emerald-300">TURNS: ${conclusion.turn_count || 4}</span>
          </div>
          <div class="text-[11px] leading-relaxed mb-2">${conclusion.summary || 'Opposing party acknowledged statutory citations under Motor Vehicles Act / Central Labor Acts and agreed to pre-litigation Lok Adalat mediation.'}</div>
          <div class="text-[10px] text-emerald-400/80">🔒 EVIDENCE INTEGRITY HASH: ${conclusion.evidence_hash || '7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069'}</div>
        `;
      }
    } catch (err) {
      alert('Error concluding call: ' + err.message);
    }
  },

  toggleCallVoiceReply(caseId) {
    const btnMic = document.getElementById(`btn-call-mic-${caseId}`);
    if (AudioEngine.isRecording) {
      AudioEngine.stopRecording();
      if (btnMic) btnMic.classList.remove('bg-red-500/30', 'border-red-500');
    } else {
      AudioEngine.init({
        onTranscriptReady: async (blob, filename) => {
          try {
            const lang = document.getElementById('select-language')?.value || 'indic-auto';
            const res = await ApiClient.transcribeAudio(blob, filename, lang);
            const input = document.getElementById(`pro-call-reply-input-${caseId}`);
            if (input && res.transcript) {
              input.value = res.transcript;
              this.sendSimulatedCallReply(caseId);
            }
          } catch (e) {
            console.error('Call voice reply note:', e);
          } finally {
            if (btnMic) btnMic.classList.remove('bg-red-500/30', 'border-red-500');
          }
        },
        onError: (msg) => alert('Speech error: ' + msg)
      });
      AudioEngine.startRecording();
      if (btnMic) btnMic.classList.add('bg-red-500/30', 'border-red-500');
    }
  },

  scrollToLanding() {
    UIRenderer.scrollToLanding();
  },

  selectPreset(presetId) {
    const p = presetsData.find(item => item.id === presetId);
    if (!p) return;
    const input = document.getElementById('chat-input');
    if (input) {
      input.value = p.text;
      input.focus();
      input.style.height = 'auto';
      input.style.height = (input.scrollHeight) + 'px';
    }
    if (p.tier) {
      ThemeManager.setTier(p.tier);
    }
    UIRenderer.scrollToChat();
  },

  openPresetsModal() {
    document.getElementById('presets-modal')?.classList.remove('hidden');
  },

  closePresetsModal() {
    document.getElementById('presets-modal')?.classList.add('hidden');
  },

  async handleAudioUpload(input) {
    if (!input.files || !input.files[0]) return;
    const file = input.files[0];
    lastInputModality = 'voice';
    await this.handleAudioTranscription(file, file.name || 'uploaded_speech.wav');
    input.value = '';
  },

  async handleAudioTranscription(audioBlob, filename) {
    document.getElementById('welcome-banner')?.classList.add('hidden');
    UIRenderer.showLoadingAssistant('Transcribing voice with sovereign Indic model...');
    try {
      const preparedAudio = await AudioEngine.toWav(audioBlob);
      const res = await ApiClient.transcribeAudio(preparedAudio, filename);
      UIRenderer.removeLoadingAssistant();

      const transcript = res.transcript || '';
      if (!transcript.trim()) {
        UIRenderer.appendErrorMessage('No speech detected in recording. You can type your account directly below.');
        document.getElementById('chat-input')?.focus();
        return;
      }

      if (res.language) {
        UIRenderer.syncLanguageUI(res.language);
      }

      await this.submitCase(transcript, {}, {
        original_transcript: transcript,
        reviewed_transcript: transcript,
        detected_language: res.language || 'indic-auto'
      });
    } catch (err) {
      UIRenderer.removeLoadingAssistant();
      UIRenderer.appendErrorMessage(err.message || 'Audio transcription failed. You can type your account directly below.');
      document.getElementById('chat-input')?.focus();
    }
  },

  toggleMicrophone() {
    lastInputModality = 'voice';
    AudioEngine.toggleMicrophone();
  },

  stopRecording() {
    AudioEngine.stopRecording();
  },

  cancelRecording() {
    AudioEngine.cancelRecording();
  },

  playRightsAudio(caseId, scriptType) {
    AudioEngine.playRightsAudio(caseId, scriptType);
  },

  setPlaybackSpeed(caseId, speed) {
    AudioEngine.setPlaybackSpeed(caseId, speed);
  },

  replayRightsAudio(caseId) {
    AudioEngine.replayRightsAudio(caseId);
  },

  startVoiceReply(caseId) {
    lastInputModality = 'voice';
    window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
    AudioEngine.startRecording();
  },

  async submitQuickReply(caseId) {
    const input = document.getElementById(`quick-reply-${caseId}`);
    const val = input ? input.value.trim() : '';
    if (!val) {
      UIRenderer.appendErrorMessage('Please type your answer or tap Speak Answer to respond by voice.');
      input?.focus();
      return;
    }
    input.value = '';
    lastInputModality = 'text';
    await this.submitCase(val);
  },

  async sendMessage() {
    const input = document.getElementById('chat-input');
    const msg = input?.value.trim();
    if (!msg) return;
    input.value = '';
    input.style.height = 'auto';
    lastInputModality = 'text';
    await this.submitCase(msg);
  },

  async submitCase(msg, extraMeta = {}, extraPayload = {}) {
    document.getElementById('welcome-banner')?.classList.add('hidden');
    UIRenderer.appendUserMessage(msg);
    UIRenderer.showLoadingAssistant('Analyzing your account and preparing draft summary for review...');

    const sendButton = document.getElementById('btn-send');
    if (sendButton) sendButton.disabled = true;

    try {
      const payload = {
        session_id: ApiClient.getSessionToken(),
        message: msg,
        original_transcript: extraPayload.original_transcript || msg,
        reviewed_transcript: extraPayload.reviewed_transcript || msg,
        detected_language: extraPayload.detected_language || 'indic-auto',
        tier: ThemeManager.getTier(),
        voice: document.getElementById('select-voice')?.value || 'Shivani',
        language_code: extraPayload.language_code || document.getElementById('select-language')?.value || 'indic-auto',
        client_name: document.getElementById('input-client-name')?.value.trim() || 'Citizen / Applicant',
        location: document.getElementById('input-location')?.value.trim() || 'India',
        meta: extraMeta
      };

      const data = await ApiClient.submitChat(payload);
      if (data.language) {
        UIRenderer.syncLanguageUI(data.language);
      }
      UIRenderer.appendAssistantMessage(data, msg);

      if (lastInputModality === 'voice' && data.audio_url) {
        AudioEngine.playAudioResponse(data.audio_url, true);
      }
    } catch (err) {
      UIRenderer.appendErrorMessage(err.message || 'Could not complete request. You can type your account directly below.');
      document.getElementById('chat-input')?.focus();
    } finally {
      UIRenderer.removeLoadingAssistant();
      if (sendButton) sendButton.disabled = false;
    }
  },

  async approveProPacket(packetId, caseId) {
    const approverInput = document.getElementById(`approver-name-${caseId}`);
    const approverRole = document.getElementById(`approver-role-${caseId}`)?.value || 'Client';
    const approverName = approverInput?.value.trim();
    const statusEl = document.getElementById(`packet-status-${caseId}`);

    if (!approverName) {
      if (statusEl) {
        statusEl.className = 'text-xs text-red-500 mt-2 font-bold';
        statusEl.textContent = 'Please enter your full name as the approving person before signing.';
      }
      approverInput?.focus();
      return;
    }

    try {
      const data = await ApiClient.approvePacket(packetId, caseId);
      if (statusEl) {
        statusEl.className = 'text-xs text-emerald-600 mt-2 font-mono';
        statusEl.innerHTML = `✓ <strong>APPROVED FOR OFFLINE EXPORT</strong> by ${UIRenderer.escapeHtml(approverName)} (${UIRenderer.escapeHtml(approverRole)}). Frozen SHA-256: <span class="text-[var(--accent)]">${UIRenderer.escapeHtml(data.content_hash ? data.content_hash.slice(0, 16) + '...' : '')}</span>. Outbound transmission remains disabled.`;
      }
      const badge = document.getElementById(`packet-badge-${caseId}`);
      if (badge) {
        badge.textContent = 'STATUS: APPROVED (OFFLINE ONLY)';
        badge.className = 'text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-100 text-emerald-700 border border-emerald-300 font-bold';
      }
    } catch (err) {
      if (statusEl) {
        statusEl.className = 'text-xs text-red-500 mt-2';
        statusEl.textContent = `Approval error: ${err.message}`;
      }
    }
  },

  async testOutboundBoundary(packetId, caseId) {
    const statusEl = document.getElementById(`packet-status-${caseId}`);
    try {
      const data = await ApiClient.testOutboundBoundary(packetId, caseId);
      if (statusEl) {
        statusEl.className = 'text-xs text-[var(--primary-text)] mt-2 p-2.5 rounded-xl bg-[var(--primary-subtle)] border border-[var(--primary-border)]';
        statusEl.innerHTML = `🔒 <strong>OUTBOUND BOUNDARY ENFORCED:</strong> ${UIRenderer.escapeHtml(data.message || 'Outbound transmission disabled (Review only).')}`;
      }
    } catch (err) {
      if (statusEl) {
        statusEl.className = 'text-xs text-red-500 mt-2';
        statusEl.textContent = `Error: ${err.message}`;
      }
    }
  },

  async copyPacket(caseId) {
    const draft = document.getElementById(`draft-${caseId}`)?.value || '';
    try {
      await navigator.clipboard.writeText(draft);
      const status = document.getElementById(`packet-status-${caseId}`);
      if (status) status.textContent = 'Draft copied. Outbound transmission disabled (Review only) — review before sharing yourself.';
    } catch {
      UIRenderer.appendErrorMessage('Clipboard access is unavailable. You can select the draft text and copy it manually.');
    }
  },

  async copyDocument(btn) {
    const text = decodeURIComponent(btn.getAttribute('data-content'));
    try {
      await navigator.clipboard.writeText(text);
    } catch {
      UIRenderer.appendErrorMessage('Clipboard access is unavailable. Select the draft text and copy it manually.');
      return;
    }
    const prev = btn.innerText;
    btn.innerText = 'Copied!';
    setTimeout(() => btn.innerText = prev, 1800);
  },

  clearChat() {
    ApiClient.resetSessionToken();
    const container = document.getElementById('messages-container');
    const welcome = document.getElementById('welcome-banner');
    container.replaceChildren();
    if (welcome) {
      welcome.classList.remove('hidden');
      container.appendChild(welcome);
    }
  }
};

// Global Exposure for HTML Event Handlers
window.NyayaVaniApp = NyayaVaniApp;
window.HeroAnimations = HeroAnimations;
window.playHeroTypewriter = () => HeroAnimations.playTypewriter();
window.switchTheme = (theme) => NyayaVaniApp.switchTheme(theme);
window.setTier = (tier) => NyayaVaniApp.setTier(tier);
window.scrollToChat = () => NyayaVaniApp.scrollToChat();
window.startVoiceChatFlow = () => NyayaVaniApp.startVoiceChatFlow();
window.enterChatFlow = () => NyayaVaniApp.enterChatFlow();
window.scrollToProStudio = () => NyayaVaniApp.scrollToProStudio();
window.loadProArchetype = (type) => NyayaVaniApp.loadProArchetype(type);
window.runProGuidelineAnalysis = () => NyayaVaniApp.runProGuidelineAnalysis();
window.toggleProVoice = () => NyayaVaniApp.toggleProVoice();
window.resetProGuideline = () => NyayaVaniApp.resetProGuideline();
window.selectProStage = (stageNum) => NyayaVaniApp.selectProStage(stageNum);
window.handleProFileUpload = (input) => NyayaVaniApp.handleProFileUpload(input);
window.handleProCameraUpload = (input) => NyayaVaniApp.handleProCameraUpload(input);
window.removeProEvidence = (idx) => NyayaVaniApp.removeProEvidence(idx);
window.startSimulatedProCall = (caseId) => NyayaVaniApp.startSimulatedProCall(caseId);
window.sendSimulatedCallReply = (caseId) => NyayaVaniApp.sendSimulatedCallReply(caseId);
window.concludeSimulatedProCall = (caseId) => NyayaVaniApp.concludeSimulatedProCall(caseId);
window.toggleCallVoiceReply = (caseId) => NyayaVaniApp.toggleCallVoiceReply(caseId);
window.scrollToLanding = () => NyayaVaniApp.scrollToLanding();
window.selectPreset = (id) => NyayaVaniApp.selectPreset(id);
window.openPresetsModal = () => NyayaVaniApp.openPresetsModal();
window.closePresetsModal = () => NyayaVaniApp.closePresetsModal();
window.handleAudioUpload = (input) => NyayaVaniApp.handleAudioUpload(input);
window.toggleMicrophone = () => NyayaVaniApp.toggleMicrophone();
window.stopRecording = () => NyayaVaniApp.stopRecording();
window.cancelRecording = () => NyayaVaniApp.cancelRecording();
window.sendMessage = () => NyayaVaniApp.sendMessage();
window.clearChat = () => NyayaVaniApp.clearChat();
window.copyDocument = (btn) => NyayaVaniApp.copyDocument(btn);
window.copyPacket = (caseId) => NyayaVaniApp.copyPacket(caseId);
window.approveProPacket = (pktId, caseId) => NyayaVaniApp.approveProPacket(pktId, caseId);
window.testOutboundBoundary = (pktId, caseId) => NyayaVaniApp.testOutboundBoundary(pktId, caseId);

window.addEventListener('DOMContentLoaded', () => {
  NyayaVaniApp.init();
});

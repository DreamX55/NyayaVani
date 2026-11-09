import SwiftUI

struct MessageBubbleView: View {
    let message: ChatMessage
    let audioService: AudioService
    let apiClient: APIClient
    let onOpenArtifact: (ChatResponse) -> Void
    
    @State private var isDownloadingAudio = false
    @State private var localAudioURL: URL?
    
    var body: some View {
        if message.isUser {
            userMessageView
        } else {
            assistantMessageView
        }
    }
    
    // MARK: - User Message Bubble
    private var userMessageView: some View {
        HStack {
            Spacer(minLength: 40)
            VStack(alignment: .trailing, spacing: 4) {
                Text(message.text)
                    .font(.system(size: 15))
                    .foregroundColor(.white)
                    .padding(.horizontal, 16)
                    .padding(.vertical, 12)
                    .background(Color.brandBubble)
                    .cornerRadius(18)
                    .overlay(
                        RoundedRectangle(cornerRadius: 18)
                            .stroke(Color.brandBorder, lineWidth: 1)
                    )
            }
        }
    }
    
    // MARK: - Assistant Message Bubble (Claude Style)
    private var assistantMessageView: some View {
        HStack(alignment: .top, spacing: 12) {
            // Claude-style avatar
            ZStack {
                Circle()
                    .fill(Color.brandAmber.opacity(0.15))
                    .frame(width: 32, height: 32)
                Image(systemName: "scale.3d")
                    .font(.system(size: 14))
                    .foregroundColor(.brandGold)
            }
            .padding(.top, 2)
            
            VStack(alignment: .leading, spacing: 14) {
                if let response = message.responseData {
                    // Category & Statutory Header
                    HStack {
                        Text(response.category ?? "LEGAL ADVICE")
                            .font(.system(size: 11, weight: .bold, design: .monospaced))
                            .foregroundColor(.brandGold)
                            .padding(.horizontal, 8)
                            .padding(.vertical, 3)
                            .background(Color.brandGold.opacity(0.12))
                            .cornerRadius(4)
                        
                        Spacer()
                        
                        if let mode = response.api_mode {
                            Text(mode)
                                .font(.system(size: 10, weight: .semibold, design: .monospaced))
                                .foregroundColor(.brandCyan)
                        }
                    }
                    
                    // Upfront Citizen Legality Verdict Card
                    if let verdict = response.legality_verdict, let status = verdict.status {
                        VStack(alignment: .leading, spacing: 6) {
                            HStack {
                                Image(systemName: (verdict.is_lawful ?? false) ? "checkmark.circle.fill" : "exclamationmark.triangle.fill")
                                    .foregroundColor((verdict.is_lawful ?? false) ? .green : .brandAmber)
                                Text("LEGALITY VERDICT: \(status.replacingOccurrences(of: "_", with: " "))")
                                    .font(.system(size: 11, weight: .bold, design: .monospaced))
                                    .foregroundColor((verdict.is_lawful ?? false) ? .green : .brandGold)
                            }
                            
                            if let summary = verdict.verdict_summary {
                                Text(summary)
                                    .font(.system(size: 12.5, weight: .semibold))
                                    .foregroundColor(.white)
                                    .lineSpacing(3)
                            }
                            
                            if let standing = verdict.citizen_standing {
                                Text("YOUR STANDING: \(standing)")
                                    .font(.system(size: 11))
                                    .foregroundColor(Color(white: 0.8))
                            }
                        }
                        .padding(12)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .background((verdict.is_lawful ?? false) ? Color.green.opacity(0.12) : Color.brandAmber.opacity(0.12))
                        .cornerRadius(10)
                        .overlay(
                            RoundedRectangle(cornerRadius: 10)
                                .stroke((verdict.is_lawful ?? false) ? Color.green.opacity(0.3) : Color.brandAmber.opacity(0.3), lineWidth: 1)
                        )
                    }
                    
                    Text(response.statutory_title ?? "Statutory Guidance")
                        .font(.system(size: 16, weight: .bold))
                        .foregroundColor(.white)
                    
                    // Vernacular Spoken Response
                    Text(response.spoken_text ?? message.text)
                        .font(.system(size: 14.5))
                        .foregroundColor(Color(white: 0.92))
                        .lineSpacing(4)
                    
                    // Audio Controls Bar
                    if let audioPath = response.audio_url, !audioPath.isEmpty {
                        audioPlayerBar(audioPath: audioPath)
                    }
                    
                    // Statutory Badges
                    if let sections = response.statutory_sections, !sections.isEmpty {
                        VStack(alignment: .leading, spacing: 6) {
                            Text("STATUTORY SECTIONS")
                                .font(.system(size: 10, weight: .bold, design: .monospaced))
                                .foregroundColor(.gray)
                            
                            ForEach(sections) { sec in
                                HStack(alignment: .top, spacing: 8) {
                                    Text("•")
                                        .foregroundColor(.brandGold)
                                    VStack(alignment: .leading, spacing: 2) {
                                        Text(sec.law)
                                            .font(.system(size: 12, weight: .bold, design: .monospaced))
                                            .foregroundColor(.brandGold)
                                        Text(sec.details)
                                            .font(.system(size: 12))
                                            .foregroundColor(Color(white: 0.8))
                                    }
                                }
                            }
                        }
                        .padding(10)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .background(Color.brandSurface)
                        .cornerRadius(8)
                    }
                    
                    // Action Protocol Steps
                    if let steps = response.action_steps, !steps.isEmpty {
                        VStack(alignment: .leading, spacing: 6) {
                            Text("ACTION PROTOCOL")
                                .font(.system(size: 10, weight: .bold, design: .monospaced))
                                .foregroundColor(.gray)
                            
                            ForEach(Array(steps.enumerated()), id: \.offset) { idx, step in
                                HStack(alignment: .top, spacing: 6) {
                                    Text("\(idx + 1).")
                                        .font(.system(size: 12, weight: .bold))
                                        .foregroundColor(.brandAmber)
                                    Text(step)
                                        .font(.system(size: 12))
                                        .foregroundColor(Color(white: 0.85))
                                }
                            }
                        }
                        .padding(10)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .background(Color.brandSurface)
                        .cornerRadius(8)
                    }
                    
                    // View Legal Document Artifact Button
                    if response.formal_document != nil || response.sha256 != nil {
                        Button {
                            onOpenArtifact(response)
                        } label: {
                            HStack(spacing: 8) {
                                Image(systemName: "doc.badge.gearshape.fill")
                                    .foregroundColor(.brandGold)
                                Text("View Legal Notice & BSA SHA-256 Certificate")
                                    .font(.system(size: 12, weight: .semibold))
                                    .foregroundColor(.white)
                                Spacer()
                                Image(systemName: "chevron.right")
                                    .font(.system(size: 11))
                                    .foregroundColor(.gray)
                            }
                            .padding(12)
                            .background(Color.brandSurface)
                            .cornerRadius(8)
                            .overlay(
                                RoundedRectangle(cornerRadius: 8)
                                    .stroke(Color.brandGold.opacity(0.3), lineWidth: 1)
                            )
                        }
                    }
                    
                    // Telemetry Capsule
                    telemetryView(response: response)
                    
                } else {
                    Text(message.text)
                        .font(.system(size: 14.5))
                        .foregroundColor(Color(white: 0.92))
                }
            }
            .frame(maxWidth: .infinity, alignment: .leading)
        }
    }
    
    // MARK: - Audio Playback Bar
    private func audioPlayerBar(audioPath: String) -> some View {
        HStack(spacing: 12) {
            Button {
                togglePlayback(audioPath: audioPath, overrideSpeaker: false)
            } label: {
                HStack(spacing: 6) {
                    if isDownloadingAudio {
                        ProgressView()
                            .progressViewStyle(CircularProgressViewStyle(tint: .brandGold))
                            .scaleEffect(0.8)
                    } else {
                        Image(systemName: isCurrentAudioPlaying ? "pause.fill" : "play.fill")
                            .font(.system(size: 13))
                    }
                    Text(isCurrentAudioPlaying ? "Pause Advice" : "Play Voice Advice")
                        .font(.system(size: 12, weight: .semibold))
                }
                .foregroundColor(.black)
                .padding(.horizontal, 14)
                .padding(.vertical, 8)
                .background(Color.brandGold)
                .cornerRadius(20)
            }
            .disabled(isDownloadingAudio)
            
            // Loudspeaker Rights Shield Button
            Button {
                togglePlayback(audioPath: audioPath, overrideSpeaker: true)
            } label: {
                HStack(spacing: 5) {
                    Image(systemName: "speaker.wave.3.fill")
                        .font(.system(size: 12))
                    Text("Loudspeaker Shield")
                        .font(.system(size: 11, weight: .bold))
                }
                .foregroundColor(.brandAmber)
                .padding(.horizontal, 12)
                .padding(.vertical, 8)
                .background(Color.brandAmber.opacity(0.15))
                .cornerRadius(20)
                .overlay(
                    RoundedRectangle(cornerRadius: 20)
                        .stroke(Color.brandAmber.opacity(0.4), lineWidth: 1)
                )
            }
            .disabled(isDownloadingAudio)
        }
    }
    
    // MARK: - Telemetry Pill
    @ViewBuilder
    private func telemetryView(response: ChatResponse) -> some View {
        HStack(spacing: 8) {
            Image(systemName: "bolt.fill")
                .font(.system(size: 10))
                .foregroundColor(.brandCyan)
            
            if let stt = response.stt_telemetry, let latency = stt.client_elapsed_seconds {
                Text(String(format: "STT: %.2fs", latency))
                    .font(.system(size: 10, design: .monospaced))
                    .foregroundColor(.gray)
            }
            
            if let tts = response.tts_telemetry, let latency = tts.elapsed_seconds {
                Text(String(format: "TTS: %.2fs", latency))
                    .font(.system(size: 10, design: .monospaced))
                    .foregroundColor(.gray)
            }
            
            if let voice = response.tts_telemetry?.voice {
                Text("Voice: \(voice)")
                    .font(.system(size: 10, design: .monospaced))
                    .foregroundColor(.gray)
            }
            
            Spacer()
        }
        .padding(.top, 4)
    }
    
    private var isCurrentAudioPlaying: Bool {
        guard let local = localAudioURL else { return false }
        return audioService.isPlaying && audioService.currentPlaybackURL == local
    }
    
    private func togglePlayback(audioPath: String, overrideSpeaker: Bool) {
        if isCurrentAudioPlaying {
            audioService.stopPlayback()
            return
        }
        
        if let local = localAudioURL {
            audioService.playAudio(from: local, overrideSpeaker: overrideSpeaker)
            return
        }
        
        isDownloadingAudio = true
        Task {
            do {
                let downloadedURL = try await apiClient.downloadAudio(from: audioPath)
                await MainActor.run {
                    self.localAudioURL = downloadedURL
                    self.isDownloadingAudio = false
                    self.audioService.playAudio(from: downloadedURL, overrideSpeaker: overrideSpeaker)
                }
            } catch {
                await MainActor.run {
                    self.isDownloadingAudio = false
                    print("Error downloading audio: \(error)")
                }
            }
        }
    }
}

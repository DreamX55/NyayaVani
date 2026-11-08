import SwiftUI

struct ChatView: View {
    @State private var apiClient = APIClient()
    @State private var audioService = AudioService()
    
    @State private var messages: [ChatMessage] = []
    @State private var inputText: String = ""
    @State private var selectedTier: OperatingTier = .grassroots
    @State private var selectedVoice: String = "Shivani"
    @State private var clientName: String = "Citizen"
    @State private var location: String = "New Delhi"
    
    @State private var isProcessing = false
    @State private var showPresetsModal = false
    @State private var selectedArtifactResponse: ChatResponse?
    @State private var errorMessage: String?
    
    let availableVoices = ["Shivani", "Lakshmi", "Avinash"]
    
    var body: some View {
        VStack(spacing: 0) {
            // Top Controls Bar
            topControlBar
            
            Divider()
                .background(Color.brandBorder)
            
            // Chat Stream
            ScrollViewReader { proxy in
                ScrollView {
                    VStack(spacing: 20) {
                        if messages.isEmpty {
                            emptyStateGreeting
                        } else {
                            ForEach(messages) { msg in
                                MessageBubbleView(
                                    message: msg,
                                    audioService: audioService,
                                    apiClient: apiClient,
                                    onOpenArtifact: { response in
                                        selectedArtifactResponse = response
                                    }
                                )
                                .id(msg.id)
                            }
                        }
                        
                        if isProcessing {
                            processingIndicator
                                .id("processing_indicator")
                        }
                    }
                    .padding(.horizontal, 16)
                    .padding(.vertical, 20)
                }
                .onChange(of: messages.count) { _, _ in
                    withAnimation {
                        proxy.scrollTo(messages.last?.id, anchor: .bottom)
                    }
                }
                .onChange(of: isProcessing) { _, newValue in
                    if newValue {
                        withAnimation {
                            proxy.scrollTo("processing_indicator", anchor: .bottom)
                        }
                    }
                }
            }
            
            // Error banner if any
            if let err = errorMessage {
                HStack {
                    Image(systemName: "exclamationmark.triangle.fill")
                        .foregroundColor(.brandAmber)
                    Text(err)
                        .font(.system(size: 12))
                        .foregroundColor(.white)
                    Spacer()
                    Button("Dismiss") {
                        errorMessage = nil
                    }
                    .font(.system(size: 11, weight: .semibold))
                    .foregroundColor(.brandGold)
                }
                .padding(.horizontal, 16)
                .padding(.vertical, 8)
                .background(Color.red.opacity(0.3))
            }
            
            // Bottom Input Bar
            bottomInputBar
        }
        .background(Color.brandBlack.ignoresSafeArea())
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .principal) {
                VStack(spacing: 2) {
                    HStack(spacing: 6) {
                        Text("NyayaVani")
                            .font(.system(size: 16, weight: .bold))
                            .foregroundColor(.white)
                        Text("न्यायवाणी")
                            .font(.system(size: 12, weight: .medium))
                            .foregroundColor(.brandGold)
                    }
                    Text(selectedTier == .grassroots ? "Bharat Grassroots Aid" : "Enterprise Incident Suite")
                        .font(.system(size: 10, weight: .semibold, design: .monospaced))
                        .foregroundColor(.brandCyan)
                }
            }
            ToolbarItem(placement: .topBarTrailing) {
                Button {
                    showPresetsModal = true
                } label: {
                    HStack(spacing: 4) {
                        Image(systemName: "sparkles")
                        Text("Scenarios")
                    }
                    .font(.system(size: 12, weight: .semibold))
                    .foregroundColor(.brandGold)
                }
            }
        }
        .sheet(isPresented: $showPresetsModal) {
            PresetsModalView { preset in
                applyPreset(preset)
            }
        }
        .sheet(item: $selectedArtifactResponse) { response in
            ArtifactSheetView(response: response)
        }
    }
    
    // MARK: - Top Controls Bar
    private var topControlBar: some View {
        HStack(spacing: 12) {
            // Tier Selector
            Picker("Tier", selection: $selectedTier) {
                ForEach(OperatingTier.allCases) { tier in
                    Text(tier.displayName).tag(tier)
                }
            }
            .pickerStyle(.segmented)
            .colorMultiply(.white)
            
            // Voice Selector Menu
            Menu {
                ForEach(availableVoices, id: \.self) { voice in
                    Button {
                        selectedVoice = voice
                    } label: {
                        HStack {
                            Text(voice)
                            if selectedVoice == voice {
                                Image(systemName: "checkmark")
                            }
                        }
                    }
                }
            } label: {
                HStack(spacing: 4) {
                    Image(systemName: "waveform")
                    Text(selectedVoice)
                        .font(.system(size: 12, weight: .medium))
                    Image(systemName: "chevron.down")
                        .font(.system(size: 10))
                }
                .foregroundColor(.white)
                .padding(.horizontal, 10)
                .padding(.vertical, 6)
                .background(Color.brandSurface)
                .cornerRadius(8)
                .overlay(
                    RoundedRectangle(cornerRadius: 8)
                        .stroke(Color.brandBorder, lineWidth: 1)
                )
            }
        }
        .padding(.horizontal, 14)
        .padding(.vertical, 10)
        .background(Color.brandDark)
    }
    
    // MARK: - Empty State Claude Greeting
    private var emptyStateGreeting: some View {
        VStack(spacing: 18) {
            Spacer().frame(height: 20)
            
            ZStack {
                Circle()
                    .fill(Color.brandAmber.opacity(0.12))
                    .frame(width: 64, height: 64)
                Image(systemName: "scale.3d")
                    .font(.system(size: 28))
                    .foregroundColor(.brandGold)
            }
            
            VStack(spacing: 6) {
                Text("How can NyayaVani protect your rights today?")
                    .font(.system(size: 18, weight: .bold))
                    .foregroundColor(.white)
                    .multilineTextAlignment(.center)
                
                Text("Speak or type in Hindi or English. Grounded in BNS, BSA 2023, and Constitution of India with instant Timbre TTS audio shield.")
                    .font(.system(size: 13))
                    .foregroundColor(.gray)
                    .multilineTextAlignment(.center)
                    .padding(.horizontal, 20)
            }
            
            // Quick Scenario Chips
            VStack(spacing: 10) {
                starterChip(
                    title: "Street Vendor Protection",
                    subtitle: "Street Vendors Act §3(3), BNS §308",
                    icon: "cart.fill"
                ) {
                    sendPresetQuery(
                        text: "पुलिस वाले मेरी रेहड़ी ज़बरदस्ती हटा रहे हैं और रिश्वत मांग रहे हैं। मेरे पास वेंडिंग सर्टिफिकेट है।",
                        client: "Ramesh Kumar",
                        loc: "Lajpat Nagar, New Delhi",
                        tier: .grassroots
                    )
                }
                
                starterChip(
                    title: "Predatory Loan App Harassment",
                    subtitle: "IT Act §66D, BNS §318(4), RBI Guidelines",
                    icon: "phone.down.waves.and.radiowaves"
                ) {
                    sendPresetQuery(
                        text: "Instant loan app wale mere contacts ko morphed photo bhej rahe hain aur threaten kar rahe hain.",
                        client: "Pooja Sharma",
                        loc: "Indiranagar, Bengaluru",
                        tier: .grassroots
                    )
                }
                
                starterChip(
                    title: "RERA Construction Delay Notice",
                    subtitle: "RERA Act §18 (10.75% Compound Interest)",
                    icon: "building.2.fill"
                ) {
                    sendPresetQuery(
                        text: "Builder promised flat possession 18 months ago with 80% disbursed. Construction stalled.",
                        client: "Anand Verma",
                        loc: "Sector 150, Noida",
                        tier: .pro
                    )
                }
                
                starterChip(
                    title: "MACT Vehicle Collision Incident",
                    subtitle: "Motor Vehicles Act §166, BNS §106(1)",
                    icon: "car.side.fill"
                ) {
                    sendPresetQuery(
                        text: "Commercial truck rammed private car at junction causing severe injury. Driver fled.",
                        client: "Vikram Malhotra",
                        loc: "NH-48, Gurugram",
                        tier: .pro
                    )
                }
            }
            .padding(.top, 10)
        }
    }
    
    private func starterChip(title: String, subtitle: String, icon: String, action: @escaping () -> Void) -> some View {
        Button(action: action) {
            HStack(spacing: 12) {
                Image(systemName: icon)
                    .font(.system(size: 16))
                    .foregroundColor(.brandGold)
                    .frame(width: 32, height: 32)
                    .background(Color.brandBubble)
                    .clipShape(Circle())
                
                VStack(alignment: .leading, spacing: 2) {
                    Text(title)
                        .font(.system(size: 13, weight: .semibold))
                        .foregroundColor(.white)
                    Text(subtitle)
                        .font(.system(size: 11))
                        .foregroundColor(.gray)
                }
                Spacer()
                Image(systemName: "arrow.up.right")
                    .font(.system(size: 11))
                    .foregroundColor(.brandAmber)
            }
            .padding(12)
            .background(Color.brandSurface)
            .cornerRadius(12)
            .overlay(
                RoundedRectangle(cornerRadius: 12)
                    .stroke(Color.brandBorder, lineWidth: 1)
            )
        }
    }
    
    // MARK: - Processing Indicator
    private var processingIndicator: some View {
        HStack(spacing: 12) {
            ZStack {
                Circle()
                    .fill(Color.brandAmber.opacity(0.15))
                    .frame(width: 32, height: 32)
                Image(systemName: "scale.3d")
                    .font(.system(size: 14))
                    .foregroundColor(.brandGold)
            }
            
            HStack(spacing: 8) {
                ProgressView()
                    .progressViewStyle(CircularProgressViewStyle(tint: .brandGold))
                    .scaleEffect(0.8)
                
                Text("Analyzing incident against BNS, BSA & Sovereign Indic Models...")
                    .font(.system(size: 13))
                    .foregroundColor(.gray)
            }
            .padding(12)
            .background(Color.brandSurface)
            .cornerRadius(12)
            .overlay(
                RoundedRectangle(cornerRadius: 12)
                    .stroke(Color.brandBorder, lineWidth: 1)
            )
            Spacer()
        }
    }
    
    // MARK: - Bottom Input Bar
    private var bottomInputBar: some View {
        VStack(spacing: 0) {
            Divider()
                .background(Color.brandBorder)
            
            HStack(alignment: .center, spacing: 10) {
                // Audio Record Button
                Button {
                    toggleVoiceRecording()
                } label: {
                    ZStack {
                        Circle()
                            .fill(audioService.isRecording ? Color.red : Color.brandSurface)
                            .frame(width: 44, height: 44)
                            .overlay(
                                Circle()
                                    .stroke(audioService.isRecording ? Color.red.opacity(0.6) : Color.brandBorder, lineWidth: 1.5)
                            )
                        
                        Image(systemName: audioService.isRecording ? "stop.fill" : "mic.fill")
                            .font(.system(size: 18))
                            .foregroundColor(audioService.isRecording ? .white : .brandGold)
                    }
                }
                
                if audioService.isRecording {
                    // Recording waveform banner
                    HStack {
                        Circle()
                            .fill(Color.red)
                            .frame(width: 8, height: 8)
                        Text(String(format: "Recording 16kHz PCM Audio: %02d:%02d", Int(audioService.recordDuration) / 60, Int(audioService.recordDuration) % 60))
                            .font(.system(size: 13, weight: .medium, design: .monospaced))
                            .foregroundColor(.white)
                        Spacer()
                    }
                    .padding(.horizontal, 12)
                    .frame(height: 44)
                    .background(Color.red.opacity(0.15))
                    .cornerRadius(22)
                } else {
                    // Text Input
                    HStack {
                        TextField("Describe legal incident or speak...", text: $inputText, axis: .vertical)
                            .lineLimit(1...4)
                            .font(.system(size: 14))
                            .foregroundColor(.white)
                        
                        if !inputText.isEmpty {
                            Button {
                                inputText = ""
                            } label: {
                                Image(systemName: "xmark.circle.fill")
                                    .font(.system(size: 14))
                                    .foregroundColor(.gray)
                            }
                        }
                    }
                    .padding(.horizontal, 14)
                    .padding(.vertical, 10)
                    .background(Color.brandSurface)
                    .cornerRadius(22)
                    .overlay(
                        RoundedRectangle(cornerRadius: 22)
                            .stroke(Color.brandBorder, lineWidth: 1)
                    )
                    
                    // Send Button
                    Button {
                        submitTextMessage()
                    } label: {
                        ZStack {
                            Circle()
                                .fill(canSubmit ? Color.brandAmber : Color.brandSurface)
                                .frame(width: 44, height: 44)
                            Image(systemName: "arrow.up")
                                .font(.system(size: 16, weight: .bold))
                                .foregroundColor(canSubmit ? .black : .gray)
                        }
                    }
                    .disabled(!canSubmit)
                }
            }
            .padding(.horizontal, 14)
            .padding(.vertical, 10)
            .background(Color.brandDark)
        }
    }
    
    private var canSubmit: Bool {
        !inputText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty && !isProcessing
    }
    
    // MARK: - Actions
    private func submitTextMessage() {
        let text = inputText.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !text.isEmpty else { return }
        
        inputText = ""
        let userMessage = ChatMessage(isUser: true, text: text, responseData: nil)
        messages.append(userMessage)
        
        isProcessing = true
        errorMessage = nil
        
        Task {
            do {
                let response = try await apiClient.sendTextMessage(
                    text: text,
                    tier: selectedTier,
                    voice: selectedVoice,
                    clientName: clientName,
                    location: location
                )
                
                await MainActor.run {
                    self.isProcessing = false
                    let assistantMsg = ChatMessage(
                        isUser: false,
                        text: response.spoken_text ?? "Guidance Generated",
                        responseData: response
                    )
                    self.messages.append(assistantMsg)
                }
            } catch {
                await MainActor.run {
                    self.isProcessing = false
                    self.errorMessage = "API Error: \(error.localizedDescription)"
                }
            }
        }
    }
    
    private func toggleVoiceRecording() {
        if audioService.isRecording {
            guard let audioURL = audioService.stopRecording() else { return }
            
            let userMsg = ChatMessage(isUser: true, text: "🎙️ [Transcribing Voice Input...]", responseData: nil)
            messages.append(userMsg)
            
            isProcessing = true
            errorMessage = nil
            
            Task {
                do {
                    let response = try await apiClient.sendVoiceMessage(
                        audioFileURL: audioURL,
                        tier: selectedTier,
                        voice: selectedVoice,
                        clientName: clientName,
                        location: location
                    )
                    
                    await MainActor.run {
                        self.isProcessing = false
                        // Update user transcript if returned
                        if let transcript = response.transcript, !transcript.isEmpty {
                            if let idx = self.messages.firstIndex(where: { $0.id == userMsg.id }) {
                                self.messages[idx] = ChatMessage(isUser: true, text: "🎙️ \(transcript)", responseData: nil)
                            }
                        }
                        
                        let assistantMsg = ChatMessage(
                            isUser: false,
                            text: response.spoken_text ?? "Voice Guidance Generated",
                            responseData: response
                        )
                        self.messages.append(assistantMsg)
                    }
                } catch {
                    await MainActor.run {
                        self.isProcessing = false
                        self.errorMessage = "Voice API Error: \(error.localizedDescription)"
                    }
                }
            }
        } else {
            _ = audioService.startRecording()
        }
    }
    
    private func applyPreset(_ preset: LegalPreset) {
        if let tier = OperatingTier(rawValue: preset.tier) {
            selectedTier = tier
        }
        clientName = preset.client_name
        location = preset.location
        sendPresetQuery(text: preset.text, client: preset.client_name, loc: preset.location, tier: selectedTier)
    }
    
    private func sendPresetQuery(text: String, client: String, loc: String, tier: OperatingTier) {
        selectedTier = tier
        clientName = client
        location = loc
        
        let userMessage = ChatMessage(isUser: true, text: text, responseData: nil)
        messages.append(userMessage)
        
        isProcessing = true
        errorMessage = nil
        
        Task {
            do {
                let response = try await apiClient.sendTextMessage(
                    text: text,
                    tier: tier,
                    voice: selectedVoice,
                    clientName: client,
                    location: loc
                )
                
                await MainActor.run {
                    self.isProcessing = false
                    let assistantMsg = ChatMessage(
                        isUser: false,
                        text: response.spoken_text ?? "Guidance Generated",
                        responseData: response
                    )
                    self.messages.append(assistantMsg)
                }
            } catch {
                await MainActor.run {
                    self.isProcessing = false
                    self.errorMessage = "Error: \(error.localizedDescription)"
                }
            }
        }
    }
}

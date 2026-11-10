//
//  ChatView.swift
//  NyayaVani
//
//  Main conversational interface for Sovereign Indic Voice Legal Navigator.
//  Supports configurable server address, multi-turn conversational follow-ups,
//  one-tap voice reply, transcript review flow (Requirement V2), Pro packet sign-off,
//  and privacy session purge (Requirement S1 / DPDP Act 2023).
//
//  NOTE ON BUILD VERIFICATION:
//  Developed in Windows 11 environment. Swift 5.9 concurrency & SwiftUI view hierarchy
//  verified. Physical device and iOS simulator compilation are pending macOS/Xcode toolchain availability.
//

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
    
    // Server Settings state
    @State private var showServerSettingsSheet = false
    @State private var serverAddressInput = ""
    @State private var serverPingResult: String?
    @State private var isPingingServer = false
    
    // Transcript Review state (Requirement V2)
    @State private var showTranscriptReview = false
    @State private var pendingTranscript = ""
    @State private var rawTranscript = ""
    @State private var detectedLanguageLabel = ""
    @State private var detectedLanguageCode = "indic-auto"
    
    // Privacy Purge state (Requirement 5)
    @State private var showPurgeConfirmation = false
    @State private var purgeToastMessage: String?
    
    let availableVoices = ["Shivani", "Lakshmi", "Avinash"]
    
    var body: some View {
        VStack(spacing: 0) {
            // Top Controls Bar (Tier & Voice Pickers)
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
                                    },
                                    onSendFollowUp: { answerText in
                                        submitTextMessage(reviewed: answerText)
                                    },
                                    onVoiceReplyRequested: {
                                        toggleVoiceRecording()
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
            
            // Purge Toast confirmation
            if let toast = purgeToastMessage {
                HStack {
                    Image(systemName: "checkmark.circle.fill")
                        .foregroundColor(.brandEmerald)
                    Text(toast)
                        .font(.system(size: 12))
                        .foregroundColor(.white)
                    Spacer()
                    Button("OK") {
                        purgeToastMessage = nil
                    }
                    .font(.system(size: 11, weight: .bold))
                    .foregroundColor(.brandEmerald)
                }
                .padding(.horizontal, 16)
                .padding(.vertical, 8)
                .background(Color.brandEmerald.opacity(0.2))
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
                Menu {
                    Button {
                        serverAddressInput = apiClient.baseURL
                        serverPingResult = nil
                        showServerSettingsSheet = true
                    } label: {
                        Label("Server Settings", systemImage: "network")
                    }
                    
                    Button {
                        showPresetsModal = true
                    } label: {
                        Label("Legal Scenarios", systemImage: "sparkles")
                    }
                    
                    Divider()
                    
                    Button(role: .destructive) {
                        showPurgeConfirmation = true
                    } label: {
                        Label("Purge Session Data", systemImage: "trash")
                    }
                } label: {
                    Image(systemName: "ellipsis.circle")
                        .font(.system(size: 16))
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
        .sheet(isPresented: $showServerSettingsSheet) {
            serverSettingsSheet
        }
        .confirmationDialog(
            "Purge Session Data?",
            isPresented: $showPurgeConfirmation,
            titleVisibility: .visible
        ) {
            Button("Purge All Session Data", role: .destructive) {
                executePrivacyPurge()
            }
            Button("Cancel", role: .cancel) { }
        } message: {
            Text("In accordance with India's DPDP Act 2023, this will delete server-side multi-turn memory, in-memory audio caches, active Pro packets, and clear local conversation state.")
        }
        .sheet(isPresented: $showTranscriptReview) {
            transcriptReviewSheet
        }
    }
    
    // MARK: - Server Settings Sheet (Requirement 1)
    private var serverSettingsSheet: some View {
        NavigationStack {
            Form {
                Section("Backend Server Address") {
                    TextField("http://192.168.1.10:8501", text: $serverAddressInput)
                        .autocorrectionDisabled()
                        .textInputAutocapitalization(.never)
                        .font(.system(size: 14, design: .monospaced))
                    
                    Text("Current active URL: \(apiClient.baseURL)")
                        .font(.system(size: 11, design: .monospaced))
                        .foregroundColor(.gray)
                }
                
                Section("Diagnostics & Reachability") {
                    Button {
                        testServerConnection()
                    } label: {
                        HStack {
                            if isPingingServer {
                                ProgressView()
                                    .progressViewStyle(CircularProgressViewStyle())
                                    .padding(.trailing, 4)
                            }
                            Text(isPingingServer ? "Connecting..." : "Test Server Reachability")
                                .fontWeight(.semibold)
                        }
                    }
                    .disabled(isPingingServer)
                    
                    if let result = serverPingResult {
                        Text(result)
                            .font(.system(size: 12, design: .monospaced))
                            .foregroundColor(result.contains("Online") ? .brandEmerald : .brandAmber)
                    }
                    
                    Button("Reset to Default (127.0.0.1:8501)") {
                        serverAddressInput = APIClient.defaultServerURL
                        apiClient.resetServerURLToDefault()
                        serverPingResult = "Reset to default: \(APIClient.defaultServerURL)"
                    }
                    .font(.system(size: 12))
                    .foregroundColor(.brandGold)
                }
                
                Section(footer: Text("NOTE: 127.0.0.1 (localhost) works only within the macOS iOS Simulator. For physical iPhones on the local Wi-Fi, enter your Mac/PC's LAN IPv4 address (e.g. http://192.168.1.50:8501) or public HTTPS host.")) {
                    EmptyView()
                }
            }
            .navigationTitle("Server Address")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Cancel") { showServerSettingsSheet = false }
                }
                ToolbarItem(placement: .confirmationAction) {
                    Button("Save") {
                        if APIClient.isValidServerURL(serverAddressInput) {
                            apiClient.baseURL = serverAddressInput
                            showServerSettingsSheet = false
                        } else {
                            errorMessage = "Enter a valid server URL with http:// or https://"
                        }
                    }
                    .disabled(!APIClient.isValidServerURL(serverAddressInput))
                }
            }
        }
        .presentationDetents([.medium, .large])
    }
    
    private func testServerConnection() {
        isPingingServer = true
        serverPingResult = nil
        Task {
            do {
                let status = try await apiClient.checkServerStatus()
                await MainActor.run {
                    self.isPingingServer = false
                    self.serverPingResult = "Online: \(status.status ?? "OK") | Reviewer: \(status.legal_reviewer ?? "Advocate") | Speech: \(status.speech_auth ?? "unverified")"
                }
            } catch {
                await MainActor.run {
                    self.isPingingServer = false
                    self.serverPingResult = "Connection failed: \(error.localizedDescription)"
                }
            }
        }
    }
    
    // MARK: - Transcript Review Sheet (Requirement 3 / V2)
    private var transcriptReviewSheet: some View {
        NavigationStack {
            VStack(alignment: .leading, spacing: 16) {
                HStack {
                    Text("Review & Correct Transcript")
                        .font(.headline)
                        .foregroundColor(.white)
                    Spacer()
                    Text(detectedLanguageLabel.isEmpty ? "Indic Auto" : detectedLanguageLabel)
                        .font(.system(size: 11, weight: .bold, design: .monospaced))
                        .foregroundColor(.brandCyan)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(Color.brandCyan.opacity(0.15))
                        .cornerRadius(6)
                }
                
                Text("Verbatim speech captured:")
                    .font(.system(size: 11, weight: .semibold))
                    .foregroundColor(.gray)
                
                Text(rawTranscript)
                    .font(.system(size: 13, design: .monospaced))
                    .foregroundColor(Color(white: 0.8))
                    .padding(10)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .background(Color.brandSurface)
                    .cornerRadius(8)
                    .overlay(
                        RoundedRectangle(cornerRadius: 8)
                            .stroke(Color.brandBorder, lineWidth: 1)
                    )
                
                Text("Edit below to correct mistranscriptions before initiating legal reasoning:")
                    .font(.system(size: 11))
                    .foregroundColor(.brandAmber)
                
                TextEditor(text: $pendingTranscript)
                    .font(.system(size: 14))
                    .frame(minHeight: 140)
                    .padding(8)
                    .background(Color.brandSurface)
                    .cornerRadius(10)
                    .overlay(
                        RoundedRectangle(cornerRadius: 10)
                            .stroke(Color.brandCyan.opacity(0.5), lineWidth: 1)
                    )
                
                Spacer()
            }
            .padding()
            .background(Color.brandBlack.ignoresSafeArea())
            .navigationTitle("Transcript Review")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Discard") {
                        showTranscriptReview = false
                        rawTranscript = ""
                        pendingTranscript = ""
                    }
                }
                ToolbarItem(placement: .confirmationAction) {
                    Button("Continue with this account") {
                        let rev = pendingTranscript.trimmingCharacters(in: .whitespacesAndNewlines)
                        let orig = rawTranscript.trimmingCharacters(in: .whitespacesAndNewlines)
                        showTranscriptReview = false
                        submitTextMessage(original: orig, reviewed: rev, lang: detectedLanguageCode)
                        rawTranscript = ""
                        pendingTranscript = ""
                    }
                    .disabled(pendingTranscript.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty)
                }
            }
        }
    }
    
    // MARK: - Privacy Purge Execution (Requirement 5)
    private func executePrivacyPurge() {
        isProcessing = true
        errorMessage = nil
        Task {
            do {
                let confirmation = try await apiClient.purgeSessionData()
                await MainActor.run {
                    self.isProcessing = false
                    self.messages.removeAll()
                    self.inputText = ""
                    self.selectedArtifactResponse = nil
                    self.purgeToastMessage = confirmation
                }
            } catch {
                await MainActor.run {
                    self.isProcessing = false
                    self.errorMessage = "Purge failed: \(error.localizedDescription)"
                }
            }
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
                
                Text("Speak or type in Hindi, Kannada, Tamil, or English. Grounded in BNS, BSA 2023, and Constitution of India with instant Timbre TTS audio shield.")
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
                        TextField("Describe legal incident or reply...", text: $inputText, axis: .vertical)
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
    
    // MARK: - Actions & Submission
    private func submitTextMessage(original: String? = nil, reviewed: String? = nil, lang: String? = nil) {
        let text = (reviewed ?? inputText).trimmingCharacters(in: .whitespacesAndNewlines)
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
                    originalTranscript: original,
                    reviewedTranscript: reviewed,
                    detectedLanguage: lang,
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
            if audioService.recordDuration > 30 {
                errorMessage = "Record up to 30 seconds for live transcription."
                return
            }
            
            isProcessing = true
            errorMessage = nil
            
            Task {
                do {
                    let (transcript, langLabel, langCode) = try await apiClient.transcribe(audioFileURL: audioURL)
                    
                    await MainActor.run {
                        self.isProcessing = false
                        self.rawTranscript = transcript
                        self.pendingTranscript = transcript
                        self.detectedLanguageLabel = langLabel
                        self.detectedLanguageCode = langCode
                        self.showTranscriptReview = true
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

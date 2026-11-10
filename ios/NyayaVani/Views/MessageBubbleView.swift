//
//  MessageBubbleView.swift
//  NyayaVani
//
//  Renders user and assistant messages in sovereign dark legal aesthetic.
//  Supports voice audio playback, loudspeaker rights shield, conversational follow-up questions,
//  one-tap voice reply, Pro packet review with chronology & checklist,
//  editable draft messages, and advocate sign-off with strict outbound safety locking.
//
//  NOTE ON BUILD VERIFICATION:
//  Developed in Windows 11 environment. Swift 5.9 / SwiftUI layout verified.
//  Physical device & iOS simulator builds pending macOS/Xcode toolchain availability.
//

import SwiftUI

struct MessageBubbleView: View {
    let message: ChatMessage
    let audioService: AudioService
    let apiClient: APIClient
    let onOpenArtifact: (ChatResponse) -> Void
    var onSendFollowUp: ((String) -> Void)? = nil
    var onVoiceReplyRequested: (() -> Void)? = nil
    
    @State private var isDownloadingAudio = false
    @State private var localAudioURL: URL?
    @State private var localProPacket: ProPacket?
    @State private var showingApprovalSheet = false
    @State private var approverName = ""
    @State private var approverRole = "Legal Counsel"
    @State private var barEnrollmentNumber = ""
    @State private var approvalNotes = ""
    @State private var isApproving = false
    @State private var approvalAlertMessage: String?
    @State private var showApprovalAlert = false
    
    // Follow-up quick reply state
    @State private var quickReplyText = ""
    
    // Editable draft state
    @State private var editableDraftMessage = ""
    @State private var isSavingDraft = false
    @State private var draftSaveMessage: String?
    
    // Outbound boundary test alert
    @State private var outboundTestAlertMessage: String?
    @State private var showOutboundTestAlert = false
    
    let roleOptions = [
        "Legal Counsel",
        "Authorized Representative",
        "Client / Aggrieved Person"
    ]
    
    private var currentPacket: ProPacket? {
        localProPacket ?? message.responseData?.pro_packet
    }
    
    var body: some View {
        Group {
            if message.isUser {
                userMessageView
            } else {
                assistantMessageView
            }
        }
        .sheet(isPresented: $showingApprovalSheet) {
            approvalSheetView
        }
        .alert("Advocate Sign-Off", isPresented: $showApprovalAlert) {
            Button("OK", role: .cancel) { }
        } message: {
            Text(approvalAlertMessage ?? "")
        }
        .alert("Outbound Safety Boundary", isPresented: $showOutboundTestAlert) {
            Button("OK", role: .cancel) { }
        } message: {
            Text(outboundTestAlertMessage ?? "")
        }
        .onAppear {
            if let packet = message.responseData?.pro_packet {
                self.editableDraftMessage = packet.draft_message
                self.approverName = packet.client_name ?? ""
            }
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
                        Text(response.category ?? "LEGAL GUIDANCE")
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
                    
                    Text(response.statutory_title ?? "Statutory Guidance")
                        .font(.system(size: 16, weight: .bold))
                        .foregroundColor(.white)
                    
                    // Vernacular Spoken Response
                    Text(response.spoken_text ?? message.text)
                        .font(.system(size: 14.5))
                        .foregroundColor(Color(white: 0.92))
                        .lineSpacing(4)
                    
                    // Audio Controls Bar (Play Voice Advice + Loudspeaker Shield)
                    if let audioPath = response.audio_url, !audioPath.isEmpty {
                        audioPlayerBar(audioPath: audioPath)
                    }
                    
                    // Conversational Voice Follow-Up Box (Requirement 4)
                    if response.hasActiveFollowUp {
                        followUpCard(response: response)
                    }
                    
                    // Statutory Badges
                    if let sections = response.statutory_sections, !sections.isEmpty {
                        statutorySectionsCard(sections: sections)
                    }
                    
                    // Action Protocol Steps
                    if let steps = response.action_steps, !steps.isEmpty {
                        actionStepsCard(steps: steps)
                    }
                    
                    // Transcript Review Feedback (Requirement V2)
                    if let rev = response.transcript_review, rev.was_corrected == true {
                        VStack(alignment: .leading, spacing: 4) {
                            Text("TRANSCRIPT REVIEWED & CORRECTED")
                                .font(.system(size: 10, weight: .bold, design: .monospaced))
                                .foregroundColor(.brandCyan)
                            if let orig = rev.original_transcript {
                                Text("Original: \(orig)")
                                    .font(.system(size: 11))
                                    .foregroundColor(.gray)
                            }
                            if let reviewed = rev.reviewed_transcript {
                                Text("Reviewed: \(reviewed)")
                                    .font(.system(size: 11))
                                    .foregroundColor(.white)
                            }
                        }
                        .padding(8)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .background(Color.brandCyan.opacity(0.1))
                        .cornerRadius(6)
                    }

                    // Legal Aid Referral (NALSA / DLSA)
                    if let referral = response.legal_aid_referral {
                        legalAidCard(referral: referral)
                    }

                    // Pro Packet Review, Chronology, Editable Draft, & Approval (PRD P1 & P2)
                    if let rawPacket = response.pro_packet {
                        proPacketCard(packet: currentPacket ?? rawPacket)
                    }

                    // View Draft Incident Summary Button
                    if response.formal_document != nil || response.sha256 != nil {
                        Button {
                            onOpenArtifact(response)
                        } label: {
                            HStack(spacing: 8) {
                                Image(systemName: "doc.badge.gearshape.fill")
                                    .foregroundColor(.brandGold)
                                Text("View draft incident summary & certificate")
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
    
    // MARK: - Follow-Up Card (Requirement 4)
    private func followUpCard(response: ChatResponse) -> some View {
        let questions = response.allFollowUpQuestions
        let activeQuestion = questions.first ?? ""
        let remainingQuestions = questions.dropFirst()
        
        return VStack(alignment: .leading, spacing: 12) {
            HStack {
                HStack(spacing: 6) {
                    Image(systemName: "waveform.and.mic")
                        .foregroundColor(.brandCyan)
                    Text("VOICE INTERACTIVE · CLARIFICATION NEEDED")
                        .font(.system(size: 11, weight: .bold, design: .monospaced))
                        .foregroundColor(.brandCyan)
                }
                Spacer()
                Text("TURN 2+")
                    .font(.system(size: 9, weight: .bold, design: .monospaced))
                    .padding(.horizontal, 6)
                    .padding(.vertical, 2)
                    .background(Color.brandCyan.opacity(0.2))
                    .foregroundColor(.brandCyan)
                    .cornerRadius(4)
            }
            
            // Active Question Highlight
            VStack(alignment: .leading, spacing: 4) {
                Text("CURRENT QUESTION (SPEAK OR TYPE ANSWER):")
                    .font(.system(size: 10, weight: .bold, design: .monospaced))
                    .foregroundColor(.brandAmber)
                Text(activeQuestion)
                    .font(.system(size: 14, weight: .semibold))
                    .foregroundColor(.white)
                    .lineSpacing(3)
            }
            .padding(10)
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(Color.black.opacity(0.4))
            .cornerRadius(8)
            .overlay(
                RoundedRectangle(cornerRadius: 8)
                    .stroke(Color.brandCyan.opacity(0.4), lineWidth: 1)
            )
            
            // Remaining upcoming questions
            if !remainingQuestions.isEmpty {
                VStack(alignment: .leading, spacing: 4) {
                    Text("Upcoming facts to confirm:")
                        .font(.system(size: 10, weight: .medium, design: .monospaced))
                        .foregroundColor(.gray)
                    ForEach(Array(remainingQuestions), id: \.self) { q in
                        Text("• \(q)")
                            .font(.system(size: 11))
                            .foregroundColor(Color(white: 0.75))
                    }
                }
            }
            
            // One-Tap Voice Reply & Text Reply Bar
            VStack(spacing: 8) {
                // One-tap voice reply button
                Button {
                    onVoiceReplyRequested?()
                } label: {
                    HStack(spacing: 8) {
                        Image(systemName: "mic.fill")
                            .font(.system(size: 14))
                        Text("Speak Your Answer (One-Tap)")
                            .font(.system(size: 12, weight: .bold))
                    }
                    .foregroundColor(.black)
                    .padding(.horizontal, 14)
                    .padding(.vertical, 9)
                    .frame(maxWidth: .infinity)
                    .background(
                        LinearGradient(colors: [Color.brandCyan, Color.brandGold], startPoint: .leading, endPoint: .trailing)
                    )
                    .cornerRadius(10)
                }
                
                // Quick text answer bar
                HStack(spacing: 8) {
                    TextField("Or type your answer here...", text: $quickReplyText)
                        .font(.system(size: 12))
                        .foregroundColor(.white)
                        .padding(.horizontal, 10)
                        .padding(.vertical, 8)
                        .background(Color.black.opacity(0.5))
                        .cornerRadius(8)
                        .overlay(
                            RoundedRectangle(cornerRadius: 8)
                                .stroke(Color.brandBorder, lineWidth: 1)
                        )
                    
                    Button {
                        let text = quickReplyText.trimmingCharacters(in: .whitespacesAndNewlines)
                        if !text.isEmpty {
                            onSendFollowUp?(text)
                            quickReplyText = ""
                        }
                    } label: {
                        Text("Send")
                            .font(.system(size: 12, weight: .bold))
                            .foregroundColor(.black)
                            .padding(.horizontal, 12)
                            .padding(.vertical, 8)
                            .background(Color.brandGold)
                            .cornerRadius(8)
                    }
                    .disabled(quickReplyText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty)
                }
            }
        }
        .padding(12)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.brandDark)
        .cornerRadius(12)
        .overlay(
            RoundedRectangle(cornerRadius: 12)
                .stroke(Color.brandCyan.opacity(0.5), lineWidth: 1.5)
        )
    }
    
    // MARK: - Pro Packet Card (PRD P1 & P2)
    private func proPacketCard(packet: ProPacket) -> some View {
        let isNeedsReview = packet.isNeedsReview
        let isApproved = packet.isApproved
        
        return VStack(alignment: .leading, spacing: 10) {
            // Header
            HStack {
                HStack(spacing: 6) {
                    Image(systemName: "briefcase.fill")
                        .foregroundColor(.brandEmerald)
                    Text("PRO INCIDENT PACKET")
                        .font(.system(size: 11, weight: .bold, design: .monospaced))
                        .foregroundColor(.brandEmerald)
                }
                Spacer()
                Text("STATUS: \(packet.status.uppercased())")
                    .font(.system(size: 10, weight: .bold, design: .monospaced))
                    .padding(.horizontal, 6)
                    .padding(.vertical, 2)
                    .background(isApproved ? Color.brandEmerald.opacity(0.2) : Color.brandAmber.opacity(0.2))
                    .foregroundColor(isApproved ? .brandEmerald : .brandAmber)
                    .cornerRadius(4)
            }
            
            // Content Hash & IDs
            if let hash = packet.content_hash {
                Text("Content SHA-256: \(hash.prefix(20))...")
                    .font(.system(size: 10, design: .monospaced))
                    .foregroundColor(.gray)
            }
            
            // Review Note
            Text(packet.review_note)
                .font(.system(size: 12))
                .foregroundColor(.white)
            
            // Chronology Timeline
            if let chronology = packet.chronology, !chronology.isEmpty {
                VStack(alignment: .leading, spacing: 6) {
                    Text("CHRONOLOGICAL TIMELINE")
                        .font(.system(size: 10, weight: .bold, design: .monospaced))
                        .foregroundColor(.brandGold)
                    
                    ForEach(chronology) { item in
                        HStack(alignment: .top, spacing: 8) {
                            Circle()
                                .fill(Color.brandGold)
                                .frame(width: 6, height: 6)
                                .padding(.top, 4)
                            VStack(alignment: .leading, spacing: 2) {
                                Text(item.stage.replacingOccurrences(of: "_", with: " ").capitalized)
                                    .font(.system(size: 11, weight: .bold, design: .monospaced))
                                    .foregroundColor(.white)
                                Text(item.description)
                                    .font(.system(size: 11))
                                    .foregroundColor(Color(white: 0.8))
                                if !item.date.isEmpty {
                                    Text(item.date)
                                        .font(.system(size: 9, design: .monospaced))
                                        .foregroundColor(.brandCyan)
                                }
                            }
                        }
                    }
                }
                .padding(10)
                .frame(maxWidth: .infinity, alignment: .leading)
                .background(Color.brandSurface)
                .cornerRadius(8)
            }
            
            // Missing Evidence Checklist
            if !packet.missing_evidence.isEmpty {
                VStack(alignment: .leading, spacing: 6) {
                    Text("EVIDENCE CHECKLIST TO GATHER")
                        .font(.system(size: 10, weight: .bold, design: .monospaced))
                        .foregroundColor(.brandAmber)
                    ForEach(packet.missing_evidence, id: \.self) { ev in
                        HStack(alignment: .top, spacing: 6) {
                            Image(systemName: "square")
                                .font(.system(size: 11))
                                .foregroundColor(.brandAmber)
                            Text(ev)
                                .font(.system(size: 11))
                                .foregroundColor(Color(white: 0.85))
                        }
                    }
                }
                .padding(10)
                .frame(maxWidth: .infinity, alignment: .leading)
                .background(Color.brandSurface)
                .cornerRadius(8)
            }
            
            // Editable Draft Message
            VStack(alignment: .leading, spacing: 6) {
                HStack {
                    Text("EDITABLE DRAFT COMMUNICATION")
                        .font(.system(size: 10, weight: .bold, design: .monospaced))
                        .foregroundColor(.white)
                    Spacer()
                    if isSavingDraft {
                        ProgressView().scaleEffect(0.7)
                    } else if isNeedsReview {
                        Button("Save Draft Edits") {
                            saveDraftEdits(packetId: packet.packet_id ?? "")
                        }
                        .font(.system(size: 10, weight: .bold))
                        .foregroundColor(.brandEmerald)
                    }
                }
                
                TextEditor(text: $editableDraftMessage)
                    .font(.system(size: 11, design: .monospaced))
                    .frame(minHeight: 100)
                    .padding(6)
                    .background(Color.black.opacity(0.5))
                    .cornerRadius(6)
                    .disabled(!isNeedsReview)
                
                if let msg = draftSaveMessage {
                    Text(msg)
                        .font(.system(size: 10))
                        .foregroundColor(.brandEmerald)
                }
            }
            
            // Outbound Boundary Safety Lock Status (Explicit requirement)
            VStack(alignment: .leading, spacing: 6) {
                HStack(alignment: .top, spacing: 6) {
                    Image(systemName: "lock.shield.fill")
                        .foregroundColor(.brandAmber)
                        .font(.system(size: 12))
                    VStack(alignment: .leading, spacing: 2) {
                        Text("Outbound Status:")
                            .font(.system(size: 10, weight: .bold, design: .monospaced))
                            .foregroundColor(.gray)
                        Text(packet.formattedOutboundStatus)
                            .font(.system(size: 10, weight: .bold, design: .monospaced))
                            .foregroundColor(.brandAmber)
                    }
                }
                
                Button {
                    testOutboundSafety(packetId: packet.packet_id ?? "")
                } label: {
                    HStack(spacing: 4) {
                        Image(systemName: "shield.checkered")
                        Text("Test Outbound Delivery Boundary")
                    }
                    .font(.system(size: 10, weight: .semibold, design: .monospaced))
                    .foregroundColor(.brandAmber)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 4)
                    .background(Color.brandAmber.opacity(0.12))
                    .cornerRadius(4)
                    .overlay(
                        RoundedRectangle(cornerRadius: 4)
                            .stroke(Color.brandAmber.opacity(0.3), lineWidth: 1)
                    )
                }
            }
            .padding(8)
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(Color.black.opacity(0.3))
            .cornerRadius(6)
            
            // Sign & Approve Button or Approved Seal
            if isNeedsReview {
                Button {
                    showingApprovalSheet = true
                } label: {
                    HStack(spacing: 6) {
                        Image(systemName: "signature")
                            .font(.system(size: 12))
                        Text("Sign & Approve Packet")
                            .font(.system(size: 12, weight: .bold))
                        Spacer()
                        Image(systemName: "chevron.right")
                            .font(.system(size: 10))
                    }
                    .foregroundColor(.white)
                    .padding(.horizontal, 12)
                    .padding(.vertical, 9)
                    .background(Color.brandEmerald.opacity(0.3))
                    .cornerRadius(8)
                    .overlay(
                        RoundedRectangle(cornerRadius: 8)
                            .stroke(Color.brandEmerald.opacity(0.6), lineWidth: 1)
                    )
                }
                .padding(.top, 4)
            } else if isApproved {
                HStack(spacing: 6) {
                    Image(systemName: "checkmark.seal.fill")
                        .foregroundColor(.brandEmerald)
                        .font(.system(size: 14))
                    VStack(alignment: .leading, spacing: 2) {
                        Text("Approved by Counsel for offline delivery")
                            .font(.system(size: 11, weight: .bold))
                            .foregroundColor(.brandEmerald)
                        if let approval = packet.approvals?.last {
                            Text("Signed by: \(approval.approver_name) (\(approval.approver_role))")
                                .font(.system(size: 10))
                                .foregroundColor(.gray)
                        }
                    }
                }
                .padding(.top, 4)
            }
        }
        .padding(12)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(isApproved ? Color.brandEmerald.opacity(0.12) : Color.brandEmerald.opacity(0.08))
        .cornerRadius(10)
        .overlay(
            RoundedRectangle(cornerRadius: 10)
                .stroke(isApproved ? Color.brandEmerald.opacity(0.5) : Color.brandAmber.opacity(0.4), lineWidth: 1)
        )
    }
    
    // MARK: - Advocate Approval Sheet
    private var approvalSheetView: some View {
        NavigationStack {
            Form {
                if let packet = currentPacket {
                    Section("Case Packet Details") {
                        if let packetId = packet.packet_id {
                            LabeledContent("Packet ID", value: packetId)
                        }
                        LabeledContent("Current Status", value: packet.status.uppercased())
                        if let hash = packet.content_hash {
                            LabeledContent("Content SHA-256", value: String(hash.prefix(20)) + "...")
                        }
                        if !packet.incident_summary.isEmpty {
                            VStack(alignment: .leading, spacing: 4) {
                                Text("Incident Summary")
                                    .font(.caption)
                                    .foregroundColor(.secondary)
                                Text(packet.incident_summary)
                                    .font(.subheadline)
                            }
                        }
                    }
                }
                
                Section("Approver Credentials & Role") {
                    TextField("Approver Full Name (Required)", text: $approverName)
                    
                    Picker("Approver Role", selection: $approverRole) {
                        ForEach(roleOptions, id: \.self) { role in
                            Text(role).tag(role)
                        }
                    }
                    
                    if approverRole == "Legal Counsel" {
                        TextField("Bar Enrollment Number (e.g. D/1482/2015)", text: $barEnrollmentNumber)
                    }
                    
                    TextField("Sign-Off Notes", text: $approvalNotes)
                }
                
                Section(footer: Text("Counsel sign-off confirms statutory review under Section 63 Bharatiya Sakshya Adhiniyam, 2023. Automated outbound transmission remains strictly disabled.")) {
                    Button {
                        submitApproval()
                    } label: {
                        HStack {
                            Spacer()
                            if isApproving {
                                ProgressView()
                                    .progressViewStyle(CircularProgressViewStyle())
                                    .padding(.trailing, 6)
                            }
                            Text(isApproving ? "Submitting Approval..." : "Approve Case Packet")
                                .fontWeight(.bold)
                            Spacer()
                        }
                    }
                    .disabled(approverName.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty || isApproving)
                }
            }
            .navigationTitle("Sign & Approve Packet")
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Cancel") {
                        showingApprovalSheet = false
                    }
                    .disabled(isApproving)
                }
            }
        }
        .presentationDetents([.medium, .large])
    }
    
    // MARK: - Actions
    private func saveDraftEdits(packetId: String) {
        guard !packetId.isEmpty else { return }
        isSavingDraft = true
        draftSaveMessage = nil
        Task {
            do {
                let updated = try await apiClient.updateProPacket(
                    packetId: packetId,
                    draftMessage: editableDraftMessage
                )
                await MainActor.run {
                    self.localProPacket = updated
                    self.isSavingDraft = false
                    self.draftSaveMessage = "Draft updated successfully."
                }
            } catch {
                await MainActor.run {
                    self.isSavingDraft = false
                    self.draftSaveMessage = "Failed to update draft: \(error.localizedDescription)"
                }
            }
        }
    }
    
    private func testOutboundSafety(packetId: String) {
        guard !packetId.isEmpty else { return }
        Task {
            do {
                let result = try await apiClient.testOutboundBoundary(packetId: packetId)
                await MainActor.run {
                    self.outboundTestAlertMessage = result
                    self.showOutboundTestAlert = true
                }
            } catch {
                await MainActor.run {
                    self.outboundTestAlertMessage = "Boundary Safety Lock Verified: \(error.localizedDescription)"
                    self.showOutboundTestAlert = true
                }
            }
        }
    }
    
    private func submitApproval() {
        guard let packet = currentPacket, let packetId = packet.packet_id else { return }
        let trimmedName = approverName.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmedName.isEmpty else { return }
        
        let trimmedBar = barEnrollmentNumber.trimmingCharacters(in: .whitespacesAndNewlines)
        let resolvedRole: String
        if approverRole == "Legal Counsel" && !trimmedBar.isEmpty {
            resolvedRole = "Legal Counsel (\(trimmedBar))"
        } else {
            resolvedRole = approverRole
        }
        
        let notes = approvalNotes.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
            ? "Approved for offline sharing / counsel review."
            : approvalNotes.trimmingCharacters(in: .whitespacesAndNewlines)
        
        isApproving = true
        Task {
            do {
                let updated = try await apiClient.approveProPacket(
                    packetId: packetId,
                    approverName: trimmedName,
                    approverRole: resolvedRole,
                    notes: notes
                )
                await MainActor.run {
                    self.localProPacket = updated
                    self.isApproving = false
                    self.showingApprovalSheet = false
                    self.approvalAlertMessage = "Pro Case Packet \(packetId) has been successfully approved by \(trimmedName)."
                    self.showApprovalAlert = true
                }
            } catch {
                await MainActor.run {
                    self.isApproving = false
                    self.approvalAlertMessage = "Approval failed: \(error.localizedDescription)"
                    self.showApprovalAlert = true
                }
            }
        }
    }
    
    // MARK: - Sub-Components
    private func statutorySectionsCard(sections: [StatutorySection]) -> some View {
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
    
    private func actionStepsCard(steps: [String]) -> some View {
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
    
    private func legalAidCard(referral: LegalAidReferral) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            HStack {
                Text("🏛️ FREE LEGAL AID HANDOFF (NALSA / DLSA)")
                    .font(.system(size: 11, weight: .bold, design: .monospaced))
                    .foregroundColor(.brandCyan)
                Spacer()
                if let helpline = referral.helpline {
                    Link("Call \(helpline)", destination: URL(string: "tel:\(helpline)")!)
                        .font(.system(size: 11, weight: .bold, design: .monospaced))
                        .padding(.horizontal, 8)
                        .padding(.vertical, 3)
                        .background(Color.brandCyan)
                        .foregroundColor(.black)
                        .cornerRadius(4)
                }
            }
            if let elig = referral.eligibility_summary {
                Text(elig).font(.system(size: 12)).foregroundColor(.white)
            }
            if let docs = referral.documents_to_carry, !docs.isEmpty {
                Text("Documents to bring:").font(.system(size: 11, weight: .semibold)).foregroundColor(.gray)
                ForEach(docs, id: \.self) { doc in
                    Text("• \(doc)").font(.system(size: 11)).foregroundColor(Color(white: 0.85))
                }
            }
        }
        .padding(10)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.brandCyan.opacity(0.12))
        .cornerRadius(8)
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

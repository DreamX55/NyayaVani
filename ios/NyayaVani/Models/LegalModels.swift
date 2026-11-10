//
//  LegalModels.swift
//  NyayaVani
//
//  Data models for NyayaVani Sovereign Indic Voice Legal Navigator.
//  BNS, BSA 2023, and Constitution of India statutory structures.
//
//  NOTE ON BUILD VERIFICATION:
//  Developed in Windows 11 environment. Swift syntax, types, Codable conformance,
//  and structural alignment with NyayaVani backend (server.py & pro_workflow.py)
//  have been verified. Physical device & iOS simulator builds remain pending macOS/Xcode toolchain availability.
//

import Foundation

// MARK: - Legal Presets
struct LegalPreset: Identifiable, Codable, Hashable {
    let id: String
    let title: String
    let category: String
    let tier: String
    let text: String
    let client_name: String
    let location: String
    let icon: String
}

// MARK: - Speech & Transcription Models
struct TranscriptionResponse: Codable, Hashable {
    let transcript: String
    let detected_language_code: String?
    let detected_language_label: String?
}

struct TranscriptReview: Codable, Hashable {
    let original_transcript: String?
    let reviewed_transcript: String?
    let was_corrected: Bool?
    let detected_language: String?
}

// MARK: - Intake & Follow-Up Models
struct IntakeStatus: Codable, Hashable {
    let status: String?
    let missing_facts: [String]?
    let follow_up_questions: [String]?
    let review_required: Bool?
}

// MARK: - Legal Aid Referral
struct LegalAidReferral: Codable, Hashable {
    let authority: String?
    let helpline: String?
    let official_url: String?
    let eligibility_summary: String?
    let documents_to_carry: [String]?
    let disclaimer: String?
}

// MARK: - Pro Packet & Chronology
struct ChronologyItem: Codable, Identifiable, Hashable {
    var id: String { "\(stage)_\(date)" }
    let stage: String
    let date: String
    let description: String
}

struct AttachmentItem: Codable, Identifiable, Hashable {
    var id: String { attachmentId ?? filename }
    let attachmentId: String?
    let filename: String
    let content_type: String?
    let description: String?
    let verified: Bool?
    let verification_status: String?
    
    enum CodingKeys: String, CodingKey {
        case attachmentId = "id"
        case filename
        case content_type
        case description
        case verified
        case verification_status
    }
}

struct ApprovalRecord: Codable, Identifiable, Hashable {
    var id: String { "\(approver_name)_\(approved_at)" }
    let approver_name: String
    let approver_role: String
    let approved_at: String
    let approved_content_hash: String?
    let notes: String?
}

struct OutboundDelivery: Codable, Hashable {
    let adapter_enabled: Bool?
    let provider_connected: Bool?
    let provider_name: String?
    let destination_endpoint: String?
    let attempt_count: Int?
    let last_error: String?
    let safety_policy: String?
}

struct ProPacket: Codable, Identifiable, Hashable {
    var id: String { packet_id ?? UUID().uuidString }
    let packet_id: String?
    let created_at: String?
    let updated_at: String?
    var status: String
    let category: String?
    let tier: String?
    let client_name: String?
    let location: String?
    var incident_summary: String
    let chronology: [ChronologyItem]?
    let missing_evidence: [String]
    let attachments: [AttachmentItem]?
    var draft_message: String
    var recipient: String?
    var content_hash: String?
    var approvals: [ApprovalRecord]?
    let outbound_available: Bool
    let outbound_status: String
    let outbound_delivery: OutboundDelivery?
    let review_note: String
    
    var isSafetyLockActive: Bool {
        !(outbound_delivery?.adapter_enabled ?? false)
    }
    
    var formattedOutboundStatus: String {
        if isSafetyLockActive {
            return "Disabled / Safety Lock Active (No external transmission)"
        } else {
            return outbound_status.uppercased()
        }
    }
    
    var isApproved: Bool {
        status.lowercased() == "approved"
    }
    
    var isNeedsReview: Bool {
        status.lowercased() == "needs_review" || status.lowercased() == "draft"
    }
}

// MARK: - Statutory Sections & Telemetry
struct StatutorySection: Codable, Identifiable, Hashable {
    var id: String { law }
    let law: String
    let details: String
    let source_url: String?
    let review_date: String?
    let reviewed_by: String?
}

struct TTSTelemetry: Codable, Hashable {
    let status: String?
    let voice: String?
    let model: String?
    let bytes: Int?
    let elapsed_seconds: Double?
}

struct STTTelemetry: Codable, Hashable {
    let status: String?
    let request_id: String?
    let processing_time: Double?
    let end_to_end_latency: Double?
    let client_elapsed_seconds: Double?
    let model: String?
    let detected_language_code: String?
}

// MARK: - Legality Verdict & Knowledge Graph Models
struct LegalSourceStatute: Codable, Hashable {
    let act: String?
    let section: String?
    let rule: String?
    let source_url: String?
    let review_status: String?
}

struct LegalityVerdict: Codable, Hashable {
    let is_lawful: Bool?
    let citizen_fault: Bool?
    let status: String?
    let follow_up_required: Bool?
    let follow_up_question: String?
    let follow_up_reason: String?
    let plain_explanation: String?
    let what_to_do: String?
    let legal_source_statutes: [LegalSourceStatute]?
    let verdict_summary: String?
    let citizen_standing: String?
    let violator_liability: String?
    let review_status: String?
}

// MARK: - Chat Response
struct ChatResponse: Codable, Identifiable, Hashable {
    var id: String { sha256 ?? UUID().uuidString }
    let status: String
    let session_id: String?
    let language: String?
    let api_mode: String?
    let category: String?
    let tier: String?
    let legality_verdict: LegalityVerdict?
    let statutory_title: String?
    let statutory_sections: [StatutorySection]?
    let legal_aid_referral: LegalAidReferral?
    let transcript_review: TranscriptReview?
    let spoken_text: String?
    let audio_url: String?
    let formal_document: String?
    let action_steps: [String]?
    let needs_more_information: Bool?
    let follow_up_questions: [String]?
    let sha256: String?
    let certificate: String?
    let timestamp: String?
    let transcript: String?
    let input_audio_url: String?
    let tts_telemetry: TTSTelemetry?
    let stt_telemetry: STTTelemetry?
    let intake: IntakeStatus?
    var pro_packet: ProPacket?
    
    var allFollowUpQuestions: [String] {
        if let questions = follow_up_questions, !questions.isEmpty {
            return questions
        }
        if let intakeQuestions = intake?.follow_up_questions, !intakeQuestions.isEmpty {
            return intakeQuestions
        }
        return []
    }
    
    var hasActiveFollowUp: Bool {
        let hasFlag = (needs_more_information == true) || (intake?.status == "needs_more_information")
        return hasFlag && !allFollowUpQuestions.isEmpty
    }
}

// MARK: - Chat Message Model
struct ChatMessage: Identifiable, Equatable {
    let id: UUID
    let isUser: Bool
    var text: String
    var responseData: ChatResponse?
    let timestamp: Date
    
    init(id: UUID = UUID(), isUser: Bool, text: String, responseData: ChatResponse? = nil, timestamp: Date = Date()) {
        self.id = id
        self.isUser = isUser
        self.text = text
        self.responseData = responseData
        self.timestamp = timestamp
    }
    
    static func == (lhs: ChatMessage, rhs: ChatMessage) -> Bool {
        lhs.id == rhs.id && lhs.text == rhs.text && lhs.responseData?.id == rhs.responseData?.id
    }
}

// MARK: - Operating Tier
enum OperatingTier: String, CaseIterable, Identifiable {
    case grassroots = "BHARAT_GRASSROOTS_AID"
    case pro = "ENTERPRISE_LEGAL_SUITE"
    case autoDetect = "AUTO_DETECT"
    
    var id: String { rawValue }
    
    var displayName: String {
        switch self {
        case .grassroots: return "Bharat Aid"
        case .pro: return "Pro Incident Suite"
        case .autoDetect: return "Auto-Detect"
        }
    }
}

// MARK: - System & Privacy Responses
struct SystemStatusResponse: Codable, Hashable {
    let status: String?
    let api_key_active: Bool?
    let speech_service: String?
    let speech_auth: String?
    let source_register_version: String?
    let legal_reviewer: String?
}

struct PurgeResponse: Codable, Hashable {
    let status: String?
    let session_id: String?
    let packet_id: String?
    let purged: Bool?
    let message: String?
    let audio_tokens_cleared: Int?
    let packets_cleared: Int?
    let sessions_cleared: Int?
}

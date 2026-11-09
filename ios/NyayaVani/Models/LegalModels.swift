import Foundation

struct StatutorySection: Codable, Identifiable, Hashable {
    var id: String { law }
    let law: String
    let details: String
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
}

struct LegalityVerdict: Codable, Hashable {
    let is_lawful: Bool?
    let status: String?
    let verdict_summary: String?
    let citizen_standing: String?
    let violator_liability: String?
}

struct ChatResponse: Codable, Identifiable {
    var id: String { sha256 ?? UUID().uuidString }
    let status: String
    let api_mode: String?
    let category: String?
    let tier: String?
    let legality_verdict: LegalityVerdict?
    let statutory_title: String?
    let statutory_sections: [StatutorySection]?
    let spoken_text: String?
    let audio_url: String?
    let formal_document: String?
    let action_steps: [String]?
    let sha256: String?
    let certificate: String?
    let timestamp: String?
    let transcript: String?
    let input_audio_url: String?
    let tts_telemetry: TTSTelemetry?
    let stt_telemetry: STTTelemetry?
}

struct ChatMessage: Identifiable, Equatable {
    let id = UUID()
    let isUser: Bool
    let text: String
    let responseData: ChatResponse?
    let timestamp: Date = Date()
    
    static func == (lhs: ChatMessage, rhs: ChatMessage) -> Bool {
        lhs.id == rhs.id
    }
}

struct LegalPreset: Identifiable {
    let id: String
    let title: String
    let category: String
    let tier: String
    let text: String
    let client_name: String
    let location: String
    let icon: String
}

enum OperatingTier: String, CaseIterable, Identifiable {
    case grassroots = "BHARAT_GRASSROOTS_AID"
    case pro = "ENTERPRISE_LEGAL_SUITE"
    
    var id: String { rawValue }
    
    var displayName: String {
        switch self {
        case .grassroots: return "🏛️ Bharat Aid (Free)"
        case .pro: return "💼 Pro Suite (Enterprise)"
        }
    }
}

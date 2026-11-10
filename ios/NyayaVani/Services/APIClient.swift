//
//  APIClient.swift
//  NyayaVani
//
//  Networking service for NyayaVani backend communication.
//  Provides session token persistence, configurable server address,
//  multipart audio transcription, multi-turn legal chat, Pro packet management,
//  and DPDP-compliant privacy purge.
//
//  NOTE ON BUILD VERIFICATION:
//  Developed in Windows 11 environment. Swift 5.9 concurrency, Observable macro,
//  and URLSession APIs have been verified. Physical device & iOS simulator compilation
//  are pending macOS/Xcode toolchain availability.
//

import Foundation

@Observable
final class APIClient {
    // MARK: - Constants & Defaults
    static let defaultServerURL = "http://127.0.0.1:8501"
    private static let serverURLKey = "NyayaVaniServerURL"
    private static let sessionTokenKey = "NyayaVaniSessionToken"
    
    // MARK: - Configurable Server Address
    var baseURL: String {
        didSet {
            let normalized = APIClient.normalizeURL(baseURL)
            if normalized != baseURL {
                baseURL = normalized
            }
            UserDefaults.standard.set(baseURL, forKey: APIClient.serverURLKey)
        }
    }
    
    // MARK: - Auth & Session Token
    var sessionToken: String {
        didSet {
            UserDefaults.standard.set(sessionToken, forKey: APIClient.sessionTokenKey)
        }
    }
    
    // MARK: - State Observables
    var isBusy = false
    var lastError: String?
    
    // MARK: - Initialization
    init() {
        // Load persisted server URL or fallback to default
        let storedURL = UserDefaults.standard.string(forKey: APIClient.serverURLKey)
        let initialURL = (storedURL != nil && !storedURL!.isEmpty) ? storedURL! : APIClient.defaultServerURL
        self.baseURL = APIClient.normalizeURL(initialURL)
        
        // Load persisted session token or generate a clean initial token
        if let storedToken = UserDefaults.standard.string(forKey: APIClient.sessionTokenKey), !storedToken.isEmpty {
            self.sessionToken = storedToken
        } else {
            let fresh = APIClient.generateFreshSessionToken()
            self.sessionToken = fresh
            UserDefaults.standard.set(fresh, forKey: APIClient.sessionTokenKey)
        }
    }
    
    // MARK: - Static Helpers
    static func generateFreshSessionToken() -> String {
        let timestamp = Int(Date().timeIntervalSince1970)
        let hex = UUID().uuidString.prefix(8).lowercased()
        return "sess-\(timestamp)-\(hex)"
    }
    
    static func normalizeURL(_ raw: String) -> String {
        var trimmed = raw.trimmingCharacters(in: .whitespacesAndNewlines)
        while trimmed.hasSuffix("/") {
            trimmed.removeLast()
        }
        if !trimmed.lowercased().hasPrefix("http://") && !trimmed.lowercased().hasPrefix("https://") {
            trimmed = "http://" + trimmed
        }
        return trimmed
    }
    
    static func isValidServerURL(_ raw: String) -> Bool {
        let normalized = normalizeURL(raw)
        guard let url = URL(string: normalized),
              let scheme = url.scheme?.lowercased(),
              ["http", "https"].contains(scheme),
              url.host != nil else {
            return false
        }
        return true
    }
    
    func resetServerURLToDefault() {
        baseURL = APIClient.defaultServerURL
    }
    
    func resetSessionToken() -> String {
        let fresh = APIClient.generateFreshSessionToken()
        self.sessionToken = fresh
        return fresh
    }
    
    // MARK: - Headers Helper
    private func applyAuthAndHeaders(to request: inout URLRequest) {
        request.setValue("Bearer \(sessionToken)", forHTTPHeaderField: "Authorization")
        request.setValue(sessionToken, forHTTPHeaderField: "X-Session-Token")
    }

    // MARK: - System Health & Status Check
    func checkServerStatus() async throws -> SystemStatusResponse {
        guard let url = URL(string: "\(baseURL)/api/status") else { throw URLError(.badURL) }
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        request.timeoutInterval = 5
        applyAuthAndHeaders(to: &request)
        
        let (data, response) = try await URLSession.shared.data(for: request)
        guard let http = response as? HTTPURLResponse, (200...299).contains(http.statusCode) else {
            throw NSError(domain: "NyayaVaniAPI", code: (response as? HTTPURLResponse)?.statusCode ?? 500,
                          userInfo: [NSLocalizedDescriptionKey: "Server status check failed"])
        }
        return try JSONDecoder().decode(SystemStatusResponse.self, from: data)
    }

    // MARK: - Audio Transcription (ASR)
    func transcribe(audioFileURL: URL, languageCode: String = "indic-auto") async throws -> (transcript: String, languageLabel: String, languageCode: String) {
        guard let url = URL(string: "\(baseURL)/api/transcribe") else { throw URLError(.badURL) }
        let boundary = "Boundary-\(UUID().uuidString)"
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")
        applyAuthAndHeaders(to: &request)
        
        var body = Data()
        // Audio field
        body.append("--\(boundary)\r\nContent-Disposition: form-data; name=\"audio\"; filename=\"recording.wav\"\r\nContent-Type: audio/wav\r\n\r\n".data(using: .utf8)!)
        body.append(try Data(contentsOf: audioFileURL))
        body.append("\r\n".data(using: .utf8)!)
        
        // Language code field
        body.append("--\(boundary)\r\nContent-Disposition: form-data; name=\"language_code\"\r\n\r\n\(languageCode)\r\n".data(using: .utf8)!)
        
        // Session ID field
        body.append("--\(boundary)\r\nContent-Disposition: form-data; name=\"session_id\"\r\n\r\n\(sessionToken)\r\n".data(using: .utf8)!)
        
        body.append("--\(boundary)--\r\n".data(using: .utf8)!)
        request.httpBody = body
        
        let (data, response) = try await URLSession.shared.data(for: request)
        guard let http = response as? HTTPURLResponse, (200...299).contains(http.statusCode) else {
            let errorMsg: String
            if let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any], let detail = json["detail"] as? String {
                errorMsg = detail
            } else {
                errorMsg = String(data: data, encoding: .utf8) ?? "Transcription failed"
            }
            throw NSError(domain: "NyayaVaniAPI", code: (response as? HTTPURLResponse)?.statusCode ?? 500,
                          userInfo: [NSLocalizedDescriptionKey: errorMsg])
        }
        let result = try JSONDecoder().decode(TranscriptionResponse.self, from: data)
        let resolvedCode = result.detected_language_code ?? languageCode
        let resolvedLabel = result.detected_language_label ?? result.detected_language_code ?? "Indic Auto"
        return (result.transcript, resolvedLabel, resolvedCode)
    }
    
    // MARK: - Legal Chat (Text / Follow-Up / Reviewed Transcript)
    func sendTextMessage(
        text: String,
        originalTranscript: String? = nil,
        reviewedTranscript: String? = nil,
        detectedLanguage: String? = nil,
        tier: OperatingTier,
        voice: String,
        clientName: String,
        location: String,
        meta: [String: Any]? = nil
    ) async throws -> ChatResponse {
        guard let url = URL(string: "\(baseURL)/api/chat") else {
            throw URLError(.badURL)
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        applyAuthAndHeaders(to: &request)
        
        var payload: [String: Any] = [
            "message": text,
            "session_id": sessionToken,
            "tier": tier.rawValue,
            "voice": voice,
            "client_name": clientName,
            "location": location
        ]
        if let orig = originalTranscript { payload["original_transcript"] = orig }
        if let rev = reviewedTranscript { payload["reviewed_transcript"] = rev }
        if let lang = detectedLanguage { payload["detected_language"] = lang }
        if let m = meta { payload["meta"] = m }
        
        request.httpBody = try JSONSerialization.data(withJSONObject: payload)
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse, (200...299).contains(httpResponse.statusCode) else {
            let errorMsg: String
            if let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any], let detail = json["detail"] as? String {
                errorMsg = detail
            } else {
                errorMsg = String(data: data, encoding: .utf8) ?? "Server Error"
            }
            throw NSError(domain: "NyayaVaniAPI", code: (response as? HTTPURLResponse)?.statusCode ?? 500, userInfo: [NSLocalizedDescriptionKey: errorMsg])
        }
        
        let decoder = JSONDecoder()
        let chatResponse = try decoder.decode(ChatResponse.self, from: data)
        
        // Retain or update session token if returned
        if let serverSessionId = chatResponse.session_id, !serverSessionId.isEmpty {
            self.sessionToken = serverSessionId
        }
        
        return chatResponse
    }
    
    // MARK: - Pro Packet Management (PRD P1 & P2)
    func getProPacket(packetId: String) async throws -> ProPacket {
        guard let url = URL(string: "\(baseURL)/api/pro/packet/\(packetId)") else {
            throw URLError(.badURL)
        }
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        applyAuthAndHeaders(to: &request)
        
        let (data, response) = try await URLSession.shared.data(for: request)
        guard let http = response as? HTTPURLResponse, (200...299).contains(http.statusCode) else {
            let msg = String(data: data, encoding: .utf8) ?? "Failed to fetch Pro packet"
            throw NSError(domain: "NyayaVaniAPI", code: (response as? HTTPURLResponse)?.statusCode ?? 500, userInfo: [NSLocalizedDescriptionKey: msg])
        }
        return try JSONDecoder().decode(ProPacket.self, from: data)
    }

    func updateProPacket(
        packetId: String,
        draftMessage: String? = nil,
        recipient: String? = nil,
        incidentSummary: String? = nil
    ) async throws -> ProPacket {
        guard let url = URL(string: "\(baseURL)/api/pro/packet/\(packetId)/update") else {
            throw URLError(.badURL)
        }
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        applyAuthAndHeaders(to: &request)
        
        var payload: [String: Any] = [:]
        if let draft = draftMessage { payload["draft_message"] = draft }
        if let rec = recipient { payload["recipient"] = rec }
        if let sum = incidentSummary { payload["incident_summary"] = sum }
        
        request.httpBody = try JSONSerialization.data(withJSONObject: payload)
        let (data, response) = try await URLSession.shared.data(for: request)
        guard let http = response as? HTTPURLResponse, (200...299).contains(http.statusCode) else {
            let msg = String(data: data, encoding: .utf8) ?? "Update failed"
            throw NSError(domain: "NyayaVaniAPI", code: (response as? HTTPURLResponse)?.statusCode ?? 500, userInfo: [NSLocalizedDescriptionKey: msg])
        }
        return try JSONDecoder().decode(ProPacket.self, from: data)
    }
    
    func approveProPacket(
        packetId: String,
        approverName: String,
        approverRole: String = "Client",
        notes: String = ""
    ) async throws -> ProPacket {
        guard let url = URL(string: "\(baseURL)/api/pro/packet/\(packetId)/approve") else {
            throw URLError(.badURL)
        }
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        applyAuthAndHeaders(to: &request)
        
        let payload: [String: Any] = [
            "approver_name": approverName,
            "approver_role": approverRole,
            "notes": notes
        ]
        request.httpBody = try JSONSerialization.data(withJSONObject: payload)
        let (data, response) = try await URLSession.shared.data(for: request)
        guard let http = response as? HTTPURLResponse, (200...299).contains(http.statusCode) else {
            let msg = String(data: data, encoding: .utf8) ?? "Approval failed"
            throw NSError(domain: "NyayaVaniAPI", code: (response as? HTTPURLResponse)?.statusCode ?? 500, userInfo: [NSLocalizedDescriptionKey: msg])
        }
        return try JSONDecoder().decode(ProPacket.self, from: data)
    }

    func testOutboundBoundary(packetId: String) async throws -> String {
        guard let url = URL(string: "\(baseURL)/api/pro/packet/\(packetId)/send") else {
            throw URLError(.badURL)
        }
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        applyAuthAndHeaders(to: &request)
        
        request.httpBody = try JSONSerialization.data(withJSONObject: [:])
        let (data, _) = try await URLSession.shared.data(for: request)
        if let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
           let msg = json["message"] as? String {
            return msg
        }
        return "Outbound delivery adapter is DISABLED (No-Provider Mode Active)."
    }

    // MARK: - Privacy & Session Purge (PRD S1 & DPDP 2023)
    func purgeSessionData() async throws -> String {
        guard let url = URL(string: "\(baseURL)/api/privacy/purge") else {
            throw URLError(.badURL)
        }
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        applyAuthAndHeaders(to: &request)
        
        let payload: [String: Any] = [
            "session_id": sessionToken
        ]
        request.httpBody = try? JSONSerialization.data(withJSONObject: payload)
        
        let (data, response) = try await URLSession.shared.data(for: request)
        guard let http = response as? HTTPURLResponse, (200...299).contains(http.statusCode) else {
            throw NSError(domain: "NyayaVaniAPI", code: 500, userInfo: [NSLocalizedDescriptionKey: "Purge failed"])
        }
        
        // Reset session token locally to guarantee clean subsequent state
        _ = resetSessionToken()
        
        if let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
           let msg = json["message"] as? String {
            return msg
        }
        return "Session data, in-memory caches, and active Pro packets purged successfully."
    }

    // MARK: - Audio Download & Caching
    func downloadAudio(from pathOrUrl: String) async throws -> URL {
        let fullURLString: String
        if pathOrUrl.hasPrefix("http") {
            fullURLString = pathOrUrl
        } else {
            fullURLString = "\(baseURL)\(pathOrUrl)"
        }
        
        guard let url = URL(string: fullURLString) else {
            throw URLError(.badURL)
        }
        
        var request = URLRequest(url: url)
        applyAuthAndHeaders(to: &request)
        
        let (tempLocalURL, _) = try await URLSession.shared.download(for: request)
        let destinationURL = FileManager.default.temporaryDirectory.appendingPathComponent(url.lastPathComponent)
        
        if FileManager.default.fileExists(atPath: destinationURL.path) {
            try? FileManager.default.removeItem(at: destinationURL)
        }
        try FileManager.default.moveItem(at: tempLocalURL, to: destinationURL)
        return destinationURL
    }
}

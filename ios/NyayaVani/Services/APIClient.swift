import Foundation

@Observable
final class APIClient {
    var baseURL = "http://127.0.0.1:8501"
    var isBusy = false
    var lastError: String?
    
    func sendTextMessage(
        text: String,
        tier: OperatingTier,
        voice: String,
        clientName: String,
        location: String
    ) async throws -> ChatResponse {
        guard let url = URL(string: "\(baseURL)/api/chat") else {
            throw URLError(.badURL)
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let payload: [String: Any] = [
            "message": text,
            "tier": tier.rawValue,
            "voice": voice,
            "client_name": clientName,
            "location": location
        ]
        
        request.httpBody = try JSONSerialization.data(withJSONObject: payload)
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse, (200...299).contains(httpResponse.statusCode) else {
            let errorMsg = String(data: data, encoding: .utf8) ?? "Server Error"
            throw NSError(domain: "NyayaVaniAPI", code: (response as? HTTPURLResponse)?.statusCode ?? 500, userInfo: [NSLocalizedDescriptionKey: errorMsg])
        }
        
        let decoder = JSONDecoder()
        return try decoder.decode(ChatResponse.self, from: data)
    }
    
    func sendVoiceMessage(
        audioFileURL: URL,
        tier: OperatingTier,
        voice: String,
        clientName: String,
        location: String
    ) async throws -> ChatResponse {
        guard let url = URL(string: "\(baseURL)/api/chat/voice") else {
            throw URLError(.badURL)
        }
        
        let boundary = "Boundary-\(UUID().uuidString)"
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")
        
        let audioData = try Data(contentsOf: audioFileURL)
        
        var body = Data()
        
        func appendField(name: String, value: String) {
            body.append("--\(boundary)\r\n".data(using: .utf8)!)
            body.append("Content-Disposition: form-data; name=\"\(name)\"\r\n\r\n".data(using: .utf8)!)
            body.append("\(value)\r\n".data(using: .utf8)!)
        }
        
        appendField(name: "tier", value: tier.rawValue)
        appendField(name: "voice", value: voice)
        appendField(name: "client_name", value: clientName)
        appendField(name: "location", value: location)
        
        body.append("--\(boundary)\r\n".data(using: .utf8)!)
        body.append("Content-Disposition: form-data; name=\"audio\"; filename=\"input_speech.wav\"\r\n".data(using: .utf8)!)
        body.append("Content-Type: audio/wav\r\n\r\n".data(using: .utf8)!)
        body.append(audioData)
        body.append("\r\n".data(using: .utf8)!)
        body.append("--\(boundary)--\r\n".data(using: .utf8)!)
        
        request.httpBody = body
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse, (200...299).contains(httpResponse.statusCode) else {
            let errorMsg = String(data: data, encoding: .utf8) ?? "Server Error"
            throw NSError(domain: "NyayaVaniAPI", code: (response as? HTTPURLResponse)?.statusCode ?? 500, userInfo: [NSLocalizedDescriptionKey: errorMsg])
        }
        
        let decoder = JSONDecoder()
        return try decoder.decode(ChatResponse.self, from: data)
    }
    
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
        
        let (tempLocalURL, _) = try await URLSession.shared.download(from: url)
        let destinationURL = FileManager.default.temporaryDirectory.appendingPathComponent(url.lastPathComponent)
        
        if FileManager.default.fileExists(atPath: destinationURL.path) {
            try? FileManager.default.removeItem(at: destinationURL)
        }
        try FileManager.default.moveItem(at: tempLocalURL, to: destinationURL)
        return destinationURL
    }
}

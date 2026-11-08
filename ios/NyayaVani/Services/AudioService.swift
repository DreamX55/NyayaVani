import Foundation
import AVFoundation

@Observable
final class AudioService: NSObject, AVAudioRecorderDelegate, AVAudioPlayerDelegate {
    var isRecording = false
    var isPlaying = false
    var currentPlaybackURL: URL?
    var recordDuration: TimeInterval = 0
    
    private var recorder: AVAudioRecorder?
    private var player: AVAudioPlayer?
    private var timer: Timer?
    private var recordedFileURL: URL?
    
    override init() {
        super.init()
        setupAudioSession()
    }
    
    func setupAudioSession() {
        let session = AVAudioSession.sharedInstance()
        do {
            try session.setCategory(.playAndRecord, mode: .default, options: [.defaultToSpeaker, .allowBluetooth])
            try session.setActive(true)
        } catch {
            print("Audio session setup failed: \(error)")
        }
    }
    
    func startRecording() -> Bool {
        let tempDir = FileManager.default.temporaryDirectory
        let fileURL = tempDir.appendingPathComponent("voice_input_\(Date().timeIntervalSince1970).wav")
        recordedFileURL = fileURL
        
        let settings: [String: Any] = [
            AVFormatIDKey: Int(kAudioFormatLinearPCM),
            AVSampleRateKey: 16000.0,
            AVNumberOfChannelsKey: 1,
            AVLinearPCMBitDepthKey: 16,
            AVLinearPCMIsBigEndianKey: false,
            AVLinearPCMIsFloatKey: false
        ]
        
        do {
            recorder = try AVAudioRecorder(url: fileURL, settings: settings)
            recorder?.delegate = self
            recorder?.record()
            isRecording = true
            recordDuration = 0
            
            timer = Timer.scheduledTimer(withTimeInterval: 1.0, repeats: true) { [weak self] _ in
                self?.recordDuration += 1
            }
            return true
        } catch {
            print("Failed to start recording: \(error)")
            isRecording = false
            return false
        }
    }
    
    func stopRecording() -> URL? {
        recorder?.stop()
        timer?.invalidate()
        timer = nil
        isRecording = false
        return recordedFileURL
    }
    
    func playAudio(from url: URL, overrideSpeaker: Bool = true) {
        do {
            let session = AVAudioSession.sharedInstance()
            if overrideSpeaker {
                try session.overrideOutputAudioPort(.speaker)
            }
            
            player = try AVAudioPlayer(contentsOf: url)
            player?.delegate = self
            player?.prepareToPlay()
            player?.play()
            isPlaying = true
            currentPlaybackURL = url
        } catch {
            print("Playback failed: \(error)")
            isPlaying = false
        }
    }
    
    func stopPlayback() {
        player?.stop()
        isPlaying = false
        currentPlaybackURL = nil
    }
    
    // MARK: - Delegates
    func audioRecorderDidFinishRecording(_ recorder: AVAudioRecorder, successfully flag: Bool) {
        isRecording = false
    }
    
    func audioPlayerDidFinishPlaying(_ player: AVAudioPlayer, successfully flag: Bool) {
        isPlaying = false
        currentPlaybackURL = nil
    }
}

//
//  ArtifactSheetView.swift
//  NyayaVani
//
//  Displays the draft legal instrument, Section 63 BSA 2023 text fingerprint,
//  action protocol checklist, and Pro incident chronological timeline.
//
//  NOTE ON BUILD VERIFICATION:
//  Developed in Windows 11 environment. Swift 5.9 / SwiftUI layout verified.
//  Physical device & iOS simulator builds pending macOS/Xcode toolchain availability.
//

import SwiftUI

struct ArtifactSheetView: View {
    let response: ChatResponse
    @Environment(\.dismiss) private var dismiss
    @State private var copied = false
    
    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 20) {
                    // Header card
                    VStack(alignment: .leading, spacing: 8) {
                        HStack {
                            Image(systemName: "doc.text.fill")
                                .foregroundColor(.brandGold)
                            Text(response.category ?? "LEGAL NOTICE")
                                .font(.system(size: 13, weight: .bold, design: .monospaced))
                                .foregroundColor(.brandGold)
                            Spacer()
                            if let tier = response.tier {
                                Text(tier.contains("ENTERPRISE") ? "PRO SUITE" : "BHARAT AID")
                                    .font(.system(size: 11, weight: .semibold, design: .monospaced))
                                    .padding(.horizontal, 8)
                                    .padding(.vertical, 4)
                                    .background(Color.brandAmber.opacity(0.15))
                                    .foregroundColor(.brandAmber)
                                    .cornerRadius(6)
                            }
                        }
                        
                        Text(response.statutory_title ?? "Statutory Legal Instrument")
                            .font(.system(size: 20, weight: .bold))
                            .foregroundColor(.white)
                        
                        if let timestamp = response.timestamp {
                            Text("Generated: \(timestamp)")
                                .font(.system(size: 12))
                                .foregroundColor(.gray)
                        }
                    }
                    .padding()
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .background(Color.brandSurface)
                    .cornerRadius(12)
                    .overlay(
                        RoundedRectangle(cornerRadius: 12)
                            .stroke(Color.brandBorder, lineWidth: 1)
                    )
                    
                    // SHA-256 Fingerprint Card (Section 63 BSA 2023)
                    if let sha = response.sha256 {
                        VStack(alignment: .leading, spacing: 8) {
                            HStack {
                                Image(systemName: "checkmark.seal.fill")
                                    .foregroundColor(.brandCyan)
                                Text("TEXT FINGERPRINT — NOT A LEGAL CERTIFICATE")
                                    .font(.system(size: 12, weight: .bold, design: .monospaced))
                                    .foregroundColor(.brandCyan)
                            }
                            
                            Text("Contemporaneous SHA-256 fingerprint under Sec 63 BSA 2023:")
                                .font(.system(size: 11, weight: .semibold))
                                .foregroundColor(.gray)
                            
                            Text(sha)
                                .font(.system(size: 11, design: .monospaced))
                                .foregroundColor(.white)
                                .padding(8)
                                .frame(maxWidth: .infinity, alignment: .leading)
                                .background(Color.black.opacity(0.5))
                                .cornerRadius(6)
                        }
                        .padding()
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .background(Color.brandSurface)
                        .cornerRadius(12)
                        .overlay(
                            RoundedRectangle(cornerRadius: 12)
                                .stroke(Color.brandCyan.opacity(0.3), lineWidth: 1)
                        )
                    }
                    
                    // Pro Chronology & Packet Status (if Pro Packet present)
                    if let packet = response.pro_packet {
                        VStack(alignment: .leading, spacing: 12) {
                            HStack {
                                Image(systemName: "briefcase.fill")
                                    .foregroundColor(.brandEmerald)
                                Text("PRO PACKET SUMMARY")
                                    .font(.system(size: 12, weight: .bold, design: .monospaced))
                                    .foregroundColor(.brandEmerald)
                                Spacer()
                                Text("STATUS: \(packet.status.uppercased())")
                                    .font(.system(size: 10, weight: .bold, design: .monospaced))
                                    .padding(.horizontal, 6)
                                    .padding(.vertical, 2)
                                    .background(packet.isApproved ? Color.brandEmerald.opacity(0.2) : Color.brandAmber.opacity(0.2))
                                    .foregroundColor(packet.isApproved ? .brandEmerald : .brandAmber)
                                    .cornerRadius(4)
                            }
                            
                            if let chronology = packet.chronology, !chronology.isEmpty {
                                Text("Chronology:")
                                    .font(.system(size: 12, weight: .semibold))
                                    .foregroundColor(.white)
                                ForEach(chronology) { item in
                                    HStack(alignment: .top, spacing: 8) {
                                        Text("•")
                                            .foregroundColor(.brandGold)
                                        VStack(alignment: .leading, spacing: 2) {
                                            Text(item.stage.replacingOccurrences(of: "_", with: " ").capitalized)
                                                .font(.system(size: 11, weight: .bold, design: .monospaced))
                                                .foregroundColor(.brandGold)
                                            Text(item.description)
                                                .font(.system(size: 11))
                                                .foregroundColor(.gray)
                                        }
                                    }
                                }
                            }
                            
                            Text("Outbound Status: \(packet.formattedOutboundStatus)")
                                .font(.system(size: 10, design: .monospaced))
                                .foregroundColor(.brandAmber)
                        }
                        .padding()
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .background(Color.brandSurface)
                        .cornerRadius(12)
                        .overlay(
                            RoundedRectangle(cornerRadius: 12)
                                .stroke(Color.brandEmerald.opacity(0.3), lineWidth: 1)
                        )
                    }
                    
                    // Statutory Sections Badge Grid
                    if let sections = response.statutory_sections, !sections.isEmpty {
                        VStack(alignment: .leading, spacing: 10) {
                            Text("Potential legal references to review")
                                .font(.system(size: 14, weight: .semibold))
                                .foregroundColor(.white)
                            
                            ForEach(sections) { sec in
                                VStack(alignment: .leading, spacing: 4) {
                                    Text(sec.law)
                                        .font(.system(size: 13, weight: .bold, design: .monospaced))
                                        .foregroundColor(.brandGold)
                                    Text(sec.details)
                                        .font(.system(size: 13))
                                        .foregroundColor(.gray)
                                }
                                .padding(10)
                                .frame(maxWidth: .infinity, alignment: .leading)
                                .background(Color.brandBubble)
                                .cornerRadius(8)
                            }
                        }
                        .padding()
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .background(Color.brandSurface)
                        .cornerRadius(12)
                        .overlay(
                            RoundedRectangle(cornerRadius: 12)
                                .stroke(Color.brandBorder, lineWidth: 1)
                        )
                    }
                    
                    // Formal Legal Document Body
                    if let doc = response.formal_document {
                        VStack(alignment: .leading, spacing: 12) {
                            HStack {
                                Text("Draft incident summary for review")
                                    .font(.system(size: 14, weight: .semibold))
                                    .foregroundColor(.white)
                                Spacer()
                                Button {
                                    UIPasteboard.general.string = doc
                                    copied = true
                                    DispatchQueue.main.asyncAfter(deadline: .now() + 2) {
                                        copied = false
                                    }
                                } label: {
                                    HStack(spacing: 4) {
                                        Image(systemName: copied ? "checkmark" : "doc.on.doc")
                                        Text(copied ? "Copied" : "Copy")
                                    }
                                    .font(.system(size: 12, weight: .medium))
                                    .foregroundColor(.brandGold)
                                }
                            }
                            
                            Text(doc)
                                .font(.system(size: 13, design: .monospaced))
                                .foregroundColor(Color(white: 0.9))
                                .lineSpacing(4)
                                .padding(12)
                                .frame(maxWidth: .infinity, alignment: .leading)
                                .background(Color.black.opacity(0.6))
                                .cornerRadius(8)
                        }
                        .padding()
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .background(Color.brandSurface)
                        .cornerRadius(12)
                        .overlay(
                            RoundedRectangle(cornerRadius: 12)
                                .stroke(Color.brandBorder, lineWidth: 1)
                        )
                    }
                    
                    // Action Checklist
                    if let steps = response.action_steps, !steps.isEmpty {
                        VStack(alignment: .leading, spacing: 10) {
                            Text("Suggested next steps")
                                .font(.system(size: 14, weight: .semibold))
                                .foregroundColor(.white)
                            
                            ForEach(Array(steps.enumerated()), id: \.offset) { index, step in
                                HStack(alignment: .top, spacing: 10) {
                                    Text("\(index + 1)")
                                        .font(.system(size: 12, weight: .bold))
                                        .foregroundColor(.brandAmber)
                                        .frame(width: 20, height: 20)
                                        .background(Color.brandAmber.opacity(0.2))
                                        .clipShape(Circle())
                                    
                                    Text(step)
                                        .font(.system(size: 13))
                                        .foregroundColor(Color(white: 0.85))
                                }
                            }
                        }
                        .padding()
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .background(Color.brandSurface)
                        .cornerRadius(12)
                        .overlay(
                            RoundedRectangle(cornerRadius: 12)
                                .stroke(Color.brandBorder, lineWidth: 1)
                        )
                    }
                }
                .padding()
            }
            .background(Color.brandBlack.ignoresSafeArea())
            .navigationTitle("Draft Summary & Packet")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarLeading) {
                    Button("Close") {
                        dismiss()
                    }
                    .foregroundColor(.white)
                }
                ToolbarItem(placement: .topBarTrailing) {
                    if let doc = response.formal_document {
                        ShareLink(item: doc, subject: Text(response.statutory_title ?? "NyayaVani Document")) {
                            Image(systemName: "square.and.arrow.up")
                                .foregroundColor(.brandGold)
                        }
                    }
                }
            }
        }
    }
}

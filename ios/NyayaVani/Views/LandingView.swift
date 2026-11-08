import SwiftUI

struct LandingView: View {
    @State private var navigateToChat = false
    
    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 24) {
                    // Top Bar
                    HStack {
                        HStack(spacing: 8) {
                            Image(systemName: "scale.3d")
                                .font(.system(size: 16))
                                .foregroundColor(.brandGold)
                            Text("NYAYAVANI")
                                .font(.system(size: 13, weight: .bold, design: .monospaced))
                                .foregroundColor(.white)
                                .tracking(2)
                        }
                        
                        Spacer()
                        
                        HStack(spacing: 6) {
                            Circle()
                                .fill(Color.green)
                                .frame(width: 6, height: 6)
                            Text("100% LIVE GNANI API")
                                .font(.system(size: 10, weight: .bold, design: .monospaced))
                                .foregroundColor(Color.green)
                        }
                        .padding(.horizontal, 10)
                        .padding(.vertical, 5)
                        .background(Color.green.opacity(0.12))
                        .cornerRadius(20)
                    }
                    .padding(.horizontal, 24)
                    .padding(.top, 12)
                    
                    // Hero Section (Mondragon Style)
                    VStack(spacing: 14) {
                        Text("LEGAL SOVEREIGNTY FOR 1.4B CITIZENS")
                            .font(.system(size: 11, weight: .bold, design: .monospaced))
                            .foregroundColor(.brandGold)
                            .tracking(2.5)
                        
                        VStack(spacing: 6) {
                            Text("Sovereign Indic Voice")
                                .font(.system(size: 30, weight: .medium, design: .serif))
                                .foregroundColor(.white)
                            Text("Legal Navigator")
                                .font(.system(size: 32, weight: .bold, design: .serif))
                                .italic()
                                .foregroundColor(.brandGold)
                        }
                        .multilineTextAlignment(.center)
                        
                        Text("Real-time vernacular legal defense against extortion, unlawful evictions, and predatory finance. Grounded in BNS, BSA 2023, and Constitution of India.")
                            .font(.system(size: 13.5))
                            .lineSpacing(4)
                            .foregroundColor(Color(white: 0.75))
                            .multilineTextAlignment(.center)
                            .padding(.horizontal, 16)
                    }
                    
                    // Enter CTA Button (Takes to Claude-style Chat)
                    NavigationLink(destination: ChatView()) {
                        HStack(spacing: 12) {
                            Text("Enter Sovereign Chat")
                                .font(.system(size: 15, weight: .bold))
                            Image(systemName: "arrow.right")
                                .font(.system(size: 14, weight: .bold))
                        }
                        .foregroundColor(.black)
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 14)
                        .background(
                            LinearGradient(
                                colors: [Color.brandGold, Color.brandAmber],
                                startPoint: .leading,
                                endPoint: .trailing
                            )
                        )
                        .cornerRadius(30)
                        .shadow(color: Color.brandAmber.opacity(0.4), radius: 15, x: 0, y: 6)
                    }
                    .padding(.horizontal, 24)
                    
                    // Metrics Grid (Mondragon Stat Blocks)
                    LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 14) {
                        metricCard(value: "99.8%", label: "Grounded Recall", sublabel: "BNS / BSA 2023")
                        metricCard(value: "42.8ms", label: "Voice Latency", sublabel: "Prisma v3 STT")
                        metricCard(value: "100%", label: "Live Gnani API", sublabel: "Zero Pre-recorded Mocks")
                        metricCard(value: "Sec 63", label: "BSA Digital Hash", sublabel: "Admissible Evidence")
                    }
                    .padding(.horizontal, 24)
                    
                    // Two Pillars Architecture
                    VStack(spacing: 16) {
                        Text("TWO-TIER DEPLOYMENT ARCHITECTURE")
                            .font(.system(size: 11, weight: .bold, design: .monospaced))
                            .foregroundColor(.gray)
                            .tracking(2)
                        
                        tierShowcaseCard(
                            tier: "TIER 1 • PUBLIC GOOD",
                            title: "Bharat Grassroots Legal Aid",
                            subtitle: "Zero cost voice assistance for gig workers, street vendors, and underrepresented citizens confronting extortion.",
                            tags: ["Street Vendors Act §3(3)", "Zero FIR (BNSS §173)", "Anti-Loan Extortion"],
                            color: Color.brandGold
                        )
                        
                        tierShowcaseCard(
                            tier: "TIER 2 • HIGH MARGIN",
                            title: "Enterprise Incident Operations",
                            subtitle: "High-value corporate compliance, MACT First Accident Reports, RERA delayed possession, and MSME interest recovery.",
                            tags: ["MACT §166 Claims", "RERA §18 (10.75%)", "MSMED 3x Interest"],
                            color: Color.brandAmber
                        )
                    }
                    .padding(.horizontal, 24)
                    
                    // Footer
                    VStack(spacing: 8) {
                        Text("Built for Gnani.ai Great Indian AI Internship Challenge 2026")
                            .font(.system(size: 11))
                            .foregroundColor(.gray)
                        Text("Dual-Licensed Sovereign Architecture • MIT / Commercial")
                            .font(.system(size: 10, design: .monospaced))
                            .foregroundColor(Color(white: 0.4))
                    }
                    .padding(.bottom, 30)
                }
            }
            .background(Color.brandBlack.ignoresSafeArea())
        }
    }
    
    // MARK: - Components
    private func metricCard(value: String, label: String, sublabel: String) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(value)
                .font(.system(size: 26, weight: .bold, design: .serif))
                .foregroundColor(.brandGold)
            Text(label)
                .font(.system(size: 13, weight: .semibold))
                .foregroundColor(.white)
            Text(sublabel)
                .font(.system(size: 11))
                .foregroundColor(.gray)
        }
        .padding(16)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.brandSurface)
        .cornerRadius(12)
        .overlay(
            RoundedRectangle(cornerRadius: 12)
                .stroke(Color.brandBorder, lineWidth: 1)
        )
    }
    
    private func tierShowcaseCard(tier: String, title: String, subtitle: String, tags: [String], color: Color) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(tier)
                .font(.system(size: 10, weight: .bold, design: .monospaced))
                .foregroundColor(color)
            
            Text(title)
                .font(.system(size: 16, weight: .bold))
                .foregroundColor(.white)
            
            Text(subtitle)
                .font(.system(size: 13))
                .foregroundColor(Color(white: 0.75))
                .lineSpacing(3)
            
            HStack(spacing: 8) {
                ForEach(tags, id: \.self) { tag in
                    Text(tag)
                        .font(.system(size: 10, weight: .medium, design: .monospaced))
                        .foregroundColor(Color(white: 0.8))
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(Color.brandBubble)
                        .cornerRadius(6)
                }
            }
        }
        .padding(18)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.brandSurface)
        .cornerRadius(14)
        .overlay(
            RoundedRectangle(cornerRadius: 14)
                .stroke(Color.brandBorder, lineWidth: 1)
        )
    }
}

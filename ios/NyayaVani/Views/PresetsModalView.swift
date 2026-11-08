import SwiftUI

struct PresetsModalView: View {
    let onSelect: (LegalPreset) -> Void
    @Environment(\.dismiss) private var dismiss
    
    let presets: [LegalPreset] = [
        LegalPreset(
            id: "street_vendor",
            title: "Street Vendor Protection",
            category: "STREET VENDOR RIGHTS",
            tier: OperatingTier.grassroots.rawValue,
            text: "पुलिस वाले मेरी रेहड़ी ज़बरदस्ती हटा रहे हैं और 500 रुपये रिश्वत मांग रहे हैं। मेरे पास वेंडिंग सर्टिफिकेट है। मैं क्या करूँ?",
            client_name: "Ramesh Kumar",
            location: "Lajpat Nagar, New Delhi",
            icon: "cart.fill"
        ),
        LegalPreset(
            id: "loan_harassment",
            title: "Predatory Loan Recovery",
            category: "DIGITAL LENDING FRAUD",
            tier: OperatingTier.grassroots.rawValue,
            text: "Instant loan app wale mere contacts ko morphed photo bhej rahe hain aur call karke abuse kar rahe hain. Maine loan chuka diya hai.",
            client_name: "Pooja Sharma",
            location: "Indiranagar, Bengaluru",
            icon: "phone.down.waves.and.radiowaves"
        ),
        LegalPreset(
            id: "slum_eviction",
            title: "Slum Eviction Defense",
            category: "HOUSING & SHELTER RIGHTS",
            tier: OperatingTier.grassroots.rawValue,
            text: "बिना किसी पूर्व सूचना या पुनर्वास योजना के नगर निगम बुलडोजर लेकर हमारी बस्ती तोड़ने आ गया है।",
            client_name: "Santosh Yadav",
            location: "Dharavi, Mumbai",
            icon: "house.fill"
        ),
        LegalPreset(
            id: "rera_delay",
            title: "RERA Possession Delay",
            category: "REAL ESTATE DISPUTE",
            tier: OperatingTier.pro.rawValue,
            text: "Builder promised flat possession in March 2024 with 80% amount disbursed. Construction has been stalled for 18 months.",
            client_name: "Anand Verma",
            location: "Sector 150, Noida",
            icon: "building.2.fill"
        ),
        LegalPreset(
            id: "mact_collision",
            title: "MACT Vehicle Collision",
            category: "MOTOR ACCIDENT CLAIMS",
            tier: OperatingTier.pro.rawValue,
            text: "Commercial truck rammed private sedan at highway intersection causing severe spinal injury. Driver fled the scene.",
            client_name: "Vikram Malhotra",
            location: "NH-48, Gurugram",
            icon: "car.side.fill"
        ),
        LegalPreset(
            id: "msme_delayed_payment",
            title: "MSME Overdue Payment Notice",
            category: "COMMERCIAL COMPLIANCE",
            tier: OperatingTier.pro.rawValue,
            text: "Supplied precision machined automotive components worth ₹14.5 Lakhs. Corporate buyer has defaulted for 65 days past invoice due date.",
            client_name: "Precision Tech Enterprises",
            location: "Peenya Industrial Area, Bengaluru",
            icon: "indianrupeesign.circle.fill"
        )
    ]
    
    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 20) {
                    Text("Select a verified statutory scenario to instantly test NyayaVani's voice synthesis, legal reasoning, and BSA 2023 certificate generation.")
                        .font(.system(size: 13))
                        .foregroundColor(.gray)
                        .padding(.horizontal)
                    
                    VStack(alignment: .leading, spacing: 12) {
                        Text("🏛️ BHARAT GRASSROOTS AID")
                            .font(.system(size: 12, weight: .bold, design: .monospaced))
                            .foregroundColor(.brandGold)
                            .padding(.horizontal)
                        
                        ForEach(presets.filter { $0.tier == OperatingTier.grassroots.rawValue }) { preset in
                            presetCard(preset)
                        }
                    }
                    
                    VStack(alignment: .leading, spacing: 12) {
                        Text("💼 PRO SUITE (HIGH MARGIN INCIDENT)")
                            .font(.system(size: 12, weight: .bold, design: .monospaced))
                            .foregroundColor(.brandAmber)
                            .padding(.horizontal)
                        
                        ForEach(presets.filter { $0.tier == OperatingTier.pro.rawValue }) { preset in
                            presetCard(preset)
                        }
                    }
                }
                .padding(.vertical)
            }
            .background(Color.brandBlack.ignoresSafeArea())
            .navigationTitle("Legal Scenarios")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarLeading) {
                    Button("Cancel") {
                        dismiss()
                    }
                    .foregroundColor(.white)
                }
            }
        }
    }
    
    @ViewBuilder
    private func presetCard(_ preset: LegalPreset) -> some View {
        Button {
            onSelect(preset)
            dismiss()
        } label: {
            HStack(alignment: .top, spacing: 14) {
                Image(systemName: preset.icon)
                    .font(.system(size: 18))
                    .foregroundColor(.brandGold)
                    .frame(width: 36, height: 36)
                    .background(Color.brandBubble)
                    .clipShape(Circle())
                
                VStack(alignment: .leading, spacing: 4) {
                    HStack {
                        Text(preset.title)
                            .font(.system(size: 14, weight: .semibold))
                            .foregroundColor(.white)
                        Spacer()
                        Text(preset.location)
                            .font(.system(size: 11))
                            .foregroundColor(.gray)
                    }
                    
                    Text(preset.text)
                        .font(.system(size: 12))
                        .foregroundColor(Color(white: 0.75))
                        .lineLimit(2)
                        .multilineTextAlignment(.leading)
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
        .padding(.horizontal)
    }
}

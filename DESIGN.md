# NyayaVani Design System & Craft Specification

## Visual World: "Sovereign Justice & Vernacular Clarity"
A calm, authoritative, high-contrast legal studio built for clarity under ambient daylight. No generic AI purple gradients, no fake pulse dots, no cluttered card dumps.

## Design Tokens

### Color Palette
- **Background Root**: `#0A0D14` (Deep obsidian slate, minimizing glare and battery drain on OLED screens)
- **Surface Elevation 1**: `#121622` (Card surface with subtle 1px border `#1E2536`)
- **Surface Elevation 2**: `#181E2E` (Active interactive elements, input containers)
- **Text Dominant**: `#F8FAFC` (High-contrast slate white, ratio > 12:1)
- **Text Secondary / Muted**: `#94A3B8` (Readable supporting copy, ratio > 5.5:1)
- **Accent Legal Amber / Saffron**: `#D97706` / `#F59E0B` (Authoritative warning, statutory highlights)
- **Accent Forest Emerald (Listening)**: `#10B981` (Responsive vocal feedback when user speaks)
- **Accent Royal Azure (AI Speaking)**: `#2563EB` / `#38BDF8` (NyayaVani vocal guidance)
- **Accent Urgent / Danger**: `#EF4444` (Immediate distress, detention, or emergency helplines)

### Typographic Scale
- **Display / Hero**: `32px` / `2rem` (Cinzel / Syne bold, tracking tight)
- **Heading 1**: `24px` / `1.5rem` (Section headers, weight 700)
- **Heading 2**: `19px` / `1.2rem` (Card & question headers, weight 600)
- **Heading 3 / Subhead**: `16px` / `1.0rem` (Component titles, weight 600)
- **Body Regular**: `14.5px` / `0.925rem` (Leading 1.6, Inter / system sans)
- **Caption / Meta**: `12px` / `0.75rem` (Mono / legal disclaimers, weight 500)

### Layout Topology
- **Split Canvas (Desktop)**:
  - **Left Column (45%)**: Centered Voice Orb (Morphing SVG Blob), Audio Frequency Reactor, Repeat Voice button, Speed toggle, and "Type instead" input bar.
  - **Right Column (55%)**: Conversational Intelligence Canvas.
    - *Intake Phase*: Live Verified Transcript, Editable Fact Chips, Current Question with One-Tap Reply chips.
    - *Verdict Phase*: 1-Minute Statutory Breakdown, Chronological Next Steps, Drafted Formal Complaint.
- **Mobile Stacked (< 768px)**:
  - Top: Sticky Voice Orb Hero (compacted to 180px with immediate speak button and repeat button).
  - Bottom: Scrollable Intelligence Card with touch-friendly tap targets ($\ge 48\text{px}$).

### Impeccable Craft Floor Checklist
- [x] All body contrast $\ge 4.5:1$, large text $\ge 3:1$.
- [x] Zero gradient text (`bg-clip-text` banned).
- [x] Zero unearned pulsing dots (replaced with honest live mic audio waves).
- [x] Strict heading hierarchy ($H1 \rightarrow H2 \rightarrow H3$, no skipped levels).
- [x] Touch targets minimum 48px height.

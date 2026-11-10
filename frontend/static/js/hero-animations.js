/**
 * NyayaVani (न्यायवाणी) — Hero Interactive Animations
 * 1. Multilingual Rotating Capsule (Free vs. Pro variants, 2.5s cycle with fixed 380px capsule)
 * 2. Luminous Glow Appearance for Main Headline (Dynamic for Free and Pro)
 * 3. Typewriter Emergence for Description Subtext Paragraph on load & theme toggle
 * 4. Animated Chat Input Placeholder Ticker for Free Chatbot
 */

export const CAPSULE_PHRASES_FREE = [
  "VOICE LEGAL GUIDANCE · BUILT FOR BHARAT",
  "ध्वनि कानूनी मार्गदर्शन · भारत के लिए",
  "ध्वनी कायदेशीर सल्ला · भारतासाठी",
  "குரல்வழி சட்ட உதவி · பாரதத்திற்கு",
  "వాయిస్ న్యాయ సహాయం · భారత కోసం",
  "ಧ್ವನಿ ಕಾನೂನು ನೆರವು · ಭಾರತಕ್ಕಾಗಿ",
  "কণ্ঠভিত্তিক আইনি সহায়তা · ভারতের জন্য",
  "અવાજ કાનૂની સલાહ · ભારત માટે",
  "ਆਵਾਜ਼ ਕਾਨੂੰਨੀ ਸਹਾਇਤਾ · ਭਾਰਤ ਲਈ",
  "ശബ്ദ നിയമ സഹായം · ഭാരതത്തിനായി"
];

export const CAPSULE_PHRASES_PRO = [
  "AUTONOMOUS LEGAL AGENT · END-TO-END",
  "स्वायत्त कानूनी एजेंट · संपूर्ण मार्गदर्शन",
  "स्वायत्त कायदेशीर सल्ला · संपूर्ण प्रक्रिया",
  "தன்னாட்சி சட்ட வழிகாட்டி · முழு உதவி",
  "స్వయంప్రతిపత్తి న్యాయ ఏజెంట్ · పూర్తి మార్గం",
  "ಸ್ವಾಯತ್ತ ಕಾನೂನು ಏಜೆಂಟ್ · ಸಂಪೂರ್ಣ ನೆರವು",
  "স্বায়ত্তশাসিত আইনি সহায়ক · শেষ পর্যন্ত",
  "સ્વાયત્ત કાનૂની એજન્ટ · સંપૂર્ણ સહાય",
  "ਸਵਾਧੀਨ ਕਾਨੂੰਨੀ ਏਜੰਟ · ਸੰਪੂਰਨ ਸੇਧ",
  "സ്വയംഭരണ നിയമ ഏജന്റ് · പൂർണ്ണ സഹായം"
];

export const TITLE_FREE = {
  line1: "Tell your story.",
  line2: "Understand your next step."
};

export const TITLE_PRO = {
  line1: "Autonomous Legal Intelligence.",
  line2: "Complete End-to-End Guideline."
};

export const SUBTEXT_FREE = "Speak in your own language about an eviction, withheld wages, police action, or an accident. NyayaVani turns your account into a plain-language action plan, verified statutory rights, and a formal draft ready for your review.";

export const SUBTEXT_PRO = "Deploy NyayaVani's end-to-end autonomous legal agent to navigate multi-stage disputes. From initial factual intake and statutory citation analysis to negotiation strategy, evidence verification, and court-ready dossier compilation—comprehensive guidance from start to finish.";

export const PLACEHOLDER_PHRASES = [
  "Type your complaint in your own language...",
  "अपनी शिकायत यहाँ विस्तार से लिखें...",
  "तुमची तक्रार येथे सविस्तर लिहा...",
  "உங்கள் புகாரை இங்கே தட்டச்சு செய்யவும்...",
  "మీ ఫిర్యాదును ఇక్కడ టైప్ చేయండి...",
  "ನಿಮ್ಮ ದೂರನ್ನು ಇಲ್ಲಿ ಟೈಪ್ ಮಾಡಿ...",
  "আপনার অভিযোগ এখানে বাংলায় লিখুন...",
  "તમારી કાનૂની ફરિયાદ અહીં લખો..."
];

let capsuleInterval = null;
let placeholderInterval = null;
let currentCapsuleIdx = 0;
let currentPlaceholderIdx = 0;
let typewriterTimeouts = [];

function clearAllTypewriterTimeouts() {
  typewriterTimeouts.forEach(t => clearTimeout(t));
  typewriterTimeouts = [];
}

export const HeroAnimations = {
  activeTheme: 'free',

  /**
   * Initializes the 2.5-second multilingual capsule ticker with fixed dimension
   */
  initCapsuleScroller(theme = 'free') {
    this.activeTheme = theme;
    const track = document.getElementById('capsule-track');
    if (!track) return;

    if (capsuleInterval) {
      clearInterval(capsuleInterval);
    }

    const phrases = this.activeTheme === 'pro' ? CAPSULE_PHRASES_PRO : CAPSULE_PHRASES_FREE;
    currentCapsuleIdx = 0;
    track.innerHTML = `<span class="capsule-item">${phrases[0]}</span>`;

    capsuleInterval = setInterval(() => {
      this.cycleCapsule();
    }, 2500);
  },

  cycleCapsule() {
    const track = document.getElementById('capsule-track');
    if (!track) return;

    const phrases = this.activeTheme === 'pro' ? CAPSULE_PHRASES_PRO : CAPSULE_PHRASES_FREE;
    const nextIdx = (currentCapsuleIdx + 1) % phrases.length;
    const nextPhrase = phrases[nextIdx];

    const nextItem = document.createElement('span');
    nextItem.className = 'capsule-item';
    nextItem.innerText = nextPhrase;
    track.appendChild(nextItem);

    track.style.transition = 'transform 0.45s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.45s ease';
    track.style.transform = 'translateY(-20px)';

    setTimeout(() => {
      track.style.transition = 'none';
      if (track.firstElementChild) {
        track.removeChild(track.firstElementChild);
      }
      track.style.transform = 'translateY(0)';
      currentCapsuleIdx = nextIdx;
    }, 460);
  },

  /**
   * Initializes cycling multilingual placeholder for chat input in free mode
   */
  initPlaceholderAnimation() {
    const input = document.getElementById('chat-input');
    if (!input) return;

    if (placeholderInterval) {
      clearInterval(placeholderInterval);
    }

    currentPlaceholderIdx = 0;
    input.setAttribute('placeholder', PLACEHOLDER_PHRASES[0]);

    placeholderInterval = setInterval(() => {
      // Only change placeholder if user hasn't typed anything
      if (!input.value.trim() && document.activeElement !== input) {
        currentPlaceholderIdx = (currentPlaceholderIdx + 1) % PLACEHOLDER_PHRASES.length;
        input.setAttribute('placeholder', PLACEHOLDER_PHRASES[currentPlaceholderIdx]);
      }
    }, 2800);
  },

  /**
   * 1. Replays Headline Glow Emergence (Luminous atmospheric glow, not typewriter)
   * 2. Runs Typewriter on the Subtext paragraph
   */
  playTypewriter(theme = 'free') {
    this.activeTheme = theme;
    clearAllTypewriterTimeouts();

    // Reset capsule for theme
    this.initCapsuleScroller(theme);

    // 1. Headline Glow Emergence
    const elHeadline = document.getElementById('hero-headline');
    const elLine1 = document.getElementById('hero-title-line1');
    const elLine2 = document.getElementById('hero-title-line2');

    const titleData = theme === 'pro' ? TITLE_PRO : TITLE_FREE;
    if (elLine1) elLine1.innerText = titleData.line1;
    if (elLine2) elLine2.innerText = titleData.line2;

    if (elHeadline) {
      elHeadline.classList.remove('hero-title-glowing');
      void elHeadline.offsetWidth; // Force DOM reflow to restart CSS keyframe
      elHeadline.classList.add('hero-title-glowing');
    }

    // 2. Subtext Typewriter
    const elSubtext = document.getElementById('hero-subtext-content');
    const curSubtext = document.getElementById('hero-subtext-cursor');
    const subtextText = theme === 'pro' ? SUBTEXT_PRO : SUBTEXT_FREE;

    if (!elSubtext) return;

    elSubtext.innerText = '';
    if (curSubtext) {
      curSubtext.classList.remove('hidden');
    }

    let totalDelay = 100;

    for (let i = 0; i < subtextText.length; i++) {
      const char = subtextText[i];
      const t = setTimeout(() => {
        elSubtext.innerText += char;
      }, totalDelay);
      typewriterTimeouts.push(t);
      totalDelay += 12;
    }

    const tFinish = setTimeout(() => {
      if (curSubtext) {
        curSubtext.classList.add('hidden');
      }
    }, totalDelay + 300);
    typewriterTimeouts.push(tFinish);
  }
};

/**
 * NyayaVani (न्यायवाणी) — Dynamic Theme & Mode Manager
 * Handles synchronization between the top Free/Pro slider switch,
 * the sidebar operating tier buttons, and CSS variables.
 */

import { HeroAnimations } from './hero-animations.js';
import { LivingSphere } from './sphere.js';

const THEME_STORAGE_KEY = 'nyayavani_ui_theme';

export const ThemeManager = {
  currentTheme: 'free', // 'free' or 'pro'
  currentTier: 'BHARAT_GRASSROOTS_AID', // 'BHARAT_GRASSROOTS_AID' or 'ENTERPRISE_LEGAL_SUITE'

  init() {
    const saved = localStorage.getItem(THEME_STORAGE_KEY) || 'free';
    this.applyTheme(saved, false);
  },

  applyTheme(theme, save = true) {
    this.currentTheme = theme === 'pro' ? 'pro' : 'free';
    this.currentTier = this.currentTheme === 'pro' ? 'ENTERPRISE_LEGAL_SUITE' : 'BHARAT_GRASSROOTS_AID';

    // 1. Set DOM attribute
    document.documentElement.setAttribute('data-theme', this.currentTheme);
    document.body.setAttribute('data-theme', this.currentTheme);
    LivingSphere.setTier(this.currentTheme);

    // 2. Update Top Slider Switch
    const btnFree = document.getElementById('slider-btn-free');
    const btnPro = document.getElementById('slider-btn-pro');
    if (btnFree && btnPro) {
      if (this.currentTheme === 'free') {
        btnFree.classList.add('active');
        btnPro.classList.remove('active');
      } else {
        btnPro.classList.add('active');
        btnFree.classList.remove('active');
      }
    }

    // 3. Update Left Sidebar Operating Tier Buttons
    const sideFree = document.getElementById('btn-tier-free');
    const sidePro = document.getElementById('btn-tier-pro');
    if (sideFree && sidePro) {
      if (this.currentTheme === 'free') {
        sideFree.className = 'p-3 text-left rounded-xl border-2 border-blue-600 bg-blue-50 text-slate-900 transition flex items-center justify-between shadow-sm';
        const spanStatus = sideFree.querySelector('span');
        if (spanStatus) {
          spanStatus.innerText = 'ACTIVE';
          spanStatus.className = 'text-xs text-white font-mono font-bold px-2.5 py-0.5 rounded-full bg-[#7C3AED] shadow-sm';
        }

        sidePro.className = 'p-3 text-left rounded-xl border border-slate-200 bg-white hover:border-slate-300 text-slate-700 transition flex items-center justify-between';
        const spanPro = sidePro.querySelector('span');
        if (spanPro) {
          spanPro.innerText = 'PRO';
          spanPro.className = 'text-xs text-slate-400 font-mono';
        }
      } else {
        sidePro.className = 'p-3 text-left rounded-xl border-2 border-[#FBBF24] bg-[#0A0B0E] text-white transition flex items-center justify-between shadow-md';
        const spanPro = sidePro.querySelector('span');
        if (spanPro) {
          spanPro.innerText = 'ACTIVE';
          spanPro.className = 'text-xs text-white font-mono font-bold px-2.5 py-0.5 rounded-full bg-[#047857] border border-[#065F46] shadow-sm';
        }

        sideFree.className = 'p-3 text-left rounded-xl border border-slate-800 bg-[#0A0B0E] hover:border-slate-700 text-slate-400 transition flex items-center justify-between';
        const spanFree = sideFree.querySelector('span');
        if (spanFree) {
          spanFree.innerText = 'FREE';
          spanFree.className = 'text-xs text-slate-500 font-mono';
        }
      }
    }

    // 4. Update Header CTA Button based on Mode
    const btnTopCta = document.getElementById('btn-top-cta');
    if (btnTopCta) {
      if (this.currentTheme === 'free') {
        btnTopCta.innerHTML = `<span>Enter Legal Chat</span><svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M14 5l7 7m0 0l-7 7m7-7H3"/></svg>`;
        btnTopCta.setAttribute('onclick', 'enterChatFlow()');
      } else {
        btnTopCta.innerHTML = `<span>Access Guideline Agent</span><svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M14 5l7 7m0 0l-7 7m7-7H3"/></svg>`;
        btnTopCta.setAttribute('onclick', 'scrollToProStudio()');
      }
    }

    // 5. Update Hero Main CTA Button based on Mode
    const btnHeroCta = document.getElementById('hero-main-cta');
    if (btnHeroCta) {
      if (this.currentTheme === 'free') {
        btnHeroCta.innerHTML = `<span>START WITH YOUR VOICE</span><svg class="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M19 14l-7 7m0 0l-7-7m7 7V3"/></svg>`;
        btnHeroCta.setAttribute('onclick', 'startVoiceChatFlow()');
      } else {
        btnHeroCta.innerHTML = `<span>INITIALIZE CASE GUIDELINE AGENT</span><svg class="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M14 5l7 7m0 0l-7 7m7-7H3"/></svg>`;
        btnHeroCta.setAttribute('onclick', 'scrollToProStudio()');
      }
    }

    // 6. Toggle Workspace Views (Free Chatbot vs. Pro End-to-End Guideline Studio)
    const freeView = document.getElementById('free-workspace-view');
    const proView = document.getElementById('pro-workspace-view');
    if (freeView && proView) {
      if (this.currentTheme === 'free') {
        freeView.classList.remove('hidden');
        proView.classList.add('hidden');
      } else {
        proView.classList.remove('hidden');
        freeView.classList.add('hidden');
      }
    }

    if (save) {
      try {
        localStorage.setItem(THEME_STORAGE_KEY, this.currentTheme);
      } catch (e) {}
      // Re-trigger glowing typewriter emergence when user changes theme
      HeroAnimations.playTypewriter(this.currentTheme);
    }
  },

  setTier(tier) {
    if (tier === 'ENTERPRISE_LEGAL_SUITE') {
      this.applyTheme('pro');
    } else {
      this.applyTheme('free');
    }
  },

  getTheme() {
    return this.currentTheme;
  },

  getTier() {
    return this.currentTier;
  }
};

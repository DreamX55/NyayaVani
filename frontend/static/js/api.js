/**
 * NyayaVani (न्यायवाणी) — API Network Client Module
 * Handles all backend communication, session isolation, and token lifecycle.
 */

const SESSION_STORAGE_KEY = 'nyayavani_session_token';
let inMemorySessionToken = null;

export const ApiClient = {
  getSessionToken() {
    if (inMemorySessionToken) return inMemorySessionToken;
    try {
      const stored = sessionStorage.getItem(SESSION_STORAGE_KEY);
      if (stored) {
        inMemorySessionToken = stored;
        return stored;
      }
    } catch (e) {
      // Memory fallback if storage restricted
    }
    const freshToken = 'nv-sess-' + Date.now() + '-' + Math.random().toString(36).substring(2, 10);
    inMemorySessionToken = freshToken;
    try {
      sessionStorage.setItem(SESSION_STORAGE_KEY, freshToken);
    } catch (e) {}
    return freshToken;
  },

  resetSessionToken() {
    inMemorySessionToken = 'nv-sess-' + Date.now() + '-' + Math.random().toString(36).substring(2, 10);
    try {
      sessionStorage.setItem(SESSION_STORAGE_KEY, inMemorySessionToken);
    } catch (e) {}
    return inMemorySessionToken;
  },

  getAuthHeaders(extraHeaders = {}) {
    const token = this.getSessionToken();
    return {
      'X-Session-Token': token,
      'Authorization': `Bearer ${token}`,
      ...extraHeaders
    };
  },

  async getStatus() {
    const res = await fetch('/api/status', {
      headers: this.getAuthHeaders(),
      cache: 'no-store'
    });
    if (!res.ok) throw new Error('Service unavailable');
    return await res.json();
  },

  async resolveGeoProfile(query) {
    if (!query || !query.trim()) return null;
    const res = await fetch('/api/geo/resolve', {
      method: 'POST',
      headers: this.getAuthHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify({ query: query.trim() })
    });
    if (!res.ok) return null;
    return await res.json();
  },

  async submitChat(payload) {
    if (payload && !payload.message && payload.text) {
      payload.message = payload.text;
    }
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: this.getAuthHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify(payload)
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Service request failed');
    }
    return await res.json();
  },

  async transcribeAudio(audioBlob, filename = 'speech.wav') {
    const formData = new FormData();
    formData.append('audio', audioBlob, filename);
    let res = await fetch('/api/transcribe', {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: formData
    }).catch(() => null);

    if (!res || !res.ok) {
      res = await fetch('/api/stt', {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: formData
      });
    }

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Voice transcription failed');
    }
    return await res.json();
  },

  async generateTTS(payload) {
    let res = await fetch('/api/rights/audio', {
      method: 'POST',
      headers: this.getAuthHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify(payload)
    }).catch(() => null);

    if (!res || !res.ok) {
      res = await fetch('/api/tts', {
        method: 'POST',
        headers: this.getAuthHeaders({ 'Content-Type': 'application/json' }),
        body: JSON.stringify(payload)
      });
    }

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Speech synthesis failed');
    }
    return await res.json();
  },

  async approvePacket(packetId, caseId, approvedBy = 'Client') {
    let res = await fetch(`/api/pro/packet/${packetId}/approve`, {
      method: 'POST',
      headers: this.getAuthHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify({ approved_by: approvedBy, packet_id: packetId, case_id: caseId })
    }).catch(() => null);

    if (!res || !res.ok) {
      res = await fetch('/api/pro/approve', {
        method: 'POST',
        headers: this.getAuthHeaders({ 'Content-Type': 'application/json' }),
        body: JSON.stringify({ approved_by: approvedBy, packet_id: packetId, case_id: caseId })
      });
    }

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Approval failed');
    }
    return await res.json();
  },

  async testOutboundBoundary(packetId, caseId) {
    let res = await fetch(`/api/pro/packet/${packetId}/send`, {
      method: 'POST',
      headers: this.getAuthHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify({ packet_id: packetId, case_id: caseId })
    }).catch(() => null);

    if (!res || !res.ok) {
      res = await fetch('/api/pro/outbound', {
        method: 'POST',
        headers: this.getAuthHeaders({ 'Content-Type': 'application/json' }),
        body: JSON.stringify({ packet_id: packetId, case_id: caseId })
      });
    }

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Boundary validation failed');
    }
    return await res.json();
  },

  async purgeSession() {
    let res = await fetch('/api/privacy/purge', {
      method: 'POST',
      headers: this.getAuthHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify({
        session_id: this.getSessionToken(),
        session_token: this.getSessionToken()
      })
    }).catch(() => null);

    if (!res || !res.ok) {
      res = await fetch('/api/session/purge', {
        method: 'POST',
        headers: this.getAuthHeaders({ 'Content-Type': 'application/json' }),
        body: JSON.stringify({
          session_id: this.getSessionToken(),
          session_token: this.getSessionToken()
        })
      });
    }

    if (!res.ok) {
      throw new Error('Failed to purge session data');
    }
    return await res.json();
  },

  /* -----------------------------------------------------------------------
     Pro Simulated Calling & Negotiation Sandbox Endpoints
     ----------------------------------------------------------------------- */
  async dispatchProCall(payload) {
    const res = await fetch('/api/pro/call/dispatch', {
      method: 'POST',
      headers: this.getAuthHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify(payload)
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to dispatch simulated call');
    }
    return await res.json();
  },

  async sendCallDialogue(sessionId, text) {
    const res = await fetch('/api/pro/call/dialogue', {
      method: 'POST',
      headers: this.getAuthHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify({ session_id: sessionId, text: text })
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Dialogue response failed');
    }
    return await res.json();
  },

  async concludeProCall(sessionId) {
    const res = await fetch('/api/pro/call/conclude', {
      method: 'POST',
      headers: this.getAuthHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify({ session_id: sessionId })
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to conclude simulation call');
    }
    return await res.json();
  },

  async addPacketAttachment(packetId, file) {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`/api/pro/packet/${packetId}/attachment`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: formData
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to attach evidence file');
    }
    return await res.json();
  }
};

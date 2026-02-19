/**
 * Nexus API Client — v2.1
 * Using RELATIVE URLs via Node proxy — eliminates all cross-origin cookie issues.
 * Node server (localhost:3000) proxies /api/* → Django (127.0.0.1:8000).
 * Both the page and API are same-origin → session cookies work perfectly.
 */

const API_BASE_URL = '/api/chat';

class NexusAPI {
  constructor() {
    this.baseURL = API_BASE_URL;
    this.isAuthenticated = false;
  }

  // ── CORE REQUEST ────────────────────────────────────────────────
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      method: 'GET',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    const method = (config.method || 'GET').toUpperCase();
    if (['POST', 'PUT', 'DELETE', 'PATCH'].includes(method)) {
      const csrfToken = this.getCookie('csrftoken');
      if (csrfToken) config.headers['X-CSRFToken'] = csrfToken;
    }

    const response = await fetch(url, config);

    const contentType = response.headers.get('content-type') || '';
    const isJson = contentType.includes('application/json');
    const payload = isJson ? await response.json() : await response.text();

    if (!response.ok) {
      const msg = typeof payload === 'string' ? payload : JSON.stringify(payload);
      throw new Error(`HTTP ${response.status}: ${msg}`);
    }

    return payload;
  }

  // ── CSRF HELPER ─────────────────────────────────────────────────
  getCookie(name) {
    const match = document.cookie
      .split(';')
      .map(c => c.trim())
      .find(c => c.startsWith(name + '='));
    return match ? decodeURIComponent(match.split('=')[1]) : null;
  }

  // Fetch CSRF cookie — via proxy, /admin/login/ is on same origin
  async fetchCSRFToken() {
    try {
      await fetch('/admin/login/', {
        method: 'GET',
        credentials: 'include',
      });
    } catch (e) {
      console.warn('NexusAPI: Could not pre-fetch CSRF token:', e.message);
    }
  }

  // ── AUTH ─────────────────────────────────────────────────────────
  async login(username, password) {
    await this.fetchCSRFToken();
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);
    formData.append('csrfmiddlewaretoken', this.getCookie('csrftoken') || '');
    formData.append('next', '/admin/');

    const response = await fetch('/admin/login/', {
      method: 'POST',
      body: formData,
      credentials: 'include',
    });

    if (response.ok || response.redirected || response.status === 302) {
      this.isAuthenticated = true;
      return true;
    }
    this.isAuthenticated = false;
    return false;
  }

  // Called after passphrase gate passes — sets up session via custom endpoint
  async activateSession() {
    const data = await this.request('/auth/authenticate/', {
      method: 'POST',
      body: JSON.stringify({ passphrase: 'nexus2025' }),
    });

    if (data.success) {
      this.isAuthenticated = true;
      console.log('✅ Session activated');
    } else {
      this.isAuthenticated = false;
      throw new Error(data.message || 'Authentication failed');
    }
  }

  // ── PUBLIC CLIENT API ────────────────────────────────────────────
  async startConversation(clientName, clientEmail, message, tag = 'greeting') {
    return this.request('/start_conversation/', {
      method: 'POST',
      body: JSON.stringify({ client_name: clientName, client_email: clientEmail, message, tag }),
    });
  }

  async sendMessage(conversationId, message) {
    return this.request('/send_message/', {
      method: 'POST',
      body: JSON.stringify({ conversation_id: conversationId, message }),
    });
  }

  async getConversation(conversationId) {
    return this.request(`/conversation/?id=${conversationId}`);
  }

  // ── DEVELOPER DASHBOARD API ──────────────────────────────────────
  async getConversations(status = 'active') {
    return this.request(`/conversations/?status=${status}`);
  }

  async getConversationDetail(conversationId) {
    // Client-safe detail endpoint (public) lives on ChatViewSet
    // Developer dashboard uses /conversations/:id/ (staff session) via getConversationAdminDetail
    return this.getConversation(conversationId);
  }

  // Developer-only conversation detail (requires authenticated developer session)
  async getConversationAdminDetail(conversationId) {
    return this.request(`/conversations/${conversationId}/`);
  }

  // Alias — returns messages array directly
  async getMessages(conversationId) {
    const detail = await this.getConversationDetail(conversationId);
    return Array.isArray(detail) ? detail : (detail.messages || []);
  }

  async sendDeveloperMessage(conversationId, content) {
    return this.request(`/conversations/${conversationId}/send_message/`, {
      method: 'POST',
      body: JSON.stringify({ content }),
    });
  }

  async markAsRead(conversationId) {
    return this.request(`/conversations/${conversationId}/mark_read/`, {
      method: 'POST',
      body: JSON.stringify({}),
    });
  }

  async archiveConversation(conversationId) {
    return this.request(`/conversations/${conversationId}/archive/`, {
      method: 'POST',
      body: JSON.stringify({}),
    });
  }

  // Accepts (name, content) or just (content) — auto-generates name if needed
  async createQuickReplyTemplate(nameOrContent, content) {
    let name, templateContent;
    if (content === undefined) {
      templateContent = nameOrContent;
      name = nameOrContent.slice(0, 30).trim() + (nameOrContent.length > 30 ? '...' : '');
    } else {
      name = nameOrContent;
      templateContent = content;
    }
    return this.request('/templates/', {
      method: 'POST',
      body: JSON.stringify({ name, content: templateContent }),
    });
  }

  async getQuickReplyTemplates() {
    return this.request('/templates/');
  }

  async getAutoReplySettings() {
    return this.request('/settings/auto_reply/');
  }

  async updateAutoReplySettings(enabled, delay) {
    return this.request('/settings/auto_reply/', {
      method: 'POST',
      body: JSON.stringify({ enabled, delay }),
    });
  }
}

// Global singleton
const nexusAPI = new NexusAPI();
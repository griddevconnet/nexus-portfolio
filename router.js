/**
 * Nexus Router — v2.0
 * Simple, clean navigation for static HTML files.
 * Uses window.location.href instead of innerHTML swapping
 * to preserve JS contexts, animations, and event listeners.
 */

const NexusRouter = {
  routes: {
    '/':                   'index.html',
    '/index.html':         'index.html',
    '/chat':               'nexus_chat.html',
    '/nexus_chat.html':    'nexus_chat.html',
    '/developer':          'dev_chat.html',
    '/developer.nexus':    'dev_chat.html',
    '/dev_chat.html':      'dev_chat.html',
  },

  init() {
    // Intercept only internal anchor clicks with href starting with "/"
    document.addEventListener('click', (e) => {
      const link = e.target.closest('a[href]');
      if (!link) return;

      const href = link.getAttribute('href');

      // Skip: external links, anchors (#), mailto, tel
      if (!href || href.startsWith('http') || href.startsWith('#') ||
          href.startsWith('mailto') || href.startsWith('tel')) return;

      // Skip: direct .html file links — let the browser handle normally
      if (href.endsWith('.html')) return;

      // Handle route paths like /developer, /chat, /
      if (href.startsWith('/')) {
        const target = this.routes[href];
        if (target) {
          e.preventDefault();
          this.go(target);
        }
        // If no route match, let browser handle it
      }
    });

    // Handle browser back/forward buttons
    window.addEventListener('popstate', () => {
      const path = window.location.pathname;
      const cleanPath = path.replace(/\/$/, '') || '/';
      const target = this.routes[cleanPath];
      if (target && !window.location.pathname.endsWith(target)) {
        window.location.href = target;
      }
    });
  },

  go(page) {
    // Simple, reliable navigation — no DOM destruction
    window.location.href = page;
  },

  // Helper: navigate by route name from JS
  navigate(routePath) {
    const target = this.routes[routePath];
    if (target) {
      this.go(target);
    } else {
      console.warn(`NexusRouter: No route found for "${routePath}"`);
    }
  }
};

// Auto-init when DOM is ready — with guard for already-loaded DOM
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => NexusRouter.init());
} else {
  // DOM already loaded (script placed at bottom of body)
  NexusRouter.init();
}

// Expose globally
window.NexusRouter = NexusRouter;
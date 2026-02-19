// Simple URL router for Nexus site
class NexusRouter {
  constructor() {
    this.routes = {
      '/': 'index.html',
      '/developer': 'dev_chat.html',
      '/developer.nexus': 'dev_chat.html',
      '/chat': 'nexus_chat.html'
    };
    this.init();
  }

  init() {
    // Handle initial page load
    this.handleRoute();
    
    // Handle browser navigation
    window.addEventListener('popstate', () => this.handleRoute());
    
    // Handle navigation clicks
    document.addEventListener('click', (e) => {
      const link = e.target.closest('a[href^="/"]');
      if (link) {
        e.preventDefault();
        const path = link.getAttribute('href');
        this.navigate(path);
      }
    });
  }

  handleRoute() {
    const path = window.location.pathname;
    const cleanPath = path.replace(/\/$/, '') || '/';
    
    if (this.routes[cleanPath]) {
      this.loadPage(this.routes[cleanPath]);
    } else if (cleanPath.startsWith('/developer')) {
      // Handle any developer sub-paths
      this.loadPage('dev_chat.html');
    }
  }

  navigate(path) {
    window.history.pushState({}, '', path);
    this.handleRoute();
  }

  loadPage(page) {
    // Show loading state
    document.body.style.opacity = '0.5';
    
    fetch(page)
      .then(response => {
        if (response.ok) {
          return response.text();
        }
        throw new Error('Page not found');
      })
      .then(html => {
        document.documentElement.innerHTML = html;
        document.body.style.opacity = '1';
        
        // Re-initialize any scripts that were in the loaded page
        this.reinitializeScripts();
      })
      .catch(error => {
        console.error('Failed to load page:', error);
        document.body.style.opacity = '1';
        // Fallback to main page
        window.location.href = 'index.html';
      });
  }

  reinitializeScripts() {
    // Re-run any inline scripts that were loaded
    const scripts = document.querySelectorAll('script:not([src])');
    scripts.forEach(script => {
      const newScript = document.createElement('script');
      newScript.textContent = script.textContent;
      document.head.appendChild(newScript);
      document.head.removeChild(newScript);
    });
  }
}

// Initialize router when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  new NexusRouter();
});

// Export for global access
window.NexusRouter = NexusRouter;

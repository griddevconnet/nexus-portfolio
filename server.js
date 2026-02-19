const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 3000;
const DJANGO_HOST = '127.0.0.1';
const DJANGO_PORT = 8000;

const MIME_TYPES = {
  '.html': 'text/html',
  '.css': 'text/css',
  '.js': 'text/javascript',
  '.json': 'application/json',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.gif': 'image/gif',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon'
};

// Route mapping
const routes = {
  '/': 'index.html',
  '/index.html': 'index.html',
  '/portfolio': 'portfolio.html',
  '/chat': 'nexus_chat.html',
  '/nexus_chat.html': 'nexus_chat.html',
  '/developer': 'dev_chat.html',
  '/developer.nexus': 'dev_chat.html',
  '/dev_chat.html': 'dev_chat.html',
  '/developer-dashboard.html': 'dev_chat.html'
};

// ── PROXY FUNCTION ────────────────────────────────────────────────────────────
// Forwards /api/* and /admin/* requests to Django (127.0.0.1:8000).
// This makes both the page and API share the same origin (localhost:3000),
// so session cookies are sent without any SameSite cross-origin restrictions.
// No npm packages needed — uses Node's built-in http module.
function proxyToDjango(req, res) {
  console.log(`[Proxy] ${req.method} ${req.url} → Django`);
  console.log(`[Proxy] Request headers:`, req.headers);
  
  const options = {
    hostname: DJANGO_HOST,
    port: DJANGO_PORT,
    path: req.url,          // preserve full path + query string
    method: req.method,
    headers: {
      ...req.headers,
      host: `${DJANGO_HOST}:${DJANGO_PORT}`,  // tell Django its real host
      'x-forwarded-for': req.socket.remoteAddress,
      'x-forwarded-proto': 'http',
    },
  };

  const proxyReq = http.request(options, (proxyRes) => {
    // Debug: Log response details
    console.log(`[Proxy] Response status: ${proxyRes.statusCode}`);
    console.log(`[Proxy] Response headers:`, proxyRes.headers);
    
    // Forward all headers from Django back to browser
    // This includes Set-Cookie, Content-Type, etc.
    // Don't modify headers - forward them exactly as Django sends them
    res.writeHead(proxyRes.statusCode, proxyRes.headers);
    
    // Forward response body
    proxyRes.pipe(res, { end: true });
  });

  // Handle potential proxy errors
  proxyReq.on('error', (err) => {
    console.error(`[Proxy Error] ${req.method} ${req.url} →`, err.message);
    if (!res.headersSent) {
      res.writeHead(502, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({
        error: 'Django backend unavailable',
        detail: err.message,
        hint: 'Make sure Django is running: python manage.py runserver'
      }));
    }
  });

  // Pipe the request body (needed for POST/PUT requests)
  req.pipe(proxyReq, { end: true });
}

// ── SERVER ────────────────────────────────────────────────────────────
const server = http.createServer((req, res) => {
  let url = req.url;
  
  // Strip query string for routing decisions (proxy keeps full URL)
  const urlWithoutQuery = url.includes('?') ? url.split('?')[0] : url;
  const cleanUrl = urlWithoutQuery.replace(/\/$/, '') || '/';
  
  console.log(`${new Date().toISOString()} - ${req.method} ${url}`);
  
  // Debug: Log when developer route is accessed
  if (cleanUrl === '/developer' || cleanUrl === '/developer/') {
    console.log('[Server] Developer route accessed - serving dev_chat.html');
  }
  
  // ── Route /api/* and /admin/* to Django via proxy ──
  if (cleanUrl.startsWith('/api/') || cleanUrl.startsWith('/admin/')) {
    proxyToDjango(req, res);
    return;
  }

  // ── Serve static files ──
  try {
    let filePath;

    if (routes[cleanUrl]) {
      filePath = path.join(__dirname, routes[cleanUrl]);
    } else {
      filePath = path.join(__dirname, cleanUrl);
      if (filePath === path.join(__dirname, '')) {
        filePath = path.join(__dirname, 'index.html');
      }
    }

    // Security: prevent directory traversal
    if (!filePath.startsWith(__dirname)) {
      res.writeHead(403);
      res.end('Forbidden');
      return;
    }

    fs.stat(filePath, (err, stats) => {
      if (err || !stats.isFile()) {
        // SPA fallback — serve index.html for unknown routes
        const indexPath = path.join(__dirname, 'index.html');
        fs.readFile(indexPath, (err2, content) => {
          if (err2) {
            res.writeHead(404);
            res.end('File not found');
            return;
          }
          res.writeHead(200, { 'Content-Type': 'text/html' });
          res.end(content);
        });
        return;
      }

      const ext = path.extname(filePath);
      const contentType = MIME_TYPES[ext] || 'application/octet-stream';

      fs.readFile(filePath, (err2, content) => {
        if (err2) {
          res.writeHead(500);
          res.end('Server error');
          return;
        }
        res.writeHead(200, { 'Content-Type': contentType });
        res.end(content);
      });
    });

  } catch (error) {
    console.error('Server error:', error);
    res.writeHead(500);
    res.end('Internal server error');
  }
});

server.listen(PORT, () => {
  console.log(`🚀 Nexus Portfolio Server running at http://localhost:${PORT}`);
  console.log(`📱 Developer Dashboard: http://localhost:${PORT}/developer`);
  console.log(`💬 Chat Interface: http://localhost:${PORT}/chat`);
  console.log(`🏠 Portfolio: http://localhost:${PORT}/`);
  console.log(`🔌 Django API proxied from: http://${DJANGO_HOST}:${DJANGO_PORT}`);
  console.log('\nPress Ctrl+C to stop the server');
});
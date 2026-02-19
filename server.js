const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 3000;
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
  '/chat': 'nexus_chat.html',
  '/nexus_chat.html': 'nexus_chat.html',
  '/developer': 'dev_chat.html',
  '/developer.nexus': 'dev_chat.html',
  '/dev_chat.html': 'dev_chat.html'
};

const server = http.createServer((req, res) => {
  let url = req.url;
  
  // Handle query parameters
  if (url.includes('?')) {
    url = url.split('?')[0];
  }
  
  // Remove trailing slash for consistency
  url = url.replace(/\/$/, '') || '/';
  
  console.log(`${new Date().toISOString()} - ${req.method} ${url}`);
  
  try {
    let filePath;
    
    // Check if it's a defined route
    if (routes[url]) {
      filePath = path.join(__dirname, routes[url]);
    } else {
      // Try to serve static file directly
      filePath = path.join(__dirname, url);
      
      // Default to index.html for root
      if (filePath === path.join(__dirname, '')) {
        filePath = path.join(__dirname, 'index.html');
      }
    }
    
    // Security check - prevent directory traversal
    if (!filePath.startsWith(__dirname)) {
      res.writeHead(403);
      res.end('Forbidden');
      return;
    }
    
    // Check if file exists
    fs.stat(filePath, (err, stats) => {
      if (err || !stats.isFile()) {
        // Fallback to index.html for SPA routing
        const indexPath = path.join(__dirname, 'index.html');
        fs.readFile(indexPath, (err, content) => {
          if (err) {
            res.writeHead(404);
            res.end('File not found');
            return;
          }
          res.writeHead(200, {
            'Content-Type': 'text/html',
            'Access-Control-Allow-Origin': '*'
          });
          res.end(content);
        });
        return;
      }
      
      // Determine content type
      const ext = path.extname(filePath);
      const contentType = MIME_TYPES[ext] || 'application/octet-stream';
      
      // Serve the file
      fs.readFile(filePath, (err, content) => {
        if (err) {
          res.writeHead(500);
          res.end('Server error');
          return;
        }
        
        res.writeHead(200, {
          'Content-Type': contentType,
          'Access-Control-Allow-Origin': '*'
        });
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
  console.log('\nPress Ctrl+C to stop the server');
});

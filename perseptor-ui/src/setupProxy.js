/**
 * PERSEPTOR v2.0 - Custom Proxy Configuration
 * Extends default CRA proxy with longer timeout and SSE support.
 */
const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function (app) {
  app.use(
    '/api',
    createProxyMiddleware({
      target: 'http://localhost:5000',
      changeOrigin: true,
      // 10 minutes timeout for long-running analysis
      timeout: 600000,
      proxyTimeout: 600000,
      onProxyRes: (proxyRes, req, res) => {
        // Disable buffering for SSE endpoints so events stream in real-time
        if (req.url && req.url.includes('/analyze/stream')) {
          proxyRes.headers['cache-control'] = 'no-cache';
          proxyRes.headers['x-accel-buffering'] = 'no';
          // Ensure chunked transfer for streaming
          delete proxyRes.headers['content-length'];
        }
      },
      onError: (err, req, res) => {
        console.error('[Proxy Error]', err.message);
        if (!res.headersSent) {
          res.writeHead(502, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ error: 'Backend connection failed. Is the server running?' }));
        }
      },
    })
  );
};

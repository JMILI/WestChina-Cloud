const http = require('http');
const fs = require('fs');
const path = require('path');
const { URL } = require('url');

const ROOT = path.join(__dirname, 'ui-dist');
const GATEWAY = 'http://127.0.0.1:8080';

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'application/javascript',
  '.css': 'text/css',
  '.json': 'application/json',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon',
  '.woff': 'font/woff',
  '.woff2': 'font/woff2',
  '.ttf': 'font/ttf',
};

function proxyTo(req, res, targetBase, requestUrl) {
  const target = new URL(requestUrl, targetBase);
  const opts = {
    hostname: target.hostname,
    port: target.port,
    path: target.pathname + target.search,
    method: req.method,
    headers: { ...req.headers, host: target.host },
  };
  const proxyReq = http.request(opts, (proxyRes) => {
    res.writeHead(proxyRes.statusCode, proxyRes.headers);
    proxyRes.pipe(res);
  });
  proxyReq.on('error', (e) => {
    res.writeHead(502);
    res.end('Bad Gateway: ' + e.message);
  });
  req.pipe(proxyReq);
}

function proxy(req, res, targetBase) {
  proxyTo(req, res, targetBase, req.url.replace(/^\/prod-api/, ''));
}

function sendFile(res, filePath) {
  const ext = path.extname(filePath);
  res.writeHead(200, { 'Content-Type': MIME[ext] || 'application/octet-stream' });
  fs.createReadStream(filePath).pipe(res);
}

/** 旧版构建未设 router base 时，根路径 /static 会误落到 main，已改为各子应用独立前缀 */
function resolveLegacyRootAsset(urlPath) {
  return null;
}

function shouldServeMainSpa(urlPath) {
  const reserved = ['/main/', '/administrator/', '/ct/', '/prod-api', '/api-ct', '/minio/'];
  if (reserved.some((p) => urlPath.startsWith(p))) return false;
  if (urlPath === '/') return false;
  if (/\.[a-zA-Z0-9]+$/.test(urlPath) && !urlPath.endsWith('.html')) return false;
  return false;
}

const server = http.createServer((req, res) => {
  if (req.url.startsWith('/prod-api')) {
    return proxy(req, res, GATEWAY);
  }
  if (req.url.startsWith('/minio/')) {
    return proxyTo(req, res, 'http://127.0.0.1:9000', req.url.replace(/^\/minio/, ''));
  }
  let urlPath = req.url.split('?')[0];
  if (urlPath === '/') urlPath = '/main/';
  if (urlPath === '/index') {
    res.writeHead(302, { Location: '/main/' });
    return res.end();
  }

  const legacyAsset = resolveLegacyRootAsset(urlPath);
  if (legacyAsset) return sendFile(res, legacyAsset);

  const rel = urlPath.replace(/^\//, '');
  let filePath = path.join(ROOT, rel);
  if (fs.existsSync(filePath) && fs.statSync(filePath).isDirectory()) {
    filePath = path.join(filePath, 'index.html');
  }
  if (fs.existsSync(filePath)) return sendFile(res, filePath);
  const parts = urlPath.split('/').filter(Boolean);
  if (parts.length >= 1) {
    const spaIndex = path.join(ROOT, parts[0], 'index.html');
    if (fs.existsSync(spaIndex)) return sendFile(res, spaIndex);
  }
  if (shouldServeMainSpa(urlPath)) {
    return sendFile(res, path.join(ROOT, 'main', 'index.html'));
  }
  res.writeHead(404);
  res.end('Not Found');
});

server.listen(5000, '0.0.0.0', () => {
  console.log('WestChina local UI:');
  console.log('  main:           http://127.0.0.1:5000/main/');
  console.log('  administrator:  http://127.0.0.1:5000/administrator/');
  console.log('  ct:             http://127.0.0.1:5000/ct/');
});

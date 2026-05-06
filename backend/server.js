const express = require('express');
const http = require('http');
const WebSocket = require('ws');
const fs = require('fs');
const path = require('path');
const { spawn, spawnSync } = require('child_process');

const app = express();
const port = process.env.PORT || 5000;

const UPLOAD_DIR = path.join(__dirname, 'uploads');

if (!fs.existsSync(UPLOAD_DIR)) {
  fs.mkdirSync(UPLOAD_DIR, { recursive: true });
}

function findPythonExecutable() {
  const candidates = [process.env.PYTHON, 'python3', 'python', 'py'].filter(Boolean);
  for (const cmd of candidates) {
      try {
        const res = spawnSync(cmd, ['--version'], { encoding: 'utf8', stdio: 'pipe' });
        if (res.status === 0) {
          console.log(`Using Python executable: ${cmd} (${res.stdout || res.stderr}`);
          return cmd;
        }
      } catch (e) {
      }
  }
  return null;
}

const PY_EXEC = findPythonExecutable();
if (!PY_EXEC) {
  console.log('Python executable not found. Install Python or set the PYTHON env var in the backend container.');
}

app.get('/', (req, res) => {
  res.json({ message: 'Backend + WebSocket server is running' });
});

const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

wss.on('connection', (ws) => {
  console.log('Client connected');

  ws.send(JSON.stringify({
    type: 'connection',
    message: 'WebSocket connection established'
  }));

  ws.on('message', (message) => {
    try {
      const data = JSON.parse(message.toString());
      console.log('Received:', data.type);
      if (data.type === 'image') {
        const imgPayload = data.image || '';
        let base64Data = imgPayload;
        let ext = 'png';

        const dataUrlMatch = imgPayload.match(/^data:(image\/[^;]+);base64,(.+)$/);
        if (dataUrlMatch) {
          const mime = dataUrlMatch[1];
          base64Data = dataUrlMatch[2];
          const m = mime.split('/')[1];
          ext = m === 'jpeg' ? 'jpg' : m;
        }

        const filename = data.filename || `img_${Date.now()}.${ext}`;
        const imgBuffer = Buffer.from(base64Data, 'base64');
        console.log(`Received ${imgBuffer.length} bytes for ${filename} (in-memory)`);

        console.log(`Starting blobdetect.py (stdin) for ${filename}`);
        if (!PY_EXEC) {
          console.log('Cannot start blobdetect: no Python executable available');
          ws.send(JSON.stringify({ type: 'error', message: 'Server: Python not available to run blobdetect' }));
          return;
        }

        const py = spawn(PY_EXEC, ['blobdetect.py', '--from-stdin', '--headless'], { cwd: __dirname, stdio: ['pipe', 'pipe', 'pipe'] });

        py.on('error', (err) => {
          console.error(`Failed to spawn Python process (${PY_EXEC}): ${err.message}`);
          ws.send(JSON.stringify({ type: 'error', message: `Server failed to start Python: ${err.message}` }));
        });

        let stdout = '';
        let stderr = '';

        py.stdout.on('data', (data) => {
          stdout += data.toString();
        });

        py.stderr.on('data', (data) => {
          stderr += data.toString();
        });

        py.on('close', (code) => {
          if (stderr) {
            console.error(`blobdetect stderr for ${filename}: ${stderr.trim()}`);
          }

          console.log(`blobdetect.py exited with code ${code} for ${filename}`);

          let parsed = null;
          const trimmed = stdout.trim();
          if (trimmed) {
            try {
              parsed = JSON.parse(trimmed);
              if (parsed && Array.isArray(parsed.binary)) {
                console.log(`Detected binary for ${filename}: ${JSON.stringify(parsed.binary)}`);
              } else {
                console.log(`blobdetect output for ${filename} did not contain 'binary' array`);
              }
            } catch (e) {
              console.error(`Failed to parse blobdetect JSON for ${filename}: ${e.message}`);
            }
          } else {
            console.log(`blobdetect produced no stdout for ${filename}`);
          }

          if (code === 3) {
            console.log(`No braille binary detected in ${filename}`);
            ws.send(JSON.stringify({ type: 'result', binary: [], file: filename, detected: false }));
            return;
          }

          if (parsed && Array.isArray(parsed.binary)) {
            ws.send(JSON.stringify({ type: 'result', binary: parsed.binary, file: filename, detected: parsed.binary.length > 0 }));
          } else if (trimmed) {
            ws.send(JSON.stringify({ type: 'result', text: trimmed, file: filename }));
          } else {
            ws.send(JSON.stringify({ type: 'result', text: (stderr.trim() || `blobdetect exited with code ${code}`), file: filename }));
          }
        });

        py.stdin.write(imgBuffer);
        py.stdin.end();
      } else if (data.type === 'ping') {
        ws.send(JSON.stringify({
          type: 'pong',
          message: 'Server is alive'
        }));
      } else {
        ws.send(JSON.stringify({
          type: 'error',
          message: 'Unknown message type'
        }));
      }
    } catch (err) {
      console.error('Error parsing message:', err);
      ws.send(JSON.stringify({
        type: 'error',
        message: 'Invalid JSON'
      }));
    }
  });

  ws.on('close', () => {
    console.log('Client disconnected');
  });

  ws.on('error', (err) => {
    console.error('WebSocket error:', err);
  });
});

server.listen(port, '0.0.0.0', () => {
  console.log(`Backend listening on port ${port}`);
});
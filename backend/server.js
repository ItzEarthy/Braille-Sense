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
    console.log('Received type:', data.type);

    if (data.type === 'image') {
      const base64Data = (data.image || '').replace(/^data:image\/[^;]+;base64,/, '');
      const imgBuffer = Buffer.from(base64Data, 'base64');
      
      console.log(`Received ${imgBuffer.length} bytes (in-memory)`);

      if (!PY_EXEC) {
        console.error('Python executable not found.');
        return ws.send(JSON.stringify({ type: 'error', message: 'Python unavailable' }));
      }

      console.log('Starting blobdetect.py via stdin...');
      const py = spawn(PY_EXEC, ['blobdetect.py', '--from-stdin'], { cwd: __dirname });

      let stdout = '';
      let stderr = '';

      py.stdout.on('data', (d) => stdout += d.toString());
      py.stderr.on('data', (d) => {
        const text = d.toString();
        stderr += text;
        console.log('Python stderr:', text.trim());
      });

      py.on('close', (code) => {
        const text = stdout.trim() || stderr.trim() || `Exited with code ${code}`;
        ws.send(JSON.stringify({ type: 'output', text }));
      });

      py.on('error', (err) => {
        console.error('Python spawn error:', err);
        ws.send(JSON.stringify({ type: 'error', message: `Python error: ${err.message}` }));
      });

      py.stdin.write(imgBuffer);
      py.stdin.end();

    } else {
      ws.send(JSON.stringify({ type: 'error', message: 'Unknown message type' }));
    }
  } catch (err) {
    console.error('WebSocket message error:', err);
    ws.send(JSON.stringify({ type: 'error', message: 'Invalid JSON or parsing error' }));
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
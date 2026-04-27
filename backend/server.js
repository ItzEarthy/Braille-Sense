const express = require('express');
const http = require('http');
const WebSocket = require('ws');

const app = express();
const port = process.env.PORT || 5000;

// Basic API route
app.get('/', (req, res) => {
  res.json({ message: 'Backend + WebSocket server is running' });
});

// Create HTTP server from Express app
const server = http.createServer(app);

// Create WebSocket server
const wss = new WebSocket.Server({ server, path: '/ws/' });

wss.on('connection', (ws) => {
  console.log('WebSocket client connected');

  ws.send(JSON.stringify({
    type: 'connection',
    message: 'Connected to backend WebSocket'
  }));

  ws.on('message', (message) => {
    console.log('Received:', message.toString());
    try {
      const data = JSON.parse(message.toString());
      console.log('Received type:', data.type);

      if (data.type === 'test_image' || data.type === 'image') {
        ws.send(JSON.stringify({
          type: 'result',
          isBraille: true,
          translatedText: 'sample braille translation'
        }));
      } else if (data.type === 'ping') {
        ws.send(JSON.stringify({
          type: 'pong',
          message: 'Server is alive'
        }));
      } else {
        ws.send(JSON.stringify({
          type: 'echo',
          message: 'Message received'
        }));
      }
    } catch (err) {
      console.error('Error parsing message:', err);
      ws.send(JSON.stringify({
        type: 'error',
        message: 'Invalid JSON sent to backend'
      }));
    }
  });

  ws.on('close', () => {
    console.log('WebSocket client disconnected');
  });

  ws.on('error', (err) => {
    console.error('WebSocket error:', err);
  });
});

// Bind explicitly to 0.0.0.0
server.listen(port, '0.0.0.0', () => {
  console.log(`Backend listening on port ${port}`);
});
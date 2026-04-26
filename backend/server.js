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
    message: 'Connected to backend websocket'
  }));

  ws.on('message', (message) => {
    console.log('Received:', message.toString());

    try {
      const data = JSON.parse(message.toString());

      if (data.type === 'test_image') {
        // for now just mock a result
        ws.send(JSON.stringify({
          type: 'result',
          isBraille: true,
          translatedText: 'sample braille translation'
        }));
      } else {
        ws.send(JSON.stringify({
          type: 'echo',
          message: 'Message received'
        }));
      }
    } catch (err) {
      ws.send(JSON.stringify({
        type: 'error',
        message: 'Invalid JSON sent to backend'


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
        ws.send(JSON.stringify({
          type: 'result',
          text: 'Image received successfully.'
        }));
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
    console.log('WebSocket client disconnected');
  });
});

// bind explicitly to 0.0.0.0
server.listen(port, '0.0.0.0', () => {
  console.log(`Backend listening on port ${port}`);
    console.log('Client disconnected');
  });

  ws.on('error', (err) => {
    console.error('WebSocket error:', err);
  });
});

server.listen(port, '0.0.0.0', () => {
  console.log(`Backend listening on port ${port}`);
});
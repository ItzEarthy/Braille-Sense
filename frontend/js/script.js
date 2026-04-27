// HTML Elements
const button = document.getElementById('enable-camera');
const video = document.getElementById('camera-feed');
const placeholder = document.getElementById('camera-placeholder');
const overlay = document.getElementById('camera-overlay');
const mainView = document.getElementById('main-view');
const flash = document.getElementById('flash-overlay');
const settingsPanel = document.getElementById('settings-panel');
const closeSettings = document.getElementById('close-settings');
const ttsToggle = document.getElementById('tts-toggle');
const settings = document.getElementById("setting-button");
const textSizeArea = document.getElementById('text-size-area');
const ttsVolumeArea = document.getElementById('tts-volume-area');
const ttsToggleRow = document.getElementById('tts-toggle-row');

let socket = null;
let isFrozen = false;
const canvas = document.getElementById('freeze-frame');
const ctx = canvas.getContext('2d');

//Variables
let lastTap = 0;
let videoTrack = null;
let ttsVolume = 1;
let ttsEnabled = false;
let textSize = 1;

// Connect to backend WebSocket (single definition, with retry)
function connectWebSocket(retries = 5) {
  const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
  socket = new WebSocket(`${protocol}://${window.location.host}/ws/`);

  socket.onopen = () => {
    console.log('WebSocket connected');
  };

  socket.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      console.log('Message from server:', data);

      if (data.type === 'result') {
        placeholder.textContent = data.text;
        speak(data.text);
      }
    } catch (err) {
      console.error('Invalid message from server:', err);
    }
  };

  socket.onerror = (err) => {
    console.error('WebSocket error:', err);
  };

  socket.onclose = () => {
    console.log('WebSocket closed');
    if (retries > 0) {
      setTimeout(() => connectWebSocket(retries - 1), 1000);
    }
  };
}

// Capture current frame from video as base64
function captureFrameAsBase64() {
  if (!video.videoWidth || !video.videoHeight) {
    console.error('Video not ready yet');
    return null;
  }

  const captureCanvas = document.createElement('canvas');
  captureCanvas.width = video.videoWidth;
  captureCanvas.height = video.videoHeight;

  const captureCtx = captureCanvas.getContext('2d');
  captureCtx.drawImage(video, 0, 0, captureCanvas.width, captureCanvas.height);

  return captureCanvas.toDataURL('image/jpeg', 0.8);
}

// Start live video feed from camera
button.addEventListener('click', async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: 'environment' }
    });

    video.srcObject = stream;
    videoTrack = stream.getVideoTracks()[0];

    video.style.display = 'block';
    placeholder.style.display = 'none';
    overlay.style.display = 'block';

  } catch (err) {
    console.error(err);
    alert('Camera access denied or not available.');
  }
});

// Settings button
settings.addEventListener('click', () => {
  toggleSettings();
});

// Tap video to freeze frame and send to backend
video.addEventListener('click', () => {
  // If frozen → unfreeze
  if (isFrozen) {
    canvas.style.display = 'none';
    video.style.display = 'block';
    isFrozen = false;
    console.log('Camera resumed');
    return;
  }

  // Draw current frame onto canvas
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

  // Show frozen frame, hide live video
  canvas.style.display = 'block';
  video.style.display = 'none';
  isFrozen = true;

  // Flash effect
  flash.style.transition = 'none';
  flash.style.opacity = 0;
  flash.offsetHeight;

  flash.style.transition = 'opacity 0.1s ease-in-out';
  flash.style.opacity = 0.8;

  setTimeout(() => {
    flash.style.opacity = 0;
  }, 100);

  // Send image (optional: real image instead of placeholder)
  if (socket && socket.readyState === WebSocket.OPEN) {
    const base64Image = captureFrameAsBase64();

    if (!base64Image) {
      console.error('Could not capture image.');
      return;
    }

    socket.send(JSON.stringify({
      type: 'image',
      image: base64Image,
      timestamp: Date.now()
    }));

    console.log('Image sent to backend');
  } else {
    console.warn('WebSocket not connected');
  }
});

// Tap frozen canvas to unfreeze
canvas.addEventListener('click', () => {
  if (isFrozen) {
    canvas.style.display = 'none';
    video.style.display = 'block';
    isFrozen = false;
    console.log('Camera resumed');
  }
});

function connectWebSocket(retries = 5) {
  const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
  socket = new WebSocket(`${protocol}://${window.location.host}/ws/`);

  socket.onopen = () => {
    console.log('WebSocket connected');
  };

  socket.onmessage = (event) => {
    console.log('Message from backend:', event.data);
  };

  socket.onerror = (err) => {
    console.error('WebSocket error:', err);
  };

  socket.onclose = () => {
    console.log('WebSocket closed');

    if (retries > 0) {
      setTimeout(() => connectWebSocket(retries - 1), 1000);
    }
  };
}

connectWebSocket();
    setTimeout(() => {
      flash.style.opacity = 0;
    }, 100);


// Detect double tap (mobile) + double click (desktop) for settings
mainView.addEventListener('click', () => {
  const now = Date.now();
  const timeBetween = now - lastTap;

  if (timeBetween < 300 && timeBetween > 0) {
    toggleSettings();
  }

  lastTap = now;
});

// Text-to-speech
function speak(text) {
  if (!ttsEnabled) return;

  const utterance = new SpeechSynthesisUtterance(text);
  const length = text.length;

  let soundLevel;

  if (length < 20) {
    soundLevel = 1.2;
    utterance.rate = 1.15;
    utterance.pitch = 1.2;
  } else if (length < 80) {
    soundLevel = 1.0;
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
  } else {
    soundLevel = 0.8;
    utterance.rate = 0.85;
    utterance.pitch = 0.9;
  }

  utterance.volume = Math.max(0, Math.min(1, soundLevel * ttsVolume));
  speechSynthesis.speak(utterance);
}

// Toggle settings panel
function toggleSettings() {
  const isOpen = settingsPanel.style.display === 'block';
  settingsPanel.style.display = isOpen ? 'none' : 'block';
}

// Text size controls
textSizeArea.addEventListener('click', (e) => {
  const rect = textSizeArea.getBoundingClientRect();
  const x = e.clientX - rect.left;

  if (x < rect.width / 2) {
    textSize = Math.max(0.5, +(textSize - 0.1).toFixed(2));
  } else {
    textSize = Math.min(2, +(textSize + 0.1).toFixed(2));
  }

  placeholder.style.fontSize = textSize + 'rem';
});

// TTS volume controls
ttsVolumeArea.addEventListener('click', (e) => {
  if (!ttsEnabled) return;

  const rect = ttsVolumeArea.getBoundingClientRect();
  const x = e.clientX - rect.left;

  if (x < rect.width / 2) {
    ttsVolume = Math.max(0, +(ttsVolume - 0.1).toFixed(2));
  } else {
    ttsVolume = Math.min(1, +(ttsVolume + 0.1).toFixed(2));
  }
});

// TTS toggle
ttsToggleRow.addEventListener('click', () => {
  ttsEnabled = !ttsEnabled;
  ttsToggle.checked = ttsEnabled;
  ttsVolumeArea.classList.toggle('disabled', !ttsEnabled);
});

// Close settings button
closeSettings.addEventListener('click', () => {
  settingsPanel.style.display = 'none';
});

// Connect WebSocket on page load
window.addEventListener('load', () => {
  connectWebSocket();
});
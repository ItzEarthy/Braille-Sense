//HTHML Elements
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

//Variables
let lastTap = 0;
let videoTrack = null;
let ttsVolume = 1;
let ttsEnabled = false;
let textSize = 1;
let socket = null;

// Connect to backend WebSocket
function connectWebSocket() {
  const protocol = window.location.protocol === "https:" ? "wss" : "ws";
  const wsUrl = `${protocol}://${window.location.hostname}:11112`;

  socket = new WebSocket(wsUrl);

  socket.onopen = () => {
    console.log("WebSocket connected");
  };

  socket.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      console.log("Message from server:", data);

      if (data.type === "result") {
        placeholder.textContent = data.text;
        speak(data.text);
      }
    } catch (err) {
      console.error("Invalid message from server:", err);
    }
  };

  socket.onclose = () => {
    console.log("WebSocket disconnected");
  };

  socket.onerror = (err) => {
    console.error("WebSocket error:", err);
  };
}

// Capture current frame from video
function captureFrameAsBase64() {
  if (!video.videoWidth || !video.videoHeight) {
    console.error("Video not ready yet");
    return null;
  }

  const canvas = document.createElement("canvas");
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;

  const ctx = canvas.getContext("2d");
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

  return canvas.toDataURL("image/jpeg", 0.8);
}

//starts live video feed from phone
button.addEventListener('click', async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "environment" }
      });
  
      video.srcObject = stream;
      videoTrack = stream.getVideoTracks()[0];
  
      video.style.display = 'block';
      placeholder.style.display = 'none';
      overlay.style.display = 'block';

      if(ttsEnabled){
        speak("Camera is now on");
      }
  
    } catch (err) {
      console.error(err);
      alert('Camera access denied or not available.');
      if(ttsEnabled){
        speak("Camera access denied or not available");
      }
    }
  });

  settings.addEventListener('click', () =>{
    toggleSettings();

    if (ttsEnabled) {
      const isOpen = settingsPanel.style.display === 'block';
      speak(isOpen ? 'Settings are now open.' : 'Settings are now closed.');
    }

  });

//flash for when user takes photo
video.addEventListener('click', () => {
  flash.style.transition = 'none';
  flash.style.opacity = 0;

  flash.offsetHeight;

  flash.style.transition = 'opacity 0.1s ease-in-out';
  flash.style.opacity = 0.8;

  setTimeout(() => {
    flash.style.opacity = 0;
  }, 100);

  const imageData = captureFrameAsBase64();

    if(ttsEnabled){
      speak("Photo Taken");
    }

    setTimeout(() => {
      flash.style.opacity = 0;
    }, 100);
  if (!imageData) {
    alert("Could not capture image.");
    return;
  }

  if (!socket || socket.readyState !== WebSocket.OPEN) {
    alert("WebSocket is not connected.");
    return;
  }

  socket.send(JSON.stringify({
    type: "image",
    image: imageData,
    timestamp: Date.now()
  }));

  console.log("Image sent to backend");
});

// Detect double tap (mobile) + double click (desktop) for settings
mainView.addEventListener('click', () => {
  const now = Date.now();
  const timeBetween = now - lastTap;

  if (timeBetween < 300 && timeBetween > 0) {
    toggleSettings();

    if (ttsEnabled) {
      const isOpen = settingsPanel.style.display === 'block';
      speak(isOpen ? 'Settings are now open.' : 'Settings are now closed.');
    }

  }

  lastTap = now;
});

// Function of actually speaking
function speak(text) {
  if (!ttsEnabled) return;

  const utterance = new SpeechSynthesisUtterance(text);

  const length = text.length;

  let soundLevel;

  if (length < 20) {
    soundLevel = 1.2;
    utterance.rate = 1.15;
    utterance.pitch = 1.2;
  } 
  else if (length < 80) {
    soundLevel = 1.0;
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
  } 
  else {
    soundLevel = 0.8;
    utterance.rate = 0.85;
    utterance.pitch = 0.9;
  }

  utterance.volume = Math.max(0, Math.min(1, soundLevel * ttsVolume));

  speechSynthesis.speak(utterance);
}

//shows and closes settings
function toggleSettings() {
  const isOpen = settingsPanel.style.display === 'block';
  settingsPanel.style.display = isOpen ? 'none' : 'block';
}

textSizeArea.addEventListener('click', (e) => {
  const rect = textSizeArea.getBoundingClientRect();
  const x = e.clientX - rect.left;

  if (x < rect.width / 2) {
    textSize = Math.max(0.5, +(textSize - 0.1).toFixed(2));
  } else {
    textSize = Math.min(2, +(textSize + 0.1).toFixed(2));
  }

  placeholder.style.fontSize = textSize + "rem";

  if (ttsEnabled) {
    speak(`Font size is now set to ${Math.round(textSize * 100)}%`);
  }

});

ttsVolumeArea.addEventListener('click', (e) => {
    if (!ttsEnabled) return;
  
    const rect = ttsVolumeArea.getBoundingClientRect();
    const x = e.clientX - rect.left;
  
    if (x < rect.width / 2) {
      ttsVolume = Math.max(0, +(ttsVolume - 0.1).toFixed(2));
    } else {
      ttsVolume = Math.min(1, +(ttsVolume + 0.1).toFixed(2));
    }

    if (ttsEnabled) {
      speak(`Voice volume is now set to ${Math.round(ttsVolume * 100)}%`);
    }
  
});

// checks to see if text to speech is enabled
ttsToggleRow.addEventListener('click', () => {
    ttsEnabled = !ttsEnabled;
    ttsToggle.checked = ttsEnabled;
  
    ttsVolumeArea.classList.toggle('disabled', !ttsEnabled);

    if (ttsEnabled) {
      speak('Voice output is now turned on.');
    } else {
      ttsEnabled = !ttsEnabled;
      speak('Voice output is now turned off.');
      ttsEnabled = !ttsEnabled;
    }
});

// Close button
closeSettings.addEventListener('click', () => {
    settingsPanel.style.display = 'none';
    if (ttsEnabled) {
      speak('Settings Closed');
    } 
});

// Connect WebSocket on load
window.addEventListener("load", () => {
  connectWebSocket();
});
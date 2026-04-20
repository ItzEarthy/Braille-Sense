const button = document.getElementById('enable-camera');
const video = document.getElementById('camera-feed');
const placeholder = document.getElementById('camera-placeholder');
const overlay = document.getElementById('camera-overlay');
const mainView = document.getElementById('main-view');
const flash = document.getElementById('flash-overlay');

let socket = null;

// Text-to-speech helper
function speak(text) {
  const utterance = new SpeechSynthesisUtterance(text);
  window.speechSynthesis.cancel();
  window.speechSynthesis.speak(utterance);
}

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
      } else if (data.type === "connection") {
        console.log(data.message);
      } else if (data.type === "error") {
        console.error("Server error:", data.message);
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

// Capture current video frame as base64 image
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

// Enable camera
button.addEventListener('click', async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: "environment" }
    });

    video.srcObject = stream;

    // Show camera, hide default placeholder
    video.style.display = 'block';
    placeholder.style.display = 'none';
    overlay.style.display = 'block';

  } catch (err) {
    console.error(err);
    alert('Camera access denied or not available.');
  }
});

// When user taps video: flash + capture + send image
video.addEventListener('click', () => {
  // Flash effect
  flash.style.transition = 'none';
  flash.style.opacity = 0;

  flash.offsetHeight;

  flash.style.transition = 'opacity 0.1s ease-in-out';
  flash.style.opacity = 0.8;

  setTimeout(() => {
    flash.style.opacity = 0;
  }, 100);

  // Capture image
  const imageData = captureFrameAsBase64();

  if (!imageData) {
    alert("Could not capture image.");
    return;
  }

  // Check WebSocket connection
  if (!socket || socket.readyState !== WebSocket.OPEN) {
    alert("WebSocket is not connected.");
    return;
  }

  // Send image to backend
  socket.send(
    JSON.stringify({
      type: "image",
      image: imageData,
      timestamp: Date.now()
    })
  );

  console.log("Image sent to backend");
});

// Connect on page load
window.addEventListener("load", () => {
  connectWebSocket();
});
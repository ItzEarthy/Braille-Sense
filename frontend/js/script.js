const button = document.getElementById('enable-camera');
const video = document.getElementById('camera-feed');
const placeholder = document.getElementById('camera-placeholder');
const overlay = document.getElementById('camera-overlay');
const mainView = document.getElementById('main-view');
const flash = document.getElementById('flash-overlay');

let socket = null;
let isFrozen = false;
const canvas = document.getElementById('freeze-frame');
const ctx = canvas.getContext('2d');

button.addEventListener('click', async () => {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "environment" }
    });

    video.srcObject = stream;

    // Show camera, hide default
    video.style.display = 'block';
    placeholder.style.display = 'none';
    overlay.style.display = 'block';

    } catch (err) {
        console.error(err);
        alert('Camera access denied or not available.');
    }
});

//flash for when user takes photo and freeze frame
video.addEventListener('click', () => {
  // If frozen → unfreeze
  if (isFrozen) {
    canvas.style.display = 'none';
    video.style.display = 'block';
    isFrozen = false;
    console.log('Camera resumed');
    return;
  }

  // Capture frame
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

  // Show frozen frame
  canvas.style.display = 'block';
  video.style.display = 'none';

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
    const base64Image = canvas.toDataURL('image/png');

    socket.send(JSON.stringify({
      type: 'test_image',
      image: base64Image
    }));

    console.log('Image sent to backend');
  } else {
    console.log('WebSocket not connected');
  }

  isFrozen = true;
});

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
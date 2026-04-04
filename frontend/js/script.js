const button = document.getElementById('enable-camera');
const video = document.getElementById('camera-feed');
const placeholder = document.getElementById('camera-placeholder');

button.addEventListener('click', async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: "environment" }
    });

    video.srcObject = stream;

    // Show camera, hide default
    video.style.display = 'block';
    placeholder.style.display = 'none';

  } catch (err) {
    console.error(err);
    alert('Camera access denied or not available.');
  }
});
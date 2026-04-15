const button = document.getElementById('enable-camera');
const video = document.getElementById('camera-feed');
const placeholder = document.getElementById('camera-placeholder');
const overlay = document.getElementById('camera-overlay');
const mainView = document.getElementById('main-view');
const flash = document.getElementById('flash-overlay');

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
});
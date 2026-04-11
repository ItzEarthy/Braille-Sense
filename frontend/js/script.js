//HTHML Elements
const button = document.getElementById('enable-camera');
const video = document.getElementById('camera-feed');
const placeholder = document.getElementById('camera-placeholder');
const overlay = document.getElementById('camera-overlay');
const mainView = document.getElementById('main-view');
const flash = document.getElementById('flash-overlay');
const settingsPanel = document.getElementById('settings-panel');
const closeSettings = document.getElementById('close-settings');
const soundSlider = document.getElementById('sound-volume');
const flashlightToggle = document.getElementById('flashlight-toggle');
const ttsSlider = document.getElementById('tts-volume');

//Variables
let lastTap = 0;
let soundVolume = 1;
let ttsVolume = 1;

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

// Detect double tap (mobile) + double click (desktop)
mainView.addEventListener('click', () => {
  const now = Date.now();
  const timeBetween = now - lastTap;

  if (timeBetween < 300 && timeBetween > 0) {
    // Double tap detected
    toggleSettings();
  }

  lastTap = now;
});

function toggleSettings() {
  if (settingsPanel.style.display === 'none' || settingsPanel.style.display === '') {
    settingsPanel.style.display = 'block';
  } else {
    settingsPanel.style.display = 'none';
  }
}

soundSlider.addEventListener('input', () => {
  soundVolume = parseFloat(soundSlider.value);
  console.log('Sound volume:', soundVolume);
});

ttsSlider.addEventListener('input', () => {
  ttsVolume = parseFloat(ttsSlider.value);
  console.log('TTS volume:', ttsVolume);
});

function speak(text) {
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.volume = ttsVolume;
    speechSynthesis.speak(utterance);
  }

  let videoTrack = null;

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

  } catch (err) {
    console.error(err);
    alert('Camera access denied or not available.');
  }
});

flashlightToggle.addEventListener('change', async () => {
    if (!videoTrack) return;
  
    const capabilities = videoTrack.getCapabilities();
  
    if (!capabilities.torch) {
      alert('Flashlight not supported on this device');
      return;
    }
  
    try {
      await videoTrack.applyConstraints({
        advanced: [{ torch: flashlightToggle.checked }]
      });
    } catch (err) {
      console.error('Torch error:', err);
    }
  });


// Close button
closeSettings.addEventListener('click', () => {
    settingsPanel.style.display = 'none';
});

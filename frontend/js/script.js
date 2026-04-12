//HTHML Elements
const button = document.getElementById('enable-camera');
const video = document.getElementById('camera-feed');
const placeholder = document.getElementById('camera-placeholder');
const overlay = document.getElementById('camera-overlay');
const mainView = document.getElementById('main-view');
const flash = document.getElementById('flash-overlay');
const settingsPanel = document.getElementById('settings-panel');
const closeSettings = document.getElementById('close-settings');
const ttsSlider = document.getElementById('tts-volume');
const ttsToggle = document.getElementById('tts-toggle');

//Variables
let lastTap = 0;
let videoTrack = null;
let soundLevel = 1;
let ttsVolume = 1;
let ttsEnabled = false;

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

// Detect double tap (mobile) + double click (desktop) for settings
mainView.addEventListener('click', () => {
  const now = Date.now();
  const timeBetween = now - lastTap;

  if (timeBetween < 300 && timeBetween > 0) {
    toggleSettings();
  }

  lastTap = now;
});

// When called, shows settings page
function toggleSettings() {
  if (settingsPanel.style.display === 'none' || settingsPanel.style.display === '') {
    settingsPanel.style.display = 'block';
  } else {
    settingsPanel.style.display = 'none';
  }
}

// Shows volume in console log
ttsSlider.addEventListener('input', () => {
  ttsVolume = parseFloat(ttsSlider.value);
  console.log('TTS volume:', ttsVolume);
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

// Toggle whether or not TTS should be used
ttsToggle.addEventListener('change', () => {
    ttsEnabled = ttsToggle.checked;
  
    ttsSlider.disabled = !ttsEnabled;
  
    ttsSlider.style.opacity = ttsEnabled ? "1" : "0.4";
  });

  function toggleSettings() {
    const isOpen = settingsPanel.style.display === 'block';
    settingsPanel.style.display = isOpen ? 'none' : 'block';
  }

// Close button
closeSettings.addEventListener('click', () => {
    settingsPanel.style.display = 'none';
});

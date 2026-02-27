/* ================================================
   Chat&TalkGPT — app.js
   ================================================ */

/* ================================================
   THEME MANAGEMENT 
   ================================================ */

const ThemeManager = {
  // Theme state
  currentTheme: 'dark',

  // Initialize theme on page load
  init() {
    // First check localStorage
    const savedTheme = localStorage.getItem('theme');

    if (savedTheme) {
      this.currentTheme = savedTheme;
    } else {
      // Check system preference
      if (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches) {
        this.currentTheme = 'light';
      }
    }

    this.applyTheme();
    this.addSystemThemeListener();
  },

  // Apply theme to the document
  applyTheme() {
    if (this.currentTheme === 'light') {
      document.body.classList.add('theme-light');
      document.body.classList.remove('theme-dark');
    } else {
      document.body.classList.remove('theme-light');
      document.body.classList.add('theme-dark');
    }
  },

  // Toggle between light and dark themes
  toggle() {
    this.currentTheme = this.currentTheme === 'dark' ? 'light' : 'dark';
    this.applyTheme();
    this.saveTheme();
    this.syncWithBackend();
  },

  // Save theme preference to localStorage
  saveTheme() {
    localStorage.setItem('theme', this.currentTheme);
  },

  // Sync theme with backend
  async syncWithBackend() {
    try {
      const response = await fetch('/api/user/theme', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ theme: this.currentTheme })
      });

      if (!response.ok) {
        console.warn('Failed to sync theme with backend');
      }
    } catch (error) {
      // Backend might not be running, ignore error
      console.debug('Backend not available for theme sync');
    }
  },

  // Load theme from backend
  async loadFromBackend() {
    try {
      const response = await fetch('/api/user/theme');
      if (response.ok) {
        const data = await response.json();
        if (data.theme && data.theme !== 'system') {
          this.currentTheme = data.theme;
          this.applyTheme();
          this.saveTheme();
        }
      }
    } catch (error) {
      console.debug('Could not load theme from backend');
    }
  },

  // Listen for system theme changes
  addSystemThemeListener() {
    if (window.matchMedia) {
      window.matchMedia('(prefers-color-scheme: light)').addEventListener('change', (e) => {
        // Only apply if user hasn't set a preference
        if (!localStorage.getItem('theme')) {
          this.currentTheme = e.matches ? 'light' : 'dark';
          this.applyTheme();
        }
      });
    }
  }
};

/* ═══════════════════════════════════════════════
   VOICE MANAGER - TTS Voice Selection
   ═══════════════════════════════════════════════ */

const VoiceManager = {
  // Voice state
  currentVoice: 'edge_en_us_guy',
  currentLanguage: 'en',
  voices: [],
  languages: [],
  providers: [],
  settings: {
    speed: 1.0,
    pitch: 1.0
  },
  isPlaying: false,
  audioElement: null,

  // Initialize voice manager
  async init() {
    // Load voice preferences from localStorage
    this.loadFromLocalStorage();

    // Try to load from backend
    await this.loadFromBackend();

    // Create voice button in navbar
    this.createVoiceButton();

    console.log('VoiceManager initialized');
  },

  // Load from localStorage
  loadFromLocalStorage() {
    const savedVoice = localStorage.getItem('preferred_voice');
    const savedLanguage = localStorage.getItem('preferred_language');
    const savedSpeed = localStorage.getItem('voice_speed');
    const savedPitch = localStorage.getItem('voice_pitch');

    if (savedVoice) this.currentVoice = savedVoice;
    if (savedLanguage) this.currentLanguage = savedLanguage;
    if (savedSpeed) this.settings.speed = parseFloat(savedSpeed);
    if (savedPitch) this.settings.pitch = parseFloat(savedPitch);
  },

  // Save to localStorage
  saveToLocalStorage() {
    localStorage.setItem('preferred_voice', this.currentVoice);
    localStorage.setItem('preferred_language', this.currentLanguage);
    localStorage.setItem('voice_speed', this.settings.speed);
    localStorage.setItem('voice_pitch', this.settings.pitch);
  },

  // Load from backend
  async loadFromBackend() {
    try {
      // Get available voices
      const voicesResponse = await fetch('/api/tts/voices');
      if (voicesResponse.ok) {
        const voicesData = await voicesResponse.json();
        this.voices = voicesData.voices || [];
      }

      // Get available languages
      const langResponse = await fetch('/api/tts/voices/languages');
      if (langResponse.ok) {
        const langData = await langResponse.json();
        this.languages = langData.languages || [];
      }

      // Get providers
      const provResponse = await fetch('/api/tts/voices/providers');
      if (provResponse.ok) {
        const provData = await provResponse.json();
        this.providers = provData.providers || [];
      }

      // Get default voice
      const defaultResponse = await fetch('/api/tts/voices/default');
      if (defaultResponse.ok) {
        const defaultData = await defaultResponse.json();
        if (defaultData.voice_id) {
          this.currentVoice = defaultData.voice_id;
        }
      }

      // Get voice settings
      const settingsResponse = await fetch('/api/tts/settings');
      if (settingsResponse.ok) {
        const settingsData = await settingsResponse.json();
        this.settings = {
          speed: settingsData.speed || 1.0,
          pitch: settingsData.pitch || 1.0
        };
      }
    } catch (error) {
      console.debug('Could not load voice settings from backend');
    }
  },

  // Create voice button in navbar
  createVoiceButton() {
    const navLinks = document.getElementById('nav-links');
    if (!navLinks) return;

    // Check if voice button already exists
    if (document.getElementById('voiceSettingsBtn')) return;

    const voiceBtn = document.createElement('button');
    voiceBtn.className = 'voice-settings-btn';
    voiceBtn.id = 'voiceSettingsBtn';
    voiceBtn.setAttribute('aria-label', 'Voice settings');
    voiceBtn.innerHTML = `
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
        <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
        <line x1="12" y1="19" x2="12" y2="23"></line>
        <line x1="8" y1="23" x2="16" y2="23"></line>
      </svg>
    `;

    voiceBtn.addEventListener('click', () => {
      this.showVoiceModal();
    });

    // Insert after theme toggle
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
      navLinks.insertBefore(voiceBtn, themeToggle.nextSibling);
    } else {
      navLinks.insertBefore(voiceBtn, navLinks.firstChild);
    }
  },

  // Show voice settings modal
  showVoiceModal() {
    // Remove existing modal if any
    const existingModal = document.getElementById('voiceModal');
    if (existingModal) {
      existingModal.remove();
    }

    // Create modal
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.id = 'voiceModal';
    modal.innerHTML = `
      <div class="modal-content voice-modal-content">
        <div class="modal-header">
          <h2>Voice Settings</h2>
          <button class="close-modal">&times;</button>
        </div>
        <div class="modal-body">
          <div class="voice-section">
            <h3>Select Voice</h3>
            <div class="voice-filters">
              <select id="voiceLanguageFilter" class="voice-filter">
                <option value="">All Languages</option>
                ${this.languages.map(l => `<option value="${l.code}">${l.name}</option>`).join('')}
              </select>
              <select id="voiceProviderFilter" class="voice-filter">
                <option value="">All Providers</option>
                ${this.providers.map(p => `<option value="${p.name}">${p.display_name}</option>`).join('')}
              </select>
              <select id="voiceGenderFilter" class="voice-filter">
                <option value="">All Genders</option>
                <option value="male">Male</option>
                <option value="female">Female</option>
              </select>
            </div>
            <div class="voice-list" id="voiceList">
              ${this.renderVoiceList(this.voices)}
            </div>
          </div>
          
          <div class="voice-section">
            <h3>Voice Settings</h3>
            <div class="voice-settings">
              <div class="setting-item">
                <label for="speedSlider">Speed: <span id="speedValue">${this.settings.speed.toFixed(1)}</span></label>
                <input type="range" id="speedSlider" min="0.5" max="2.0" step="0.1" value="${this.settings.speed}">
              </div>
              <div class="setting-item">
                <label for="pitchSlider">Pitch: <span id="pitchValue">${this.settings.pitch.toFixed(1)}</span></label>
                <input type="range" id="pitchSlider" min="0.5" max="2.0" step="0.1" value="${this.settings.pitch}">
              </div>
            </div>
          </div>
          
          <div class="voice-section">
            <h3>Quick Voices</h3>
            <div class="quick-voices">
              <button class="quick-voice-btn" data-voice="edge_en_us_guy" data-context="professional">
                <span class="voice-icon">👨‍💼</span>
                <span>Professional</span>
              </button>
              <button class="quick-voice-btn" data-voice="edge_en_us_jenny" data-context="friendly">
                <span class="voice-icon">👩</span>
                <span>Friendly</span>
              </button>
              <button class="quick-voice-btn" data-voice="edge_hi_madhur" data-context="hindi">
                <span class="voice-icon">🗣️</span>
                <span>Hindi</span>
              </button>
              <button class="quick-voice-btn" data-voice="edge_ne_sagar" data-context="nepali">
                <span class="voice-icon">🇳🇵</span>
                <span>Nepali</span>
              </button>
            </div>
          </div>
          
          <div class="voice-section">
            <h3>Preview</h3>
            <button id="previewVoiceBtn" class="preview-btn">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                <polygon points="5 3 19 12 5 21 5 3"></polygon>
              </svg>
              Preview Voice
            </button>
          </div>
        </div>
        <div class="modal-footer">
          <button id="saveVoiceSettings" class="btn-primary">Save Settings</button>
        </div>
      </div>
    `;

    document.body.appendChild(modal);

    // Add event listeners
    this.setupModalEventListeners(modal);

    // Show modal
    setTimeout(() => {
      modal.classList.add('show');
    }, 10);
  },

  // Render voice list
  renderVoiceList(voices) {
    return voices.map(voice => `
      <div class="voice-item ${voice.voice_id === this.currentVoice ? 'selected' : ''}" data-voice-id="${voice.voice_id}">
        <div class="voice-info">
          <span class="voice-name">${voice.name}</span>
          <span class="voice-details">${voice.language.toUpperCase()} • ${voice.gender} • ${voice.provider}</span>
        </div>
        <div class="voice-tags">
          ${voice.tags.slice(0, 3).map(tag => `<span class="voice-tag">${tag}</span>`).join('')}
        </div>
        ${voice.quality_rating ? `<div class="voice-rating">${'★'.repeat(voice.quality_rating)}</div>` : ''}
      </div>
    `).join('');
  },

  // Setup modal event listeners
  setupModalEventListeners(modal) {
    // Close modal
    const closeBtn = modal.querySelector('.close-modal');
    closeBtn.addEventListener('click', () => {
      modal.classList.remove('show');
      setTimeout(() => modal.remove(), 300);
    });

    // Close on outside click
    modal.addEventListener('click', (e) => {
      if (e.target === modal) {
        modal.classList.remove('show');
        setTimeout(() => modal.remove(), 300);
      }
    });

    // Voice selection
    const voiceItems = modal.querySelectorAll('.voice-item');
    voiceItems.forEach(item => {
      item.addEventListener('click', () => {
        voiceItems.forEach(v => v.classList.remove('selected'));
        item.classList.add('selected');
        this.currentVoice = item.dataset.voiceId;
      });
    });

    // Filters
    const langFilter = document.getElementById('voiceLanguageFilter');
    const providerFilter = document.getElementById('voiceProviderFilter');
    const genderFilter = document.getElementById('voiceGenderFilter');

    const applyFilters = () => {
      const lang = langFilter.value;
      const provider = providerFilter.value;
      const gender = genderFilter.value;

      let filtered = this.voices;
      if (lang) filtered = filtered.filter(v => v.language === lang);
      if (provider) filtered = filtered.filter(v => v.provider === provider);
      if (gender) filtered = filtered.filter(v => v.gender === gender);

      const voiceList = document.getElementById('voiceList');
      voiceList.innerHTML = this.renderVoiceList(filtered);

      // Re-add click listeners
      const newVoiceItems = voiceList.querySelectorAll('.voice-item');
      newVoiceItems.forEach(item => {
        item.addEventListener('click', () => {
          newVoiceItems.forEach(v => v.classList.remove('selected'));
          item.classList.add('selected');
          this.currentVoice = item.dataset.voiceId;
        });
      });
    };

    langFilter.addEventListener('change', applyFilters);
    providerFilter.addEventListener('change', applyFilters);
    genderFilter.addEventListener('change', applyFilters);

    // Speed slider
    const speedSlider = document.getElementById('speedSlider');
    const speedValue = document.getElementById('speedValue');
    speedSlider.addEventListener('input', () => {
      speedValue.textContent = parseFloat(speedSlider.value).toFixed(1);
      this.settings.speed = parseFloat(speedSlider.value);
    });

    // Pitch slider
    const pitchSlider = document.getElementById('pitchSlider');
    const pitchValue = document.getElementById('pitchValue');
    pitchSlider.addEventListener('input', () => {
      pitchValue.textContent = parseFloat(pitchSlider.value).toFixed(1);
      this.settings.pitch = parseFloat(pitchSlider.value);
    });

    // Quick voice buttons
    const quickVoiceBtns = modal.querySelectorAll('.quick-voice-btn');
    quickVoiceBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        this.currentVoice = btn.dataset.voice;

        // Update selection visual
        const voiceItems = modal.querySelectorAll('.voice-item');
        voiceItems.forEach(v => {
          v.classList.toggle('selected', v.dataset.voiceId === this.currentVoice);
        });
      });
    });

    // Preview button
    const previewBtn = document.getElementById('previewVoiceBtn');
    previewBtn.addEventListener('click', () => {
      this.previewVoice();
    });

    // Save button
    const saveBtn = document.getElementById('saveVoiceSettings');
    saveBtn.addEventListener('click', async () => {
      await this.saveSettings();
      modal.classList.remove('show');
      setTimeout(() => modal.remove(), 300);
    });
  },

  // Preview voice
  async previewVoice() {
    const previewText = "Hello! This is a preview of my voice. You can adjust the settings and hear how I sound.";

    try {
      const response = await fetch('/api/tts/convert', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: previewText,
          voice_id: this.currentVoice,
          language: this.currentLanguage,
          speed: this.settings.speed,
          pitch: this.settings.pitch
        })
      });

      if (response.ok) {
        const data = await response.json();
        if (data.audio) {
          // Stop any playing audio
          if (this.audioElement) {
            this.audioElement.pause();
          }

          // Play audio
          this.audioElement = new Audio('data:audio/mp3;base64,' + data.audio);
          this.audioElement.play();
          this.isPlaying = true;

          this.audioElement.onended = () => {
            this.isPlaying = false;
          };
        }
      }
    } catch (error) {
      console.error('Error previewing voice:', error);
    }
  },

  // Save settings
  async saveSettings() {
    // Save to localStorage
    this.saveToLocalStorage();

    // Save to backend
    try {
      await fetch('/api/tts/voices/default', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ voice_id: this.currentVoice })
      });

      await fetch('/api/tts/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          speed: this.settings.speed,
          pitch: this.settings.pitch
        })
      });
    } catch (error) {
      console.debug('Could not save voice settings to backend');
    }
  },

  // Quick voice switch
  async quickSwitch(voiceId) {
    this.currentVoice = voiceId;
    this.saveToLocalStorage();

    try {
      await fetch('/api/tts/voices/default', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ voice_id: voiceId })
      });
    } catch (error) {
      console.debug('Could not save voice to backend');
    }
  },

  // Speak text using TTS
  async speak(text) {
    try {
      const response = await fetch('/api/tts/convert', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: text,
          voice_id: this.currentVoice,
          language: this.currentLanguage,
          speed: this.settings.speed,
          pitch: this.settings.pitch
        })
      });

      if (response.ok) {
        const data = await response.json();
        if (data.audio) {
          // Stop any playing audio
          if (this.audioElement) {
            this.audioElement.pause();
          }

          // Play audio
          this.audioElement = new Audio('data:audio/mp3;base64,' + data.audio);
          this.audioElement.play();
          this.isPlaying = true;

          this.audioElement.onended = () => {
            this.isPlaying = false;
          };

          return true;
        }
      }
      return false;
    } catch (error) {
      console.error('Error speaking text:', error);
      return false;
    }
  },

  // Stop speaking
  stopSpeaking() {
    if (this.audioElement) {
      this.audioElement.pause();
      this.audioElement = null;
      this.isPlaying = false;
    }
  }
};

// Initialize theme when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  ThemeManager.init();
  VoiceManager.init();

  // Create theme toggle button
  ThemeManager.createToggleButton();
});

// Create and append theme toggle button
ThemeManager.createToggleButton = function () {
  const navLinks = document.getElementById('nav-links');
  if (!navLinks) return;

  // Create the toggle button
  const toggleBtn = document.createElement('button');
  toggleBtn.className = 'theme-toggle';
  toggleBtn.id = 'themeToggle';
  toggleBtn.setAttribute('aria-label', 'Toggle theme');
  toggleBtn.innerHTML = `
        <svg class="icon-sun" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="5"></circle>
            <line x1="12" y1="1" x2="12" y2="3"></line>
            <line x1="12" y1="21" x2="12" y2="23"></line>
            <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
            <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
            <line x1="1" y1="12" x2="3" y2="12"></line>
            <line x1="21" y1="12" x2="23" y2="12"></line>
            <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
            <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
        </svg>
        <svg class="icon-moon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
        </svg>
    `;

  // Add click event
  toggleBtn.addEventListener('click', () => {
    this.toggle();
  });

  // Insert before the first child of nav-links
  navLinks.insertBefore(toggleBtn, navLinks.firstChild);
};

/* ================================================
   Navbar scroll shadow
   ================================================ */

const navbar = document.getElementById('navbar');
window.addEventListener('scroll', () => {
  navbar.classList.toggle('scrolled', window.scrollY > 10);
});

/* ── Hamburger menu ── */
const hamburger = document.getElementById('hamburger');
const navLinks = document.getElementById('navLinks');

hamburger.addEventListener('click', () => {
  hamburger.classList.toggle('open');
  navLinks.classList.toggle('open');
});
navLinks.querySelectorAll('a').forEach(link => {
  link.addEventListener('click', () => {
    hamburger.classList.remove('open');
    navLinks.classList.remove('open');
  });
});

/* ── Feature cards animate-in ── */
const cards = document.querySelectorAll('.card');
const cardObserver = new IntersectionObserver((entries) => {
  entries.forEach((entry, i) => {
    if (entry.isIntersecting) {
      setTimeout(() => entry.target.classList.add('visible'), i * 120);
      cardObserver.unobserve(entry.target);
    }
  });
}, { threshold: 0.15 });
cards.forEach(card => cardObserver.observe(card));

/* ══════════════════════════════════════════════
   WEATHER WIDGET  (Open-Meteo + Nominatim — free, no key needed)
   ══════════════════════════════════════════════ */

const cityInput = document.getElementById('cityInput');
const weatherData = document.getElementById('weatherData');
const weatherLoad = document.getElementById('weatherLoading');
const weatherErr = document.getElementById('weatherError');
const mapFrame = document.getElementById('mapFrame');

function showState(state) {
  weatherLoad.style.display = state === 'loading' ? 'flex' : 'none';
  weatherData.style.display = state === 'data' ? 'block' : 'none';
  weatherErr.style.display = state === 'error' ? 'block' : 'none';
}

function updateMap(lat, lon) {
  const delta = 0.15;
  const bbox = `${lon - delta},${lat - delta},${lon + delta},${lat + delta}`;
  mapFrame.src = `https://www.openstreetmap.org/export/embed.html?bbox=${bbox}&layer=mapnik&marker=${lat},${lon}`;
}

function weatherAdvice(code, temp) {
  if (code >= 95) return '⛈ Thunderstorms — stay indoors and avoid open spaces.';
  if (code >= 80) return '🌧 Showers expected — keep an umbrella handy.';
  if (code >= 71) return '❄️ Snowy conditions — dress warmly and drive carefully.';
  if (code >= 61) return '☔ Rain today — grab an umbrella before heading out!';
  if (code >= 51) return '🌦 Light drizzle — a light jacket will do.';
  if (code >= 45) return '🌫 Poor visibility — take extra care on the roads.';
  if (code === 0 || code === 1) return temp > 30 ? '☀️ Clear and hot — stay hydrated!' : '☀️ Clear skies — great day to be outside!';
  return '⛅ Partly cloudy — comfortable conditions overall.';
}

function windDir(deg) {
  const dirs = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'];
  return dirs[Math.round(deg / 45) % 8];
}

function wmoToDesc(code) {
  const map = {
    0: { 'desc': 'Clear sky', 'emoji': '☀️' }, 1: { 'desc': 'Mainly clear', 'emoji': '🌤' },
    2: { 'desc': 'Partly cloudy', 'emoji': '⛅' }, 3: { 'desc': 'Overcast', 'emoji': '☁️' },
    45: { 'desc': 'Foggy', 'emoji': '🌫' }, 48: { 'desc': 'Icy fog', 'emoji': '🌫' },
    51: { 'desc': 'Light drizzle', 'emoji': '🌦' }, 53: { 'desc': 'Moderate drizzle', 'emoji': '🌦' },
    55: { 'desc': 'Dense drizzle', 'emoji': '🌧' }, 61: { 'desc': 'Slight rain', 'emoji': '🌧' },
    63: { 'desc': 'Moderate rain', 'emoji': '🌧' }, 65: { 'desc': 'Heavy rain', 'emoji': '⛈' },
    71: { 'desc': 'Slight snow', 'emoji': '🌨' }, 73: { 'desc': 'Moderate snow', 'emoji': '❄️' },
    75: { 'desc': 'Heavy snow', 'emoji': '❄️' }, 77: { 'desc': 'Snow grains', 'emoji': '🌨' },
    80: { 'desc': 'Slight showers', 'emoji': '🌦' }, 81: { 'desc': 'Moderate showers', 'emoji': '🌧' },
    82: { 'desc': 'Violent showers', 'emoji': '⛈' }, 85: { 'desc': 'Slight snow showers', 'emoji': '🌨' },
    86: { 'desc': 'Heavy snow showers', 'emoji': '❄️' }, 95: { 'desc': 'Thunderstorm', 'emoji': '⛈' },
    96: { 'desc': 'Thunderstorm + hail', 'emoji': '⛈' }, 99: { 'desc': 'Thunderstorm + hail', 'emoji': '⛈' },
  };
  return map[code] || { desc: 'Unknown conditions', emoji: '🌡' };
}

async function fetchWeatherByCoords(lat, lon, label) {
  showState('loading');
  const url = `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&current_weather=true&hourly=relativehumidity_2m,apparent_temperature,visibility&timezone=auto&forecast_days=1`;
  try {
    const res = await fetch(url);
    if (!res.ok) throw new Error('fail');
    const json = await res.json();
    const cw = json.current_weather;
    const temp = Math.round(cw.temperature);
    const wind = Math.round(cw.windspeed);
    const wdir = windDir(cw.winddirection);
    const code = cw.weathercode;
    const humidity = json.hourly?.relativehumidity_2m?.[0] ?? '—';
    const feelsLike = json.hourly?.apparent_temperature?.[0] != null ? Math.round(json.hourly.apparent_temperature[0]) + '°C' : '—';
    const vis = json.hourly?.visibility?.[0] != null ? (json.hourly.visibility[0] / 1000).toFixed(1) + ' km' : '—';
    const { desc, emoji } = wmoToDesc(code);
    const advice = weatherAdvice(code, temp);

    weatherData.innerHTML = `
      <div class="weather-top">
        <div>
          <div class="weather-location-name">📍 ${label}</div>
          <div class="weather-desc">${emoji} ${desc}</div>
        </div>
        <div class="weather-temp-block">
          <span class="weather-temp">${temp}</span>
          <span class="weather-temp-unit">°C</span>
        </div>
      </div>
      <div class="weather-advice">${advice}</div>
      <div class="weather-grid">
        <div class="weather-stat"><span class="ws-icon">💧</span><span class="ws-label">Humidity</span><span class="ws-value">${humidity}%</span></div>
        <div class="weather-stat"><span class="ws-icon">💨</span><span class="ws-label">Wind</span><span class="ws-value">${wind} km/h ${wdir}</span></div>
        <div class="weather-stat"><span class="ws-icon">🌡</span><span class="ws-label">Feels Like</span><span class="ws-value">${feelsLike}</span></div>
        <div class="weather-stat"><span class="ws-icon">👁</span><span class="ws-label">Visibility</span><span class="ws-value">${vis}</span></div>
        <div class="weather-stat"><span class="ws-icon">🌐</span><span class="ws-label">Latitude</span><span class="ws-value">${lat.toFixed(3)}</span></div>
        <div class="weather-stat"><span class="ws-icon">🌐</span><span class="ws-label">Longitude</span><span class="ws-value">${lon.toFixed(3)}</span></div>
      </div>
      <a class="weather-map-link" href="https://www.openstreetmap.org/?mlat=${lat}&mlon=${lon}#map=12/${lat}/${lon}" target="_blank" rel="noopener">🗺 Open Full Map ↗</a>
    `;
    updateMap(lat, lon);
    showState('data');
  } catch (e) {
    showState('error');
    weatherErr.textContent = '⚠️ Could not fetch weather. Please check your connection or try another city.';
  }
}

async function fetchWeather() {
  const city = cityInput.value.trim();
  if (!city) { cityInput.focus(); return; }
  showState('loading');
  try {
    const geoRes = await fetch(`https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(city)}&format=json&limit=1`, { headers: { 'Accept-Language': 'en' } });
    const geoData = await geoRes.json();
    if (!geoData.length) {
      showState('error');
      weatherErr.textContent = `😕 City "${city}" not found. Try a different spelling.`;
      return;
    }
    const { lat, lon, display_name } = geoData[0];
    const shortLabel = display_name.split(',').slice(0, 2).join(', ');
    await fetchWeatherByCoords(parseFloat(lat), parseFloat(lon), shortLabel);
  } catch (e) {
    showState('error');
    weatherErr.textContent = '⚠️ Geocoding failed. Please check your internet connection.';
  }
}

function useMyLocation() {
  if (!navigator.geolocation) { alert('Geolocation not supported.'); return; }
  showState('loading');
  navigator.geolocation.getCurrentPosition(async (pos) => {
    const { latitude: lat, longitude: lon } = pos.coords;
    try {
      const r = await fetch(`https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lon}&format=json`);
      const d = await r.json();
      const label = d.address?.city || d.address?.town || d.address?.village || 'My Location';
      await fetchWeatherByCoords(lat, lon, label);
    } catch { await fetchWeatherByCoords(lat, lon, 'My Location'); }
  }, () => {
    showState('error');
    weatherErr.textContent = '📍 Location access denied. Please allow location or search manually.';
  });
}

/* ── Auto-load Kathmandu on start ── */
window.addEventListener('DOMContentLoaded', () => {
  cityInput.value = 'Kathmandu';
  fetchWeather();
});

/* ═══════════════════════════════════════════════
   AUTHENTICATION SYSTEM
   ═══════════════════════════════════════════════ */

class AuthManager {
  constructor() {
    this.TOKEN_KEY = 'chatapp_token';
    this.USER_KEY = 'chatapp_user';
    this.token = localStorage.getItem(this.TOKEN_KEY);
    this.user = JSON.parse(localStorage.getItem(this.USER_KEY) || 'null');
    this.authCallback = null;
  }

  onAuthChange(callback) {
    this.authCallback = callback;
  }

  notifyAuthChange() {
    if (this.authCallback) {
      this.authCallback(this.isAuthenticated(), this.user);
    }
  }

  isAuthenticated() {
    return !!this.token && !!this.user;
  }

  getToken() {
    return this.token;
  }

  getUser() {
    return this.user;
  }

  async register(username, email, password) {
    try {
      const response = await fetch('/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, email, password })
      });
      const data = await response.json();
      if (data.success) {
        return await this.login(email, password);
      }
      return data;
    } catch (error) {
      console.error('Registration error:', error);
      return { success: false, message: 'Network error. Please try again.' };
    }
  }

  async login(email, password) {
    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });
      const data = await response.json();
      if (data.success) {
        this.token = data.token;
        this.user = data.user;
        localStorage.setItem(this.TOKEN_KEY, data.token);
        localStorage.setItem(this.USER_KEY, JSON.stringify(data.user));
        this.notifyAuthChange();
      }
      return data;
    } catch (error) {
      console.error('Login error:', error);
      return { success: false, message: 'Network error. Please try again.' };
    }
  }

  async logout() {
    try {
      if (this.token) {
        await fetch('/api/auth/logout', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ token: this.token })
        });
      }
    } catch (error) {
      console.error('Logout error:', error);
    }
    this.token = null;
    this.user = null;
    localStorage.removeItem(this.TOKEN_KEY);
    localStorage.removeItem(this.USER_KEY);
    this.notifyAuthChange();
    return { success: true, message: 'Logged out successfully' };
  }

  async verifyAuth() {
    if (!this.token) return false;
    try {
      const response = await fetch(`/api/auth/me?token=${encodeURIComponent(this.token)}`);
      const data = await response.json();
      if (data.success) {
        this.user = data.user;
        localStorage.setItem(this.USER_KEY, JSON.stringify(data.user));
        this.notifyAuthChange();
        return true;
      } else {
        this.logout();
        return false;
      }
    } catch (error) {
      console.error('Auth verification error:', error);
      return false;
    }
  }
}

const authManager = new AuthManager();

// Auth UI Functions
function showAuthModal(type) {
  const modal = document.getElementById('authModal');
  const loginForm = document.getElementById('loginForm');
  const registerForm = document.getElementById('registerForm');
  const modalTitle = document.getElementById('authModalTitle');

  if (modal) {
    modal.style.display = 'flex';
    if (type === 'login') {
      loginForm.style.display = 'block';
      registerForm.style.display = 'none';
      modalTitle.textContent = 'Welcome Back';
    } else {
      loginForm.style.display = 'none';
      registerForm.style.display = 'block';
      modalTitle.textContent = 'Create Account';
    }
  }
}

function hideAuthModal() {
  const modal = document.getElementById('authModal');
  if (modal) {
    modal.style.display = 'none';
  }
}

function updateAuthUI(isLoggedIn, user) {
  const loginBtn = document.getElementById('loginBtn');
  const registerBtn = document.getElementById('registerBtn');
  const logoutBtn = document.getElementById('logoutBtn');
  const userDisplay = document.getElementById('userDisplay');

  if (isLoggedIn && user) {
    if (loginBtn) loginBtn.style.display = 'none';
    if (registerBtn) registerBtn.style.display = 'none';
    if (logoutBtn) logoutBtn.style.display = 'block';
    if (userDisplay) {
      userDisplay.style.display = 'block';
      userDisplay.textContent = user.username || user.email;
    }
  } else {
    if (loginBtn) loginBtn.style.display = 'block';
    if (registerBtn) registerBtn.style.display = 'block';
    if (logoutBtn) logoutBtn.style.display = 'none';
    if (userDisplay) userDisplay.style.display = 'none';
  }
}

// Initialize auth
window.addEventListener('DOMContentLoaded', async () => {
  // Set up auth change listener
  authManager.onAuthChange(updateAuthUI);

  // Verify existing session
  await authManager.verifyAuth();

  // Update UI
  updateAuthUI(authManager.isAuthenticated(), authManager.getUser());
});

// Login form handler
document.addEventListener('DOMContentLoaded', () => {
  const loginForm = document.getElementById('loginFormElement');
  if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const email = document.getElementById('loginEmail').value;
      const password = document.getElementById('loginPassword').value;
      const result = await authManager.login(email, password);
      if (result.success) {
        hideAuthModal();
        alert('Login successful! Welcome back.');
      } else {
        alert(result.message || 'Login failed');
      }
    });
  }

  const registerForm = document.getElementById('registerFormElement');
  if (registerForm) {
    registerForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const username = document.getElementById('registerUsername').value;
      const email = document.getElementById('registerEmail').value;
      const password = document.getElementById('registerPassword').value;
      const result = await authManager.register(username, email, password);
      if (result.success) {
        hideAuthModal();
        alert('Account created successfully! Welcome to Chat&TalkGPT.');
      } else {
        alert(result.message || 'Registration failed');
      }
    });
  }

  const logoutBtn = document.getElementById('logoutBtn');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', async () => {
      await authManager.logout();
      alert('Logged out successfully');
    });
  }

  const closeModal = document.getElementById('authModalClose');
  if (closeModal) {
    closeModal.addEventListener('click', hideAuthModal);
  }
});

/* ═══════════════════════════════════════════════
   REMINDER MANAGEMENT ═══════════════════════════════
   ═══════════════════════════════════════════════ */

class ReminderManager {
  constructor() {
    this.reminders = [];
    this.templates = [];
    this.userId = 1; // Default user
  }

  // Get all reminders
  async getReminders(options = {}) {
    try {
      const params = new URLSearchParams({ user_id: this.userId });
      if (options.enabledOnly) params.append('enabled_only', 'true');
      if (options.upcoming) params.append('upcoming', 'true');
      if (!options.includeCompleted) params.append('include_completed', 'false');

      const response = await fetch(`/api/reminders?${params}`);
      const data = await response.json();

      if (data.success) {
        this.reminders = data.reminders;
        return data.reminders;
      }
      return [];
    } catch (error) {
      console.error('Error getting reminders:', error);
      return [];
    }
  }

  // Get due reminders
  async getDueReminders() {
    try {
      const response = await fetch(`/api/reminders/due?user_id=${this.userId}`);
      const data = await response.json();
      return data.success ? data.reminders : [];
    } catch (error) {
      console.error('Error getting due reminders:', error);
      return [];
    }
  }

  // Get templates
  async getTemplates() {
    try {
      const response = await fetch('/api/reminders/templates');
      const data = await response.json();

      if (data.success) {
        this.templates = data.templates;
        return data.templates;
      }
      return [];
    } catch (error) {
      console.error('Error getting templates:', error);
      return [];
    }
  }

  // Create reminder
  async createReminder(reminderData) {
    try {
      const response = await fetch(`/api/reminders?user_id=${this.userId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(reminderData)
      });
      const data = await response.json();

      if (data.success) {
        this.reminders.push(data.reminder);
        return data.reminder;
      }
      return null;
    } catch (error) {
      console.error('Error creating reminder:', error);
      return null;
    }
  }

  // Create from template
  async createFromTemplate(templateId, triggerTime, customMessage = null) {
    try {
      const response = await fetch(`/api/reminders/from-template?user_id=${this.userId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          template_id: templateId,
          trigger_time: triggerTime,
          custom_message: customMessage
        })
      });
      const data = await response.json();

      if (data.success) {
        this.reminders.push(data.reminder);
        return data.reminder;
      }
      return null;
    } catch (error) {
      console.error('Error creating from template:', error);
      return null;
    }
  }

  // Update reminder
  async updateReminder(reminderId, updateData) {
    try {
      const response = await fetch(`/api/reminders/${reminderId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updateData)
      });
      const data = await response.json();

      if (data.success) {
        const index = this.reminders.findIndex(r => r.id === reminderId);
        if (index !== -1) {
          this.reminders[index] = data.reminder;
        }
        return data.reminder;
      }
      return null;
    } catch (error) {
      console.error('Error updating reminder:', error);
      return null;
    }
  }

  // Delete reminder
  async deleteReminder(reminderId) {
    try {
      const response = await fetch(`/api/reminders/${reminderId}`, {
        method: 'DELETE'
      });
      const data = await response.json();

      if (data.success) {
        this.reminders = this.reminders.filter(r => r.id !== reminderId);
        return true;
      }
      return false;
    } catch (error) {
      console.error('Error deleting reminder:', error);
      return false;
    }
  }

  // Snooze reminder
  async snoozeReminder(reminderId, duration = '15min', customMinutes = null) {
    try {
      const response = await fetch(`/api/reminders/${reminderId}/snooze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ duration, custom_minutes: customMinutes })
      });
      const data = await response.json();

      if (data.success) {
        const index = this.reminders.findIndex(r => r.id === reminderId);
        if (index !== -1) {
          this.reminders[index] = data.reminder;
        }
        return data.reminder;
      }
      return null;
    } catch (error) {
      console.error('Error snoozing reminder:', error);
      return null;
    }
  }

  // Complete reminder
  async completeReminder(reminderId) {
    try {
      const response = await fetch(`/api/reminders/${reminderId}/complete`, {
        method: 'POST'
      });
      const data = await response.json();

      if (data.success) {
        const index = this.reminders.findIndex(r => r.id === reminderId);
        if (index !== -1) {
          this.reminders[index] = data.reminder;
        }
        return data.reminder;
      }
      return null;
    } catch (error) {
      console.error('Error completing reminder:', error);
      return null;
    }
  }

  // Trigger reminder manually
  async triggerReminder(reminderId) {
    try {
      const response = await fetch(`/api/reminders/${reminderId}/trigger`, {
        method: 'POST'
      });
      const data = await response.json();
      return data.success ? data.reminder : null;
    } catch (error) {
      console.error('Error triggering reminder:', error);
      return null;
    }
  }

  // Get by category
  async getByCategory(category) {
    try {
      const response = await fetch(`/api/reminders/category/${category}?user_id=${this.userId}`);
      const data = await response.json();
      return data.success ? data.reminders : [];
    } catch (error) {
      console.error('Error getting by category:', error);
      return [];
    }
  }

  // Get by priority
  async getByPriority(priority) {
    try {
      const response = await fetch(`/api/reminders/priority/${priority}?user_id=${this.userId}`);
      const data = await response.json();
      return data.success ? data.reminders : [];
    } catch (error) {
      console.error('Error getting by priority:', error);
      return [];
    }
  }

  // Render reminders list
  renderRemindersList(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    if (this.reminders.length === 0) {
      container.innerHTML = '<div class="empty-state">No reminders yet. Create your first reminder!</div>';
      return;
    }

    container.innerHTML = this.reminders.map(reminder => this.renderReminderCard(reminder)).join('');
    this.attachReminderEventListeners();
  }

  // Render single reminder card
  renderReminderCard(reminder) {
    const priorityColors = {
      low: '#4CAF50',
      medium: '#2196F3',
      high: '#FF9800',
      urgent: '#F44336'
    };

    const statusClass = reminder.completed ? 'completed' : (reminder.snoozed ? 'snoozed' : (reminder.enabled ? 'active' : 'disabled'));
    const priorityColor = priorityColors[reminder.priority] || '#2196F3';

    return `
      <div class="reminder-card ${statusClass}" data-id="${reminder.id}">
        <div class="reminder-header">
          <span class="reminder-priority" style="background: ${priorityColor}">${reminder.priority}</span>
          <span class="reminder-type">${reminder.type}</span>
        </div>
        <h3 class="reminder-title">${reminder.title}</h3>
        <p class="reminder-message">${reminder.message}</p>
        <div class="reminder-meta">
          <span class="reminder-time">${this.formatDateTime(reminder.trigger_time || reminder.scheduled_time)}</span>
          ${reminder.recurrence_pattern ? `<span class="reminder-recurring">🔄 ${reminder.recurrence_pattern}</span>` : ''}
        </div>
        <div class="reminder-categories">
          ${(reminder.categories || []).map(cat => `<span class="category-tag">${cat}</span>`).join('')}
        </div>
        <div class="reminder-actions">
          ${!reminder.completed ? `
            <button class="btn-complete" data-action="complete" data-id="${reminder.id}">✓ Complete</button>
            <button class="btn-snooze" data-action="snooze" data-id="${reminder.id}">⏰ Snooze</button>
          ` : ''}
          <button class="btn-edit" data-action="edit" data-id="${reminder.id}">✏️ Edit</button>
          <button class="btn-delete" data-action="delete" data-id="${reminder.id}">🗑️ Delete</button>
        </div>
      </div>
    `;
  }

  // Format datetime
  formatDateTime(dateStr) {
    if (!dateStr) return 'Not set';
    const date = new Date(dateStr);
    return date.toLocaleString();
  }

  // Attach event listeners to reminder cards
  attachReminderEventListeners() {
    document.querySelectorAll('[data-action]').forEach(btn => {
      btn.addEventListener('click', async (e) => {
        const action = e.target.dataset.action;
        const id = parseInt(e.target.dataset.id);

        switch (action) {
          case 'complete':
            await this.completeReminder(id);
            break;
          case 'snooze':
            await this.snoozeReminder(id);
            break;
          case 'edit':
            // Trigger edit modal
            break;
          case 'delete':
            if (confirm('Are you sure you want to delete this reminder?')) {
              await this.deleteReminder(id);
            }
            break;
        }

        // Refresh the list
        await this.getReminders();
        this.renderRemindersList('reminders-container');
      });
    });
  }

  // Check and show due reminders notification
  async checkDueReminders() {
    const dueReminders = await this.getDueReminders();

    if (dueReminders.length > 0) {
      // Show notification
      this.showNotification(`${dueReminders.length} reminder(s) are due!`);
    }

    return dueReminders;
  }

  // Show browser notification
  showNotification(message) {
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification('Chat&TalkGPT Reminders', {
        body: message,
        icon: '/favicon.ico'
      });
    }
  }

  // Request notification permission
  async requestNotificationPermission() {
    if ('Notification' in window && Notification.permission === 'default') {
      await Notification.requestPermission();
    }
  }
}

// Create global reminder manager instance
const reminderManager = new ReminderManager();

// Initialize reminders when DOM is ready
window.addEventListener('DOMContentLoaded', async () => {
  // Request notification permission
  reminderManager.requestNotificationPermission();

  // Load templates
  await reminderManager.getTemplates();

  // Load reminders
  await reminderManager.getReminders();

  // Render if container exists
  if (document.getElementById('reminders-container')) {
    reminderManager.renderRemindersList('reminders-container');
  }

  // Check for due reminders every minute
  setInterval(async () => {
    await reminderManager.checkDueReminders();
  }, 60000);
});
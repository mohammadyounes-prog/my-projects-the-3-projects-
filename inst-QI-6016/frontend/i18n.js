(() => {
  const rtlLangs = ['ar', 'he', 'fa', 'ur'];
  const defaultLang = 'en';
  let currentDict = null; // Cache for the loaded dictionary

  function getLang() {
    const saved = localStorage.getItem('lang');
    if (saved) return saved;
    const nav = (navigator.language || navigator.userLanguage || 'en').slice(0,2).toLowerCase();
    return ['en','ar'].includes(nav) ? nav : defaultLang;
  }

  async function loadLocale(lang) {
    // Changed URL to look in the root directory instead of 'locales/'
    const url = `locales/${lang}.json`; // Assuming files are now in frontend/locales/ 

    try {
        const res = await fetch(url);
        if (!res.ok) {
            console.error(`i18n.js: Failed to load locale ${url}: ${res.status} ${res.statusText}`); // More robust error log
            throw new Error(`Failed to load locale: ${lang} (${res.status} ${res.statusText})`);
        }
        const data = await res.json();
    
        return data;
    } catch (e) {
        console.error(`i18n.js: Error during fetch for locale ${url}:`, e);
        throw e;
    }
  }

  function setDirection(lang) {
    const dir = rtlLangs.includes(lang) ? 'rtl' : 'ltr';
    document.documentElement.setAttribute('dir', dir);
    document.documentElement.setAttribute('lang', lang);
  }

  function t(obj, path) {
    const result = path.split('.').reduce((acc, key) => (acc && acc[key] != null ? acc[key] : undefined), obj);
    return result;
  }

  function applyTranslations(node, dict) {
      node.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        const val = t(dict, key);
        if (typeof val === 'string') el.textContent = val;
      });
      // Apply placeholder translations
      node.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
        const key = el.getAttribute('data-i18n-placeholder');
        const val = t(dict, key);
        if (typeof val === 'string') el.setAttribute('placeholder', val);
      });
  }

  async function applyI18n(lang) {

    try {
      currentDict = await loadLocale(lang);
      setDirection(lang);
      applyTranslations(document.documentElement, currentDict);
      document.dispatchEvent(new CustomEvent('i18n:applied', { detail: { lang } }));
      document.dispatchEvent(new CustomEvent('language:changed', { detail: { lang } }));
  
    } catch (e) {
      console.warn('i18n.js: i18n apply failed:', e);
    }
  }

    async function initI18n() {

      const lang = getLang();

      console.log(`i18n.js: initI18n started for lang: ${lang}`);

      try {

        await applyI18n(lang);

        console.log(`i18n.js: applyI18n completed for lang: ${lang}`);

      } catch (error) {

        console.error(`i18n.js: Error during initial applyI18n for lang ${lang}:`, error);

      }

      

      const switcher = document.getElementById('langSwitcher');

      if (switcher) {

        switcher.value = lang;

        switcher.addEventListener('change', async (e) => {

          const newLang = e.target.value;

          localStorage.setItem('lang', newLang);

          console.log(`i18n.js: Language switcher changed to ${newLang}, re-applying i18n.`);

          await applyI18n(newLang);

        });

      }

      console.log(`i18n.js: initI18n finished.`);

    }

  // Expose for manual usage if needed
  window.i18n = {
    applyI18n,
    getLang,
    translateNode: (node) => {
        if (currentDict && node) {
            applyTranslations(node, currentDict);
        }
    },
    t: (key, replacements = {}) => { // Added replacements parameter
        if (!currentDict) {
            console.warn(`i18n.t(): Attempted to translate key "${key}" before dictionary loaded. Returning key.`);
            return key; // Return the key itself if dictionary not loaded
        }
        let translated = t(currentDict, key); // This is the recursive call
        if (translated === undefined) {
            console.warn(`i18n.t(): Key "${key}" not found in current dictionary. Returning undefined.`);
            return undefined; // Return undefined if not found
        }
        // Apply replacements for placeholders like {{dateTime}}
        for (const placeholder in replacements) {
            // Use a global regex to replace all occurrences
            translated = translated.replace(new RegExp(`{{\s*${placeholder}\s*}}`, 'g'), replacements[placeholder]);
        }
        return translated;
    }
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initI18n);
  } else {
    initI18n();
  }
})();
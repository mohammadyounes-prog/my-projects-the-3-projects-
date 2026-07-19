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
    const url = `locales/${lang}.json`;
    const res = await fetch(url);
    if (!res.ok) throw new Error(`Failed to load locale: ${lang}`);
    const data = await res.json();

    return data;
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
  }

  async function applyI18n(lang) {
    try {
      currentDict = await loadLocale(lang);


      setDirection(lang);
      applyTranslations(document.documentElement, currentDict);
      document.dispatchEvent(new CustomEvent('i18n:applied', { detail: { lang } }));
      document.dispatchEvent(new CustomEvent('language:changed', { detail: { lang } }));
    } catch (e) {
      console.warn('i18n apply failed:', e);
    }
  }

  async function initI18n() {
    const lang = getLang();
    await applyI18n(lang);
    const switcher = document.getElementById('langSwitcher');
    if (switcher) {
      switcher.value = lang;
      switcher.addEventListener('change', async (e) => {
        const newLang = e.target.value;
        localStorage.setItem('lang', newLang);
        await applyI18n(newLang);
      });
    }
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
    t: (key) => {
        if (currentDict) {
            return t(currentDict, key);
        }
        return key;
    }
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initI18n);
  } else {
    initI18n();
  }
})();


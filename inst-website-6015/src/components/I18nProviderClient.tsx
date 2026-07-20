'use client';

'use client';

import { useEffect, useState } from 'react';
import { I18nextProvider, initReactI18next } from 'react-i18next';
import { createInstance } from 'i18next'; // Import createInstance
import LanguageDetector from 'i18next-browser-languagedetector'; // Import LanguageDetector
import Backend from 'i18next-http-backend'; // Import Backend

interface I18nProviderClientProps {
  children: React.ReactNode;
  resources: any;
  locale: string;
}

const customBackendRequest = (options, url, payload, callback) => {
  // Use window.fetch explicitly for browser environment
  fetch(url, options)
    .then(response => {
      if (!response.ok) {
        return Promise.reject(new Error(`Failed to load ${url}: ${response.statusText}`));
      }
      return response.json();
    })
    .then(data => callback(null, { status: 200, data: data }))
    .catch(error => callback(error, null));
};

export default function I18nProviderClient({
  children,
  resources,
  locale,
}: I18nProviderClientProps) {
  const [isInitialized, setIsInitialized] = useState(false);
  const [i18nInstance] = useState(() => createInstance()); // Create instance once

  useEffect(() => {
    const initializeI18n = async () => {
      if (!i18nInstance.isInitialized) {
        i18nInstance
          .use(LanguageDetector)
          .use(Backend)
          .use(initReactI18next)
          .init({
            lng: locale,
            fallbackLng: 'en',
            debug: true,
            detection: {
              order: ['queryString', 'cookie'],
              cache: ['cookie'],
            },
            supportedLngs: ['en', 'ar'],
            interpolation: {
              escapeValue: false,
            },
            backend: {
              loadPath: '/locales/{{lng}}/{{ns}}.json',
              allowMultiLoading: true,
              crossOrigin: 'anonymous',
              request: customBackendRequest,
            },
            ns: ['common'],
            defaultNS: 'common',
            resources, // Pass initial resources here
          });
      } else if (i18nInstance.language !== locale) {
        await i18nInstance.changeLanguage(locale);
      }
      setIsInitialized(true);
    };

    initializeI18n();
  }, [locale, resources, i18nInstance]);

  // Set HTML lang and dir attributes
  useEffect(() => {
    if (typeof window !== 'undefined') {
      document.documentElement.lang = locale;
      document.documentElement.dir = locale === 'ar' ? 'rtl' : 'ltr';
    }
  }, [locale]);

  if (!isInitialized) {
    return null; // Or a loading spinner
  }

  return <I18nextProvider i18n={i18nInstance}>{children}</I18nextProvider>;
}

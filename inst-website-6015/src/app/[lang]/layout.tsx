import type { Metadata } from "next";
import I18nProviderClient from "../../components/I18nProviderClient";
import { loadTranslation } from "../../lib/i18n-server";
import Header from "../../components/Header";
import Footer from "../../components/Footer";

// Suite fonts (Space Grotesk, Plus Jakarta Sans, IBM Plex Sans Arabic, Cairo)
// are loaded via next/font in src/app/layout.tsx and wired through --suite-font-*.

export const metadata: Metadata = {
  title: "LMS Platform",
  description: "Empowering education through new technology",
};

export default async function RootLayout({
  children,
  params: { lang },
}: Readonly<{
  children: React.ReactNode;
  params: { lang: string };
}>) {
  // Validate and sanitize the lang parameter
  const validLang = ['en', 'ar'].includes(lang) ? lang : 'en';

  // Load translations for the current language only
  const translations = await loadTranslation(validLang, 'common');

  const resources = {
    [validLang]: { common: translations },
  };

  return (
    <I18nProviderClient resources={resources} locale={validLang}>
      <Header />
      <main>{children}</main>
      <Footer />
    </I18nProviderClient>
  );
}

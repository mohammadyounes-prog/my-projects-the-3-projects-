import type { Metadata } from "next";
import {
  Space_Grotesk,
  Plus_Jakarta_Sans,
  IBM_Plex_Sans_Arabic,
  Cairo,
} from "next/font/google";
import I18nProviderClient from "../../components/I18nProviderClient";
import { loadTranslation } from "../../lib/i18n-server";
import Header from "../../components/Header";
import Footer from "../../components/Footer";

const spaceGrotesk = Space_Grotesk({
  subsets: ["latin"],
  variable: "--font-space-grotesk",
  display: "swap",
});

const plusJakartaSans = Plus_Jakarta_Sans({
  subsets: ["latin"],
  variable: "--font-plus-jakarta",
  display: "swap",
});

const ibmPlexSansArabic = IBM_Plex_Sans_Arabic({
  subsets: ["arabic"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-ibm-plex-arabic",
  display: "swap",
});

const cairo = Cairo({
  subsets: ["arabic", "latin"],
  variable: "--font-cairo",
  display: "swap",
});

export const metadata: Metadata = {
  title: "LMS Platform",
  description: "Empowering education through new technology",
};

export default async function LangLayout({
  children,
  params: { lang },
}: Readonly<{
  children: React.ReactNode;
  params: { lang: string };
}>) {
  const validLang = ["en", "ar"].includes(lang) ? lang : "en";
  const dir = validLang === "ar" ? "rtl" : "ltr";

  const translations = await loadTranslation(validLang, "common");
  const resources = {
    [validLang]: { common: translations },
  };

  return (
    <html
      lang={validLang}
      dir={dir}
      className={`${spaceGrotesk.variable} ${plusJakartaSans.variable} ${ibmPlexSansArabic.variable} ${cairo.variable} nebula-root bg-nebula-bg-deep`}
    >
      <body className="font-sans antialiased bg-nebula-bg-deep text-slate-100 min-h-screen">
        <div className="nebula-neural-grid"></div>
        <I18nProviderClient resources={resources} locale={validLang}>
          <div className="relative z-10 flex flex-col min-h-screen">
            <Header />
            <main className="flex-grow">{children}</main>
            <Footer />
          </div>
        </I18nProviderClient>
      </body>
    </html>
  );
}

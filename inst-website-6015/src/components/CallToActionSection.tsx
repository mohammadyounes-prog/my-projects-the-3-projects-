"use client";

import { useTranslation } from "react-i18next";
import Link from "next/link";

export default function CallToActionSection() {
  const { t, i18n } = useTranslation('common');
  const lang = i18n.language;

  return (
    <section className="relative overflow-hidden py-24 text-white bg-nebula-bg-deep">
      <div className="absolute inset-0 bg-gradient-to-br from-nebula-accent-cyan/10 via-nebula-bg-surface to-nebula-accent-purple/10 backdrop-blur-xl" />
      <div className="container relative z-10 mx-auto px-4 text-center">
        <h2 className="font-display text-4xl sm:text-5xl font-extrabold mb-6 nebula-gradient-text nebula-text-glow">
          {t('call_to_action_title')}
        </h2>
        <p className="text-xl mb-10 max-w-3xl mx-auto text-nebula-text-muted">
          {t('call_to_action_subtitle')}
        </p>
        <div className="flex flex-col sm:flex-row gap-6 justify-center mb-10">
          <Link
            href={`/${lang}/login`}
            className="inline-flex items-center justify-center bg-gradient-to-r from-nebula-accent-cyan to-nebula-accent-purple text-white px-8 py-3.5 rounded-xl hover:brightness-110 transition-all text-lg font-bold shadow-[0_0_20px_rgba(0,229,255,0.4)] hover:shadow-[0_0_30px_rgba(168,85,247,0.6)] hover:-translate-y-0.5"
          >
            {t('get_in_touch')}
          </Link>
          <Link
            href={`/${lang}/solutions`}
            className="inline-flex items-center justify-center nebula-glass border border-nebula-border-glow text-nebula-accent-cyan px-8 py-3.5 rounded-xl hover:bg-nebula-accent-cyan-dim transition-all text-lg font-bold shadow-[0_0_15px_rgba(0,229,255,0.1)] hover:-translate-y-0.5"
          >
            {t('learn_more')}
          </Link>
        </div>
        <Link href={`/${lang}`} className="text-sm font-semibold text-nebula-text-dim hover:text-nebula-accent-cyan transition-colors">
          {t('tdm_systems')}
        </Link>
      </div>
    </section>
  );
}

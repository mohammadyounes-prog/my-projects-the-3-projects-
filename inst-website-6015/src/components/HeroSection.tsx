"use client";

import { useTranslation } from "react-i18next";
import Image from "next/image"; // Assuming you might add an image later
import Link from "next/link";

export default function HeroSection() {
  const { t, i18n } = useTranslation('common');

  return (
    <section id="hero" className="relative overflow-hidden bg-[var(--nebula-gradient-hero)] text-white min-h-[90vh] flex items-center pt-28 pb-16">
      {/* Background Decorative Grids & Glow */}
      <div className="absolute inset-0 nebula-mesh-bg" />
      <div className="absolute top-1/4 start-1/4 h-96 w-96 rounded-full bg-[rgba(0,229,255,0.1)] blur-[100px]" />
      <div className="absolute bottom-1/4 end-1/4 h-96 w-96 rounded-full bg-[rgba(168,85,247,0.1)] blur-[100px]" />

      <div className="container relative z-10 mx-auto flex flex-col md:flex-row items-center justify-between px-4 sm:px-6 lg:px-8">
        {/* Left Side: Text and Buttons */}
        <div className="md:w-1/2 text-center md:text-start md:pe-8">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full nebula-glass border border-nebula-border-glow text-nebula-accent-cyan text-xs font-semibold mb-6 shadow-[0_0_15px_rgba(0,229,255,0.15)]">
            <span className="h-2 w-2 rounded-full bg-nebula-accent-cyan animate-pulse shadow-[0_0_8px_rgba(0,229,255,0.8)]" />
            {t('tdm_systems')} &bull; {t('knowledge_is_power')}
          </div>

          <h1 className="font-display text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight leading-[1.1] mb-6">
            <span className="block text-white drop-shadow-md">{t('empowering_education_title_part1')} {t('empowering_education_title_part2')}</span>
            <span className="block nebula-gradient-text mt-1 nebula-text-glow">
              {t('empowering_education_title_part3')} {t('empowering_education_title_part4')}
            </span>
          </h1>

          <p className="text-lg sm:text-xl text-nebula-text-muted leading-relaxed mb-8 max-w-xl">
            {t('empowering_education_subtitle_part1')} {t('empowering_education_subtitle_part2')}
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center md:justify-start">
            <Link
              href={`/${i18n.language}/hub`}
              className="inline-flex items-center justify-center px-7 py-3.5 rounded-xl bg-gradient-to-r from-nebula-accent-cyan to-nebula-accent-purple text-white hover:brightness-110 transition-all font-semibold text-base shadow-[0_0_20px_rgba(168,85,247,0.4)] hover:shadow-[0_0_30px_rgba(0,229,255,0.6)] hover:-translate-y-0.5"
            >
              {t('get_started')} &rarr;
            </Link>
            <Link
              href={`/${i18n.language}/solutions`}
              className="inline-flex items-center justify-center px-7 py-3.5 rounded-xl nebula-glass border border-nebula-border-glow text-nebula-accent-cyan hover:bg-nebula-accent-cyan-dim hover:text-white transition-all font-semibold text-base hover:-translate-y-0.5 shadow-[0_0_15px_rgba(0,229,255,0.1)] hover:shadow-[0_0_20px_rgba(0,229,255,0.3)]"
            >
              {t('explore_solutions')}
            </Link>
          </div>
        </div>

        {/* Right Side: Showcase Image Card */}
        <div className="md:w-1/2 mt-12 md:mt-0 w-full max-w-lg md:max-w-none">
          <div className="relative mx-auto rounded-2xl nebula-glass-card p-2 border border-nebula-border-glow shadow-[0_0_40px_rgba(0,229,255,0.2)] nebula-glow-border">
            <Image
              src="/examt.jpg"
              alt="TDM Systems Educational Technology Platform"
              width={600}
              height={400}
              priority
              className="rounded-xl w-full h-auto object-cover relative z-10"
            />
          </div>
        </div>
      </div>
    </section>
  );
}

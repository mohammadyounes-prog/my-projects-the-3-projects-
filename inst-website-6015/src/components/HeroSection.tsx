"use client";

import { useTranslation } from "react-i18next";
import Image from "next/image"; // Assuming you might add an image later
import Link from "next/link";

export default function HeroSection() {
  const { t, i18n } = useTranslation('common');

  return (
    <section id="hero" className="relative overflow-hidden bg-gradient-to-b from-[#2c5282] via-[#1e3a8a] to-[#1e293b] text-white min-h-[90vh] flex items-center pt-28 pb-16">
      {/* Background Decorative Grids & Glow */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#ffffff0a_1px,transparent_1px),linear-gradient(to_bottom,#ffffff0a_1px,transparent_1px)] bg-[size:3rem_3rem]" />
      <div className="absolute top-1/4 start-1/4 h-96 w-96 rounded-full bg-sky-500/10 blur-3xl" />

      <div className="container relative mx-auto flex flex-col md:flex-row items-center justify-between px-4 sm:px-6 lg:px-8">
        {/* Left Side: Text and Buttons */}
        <div className="md:w-1/2 text-center md:text-start md:pe-8">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-white/10 backdrop-blur-md border border-white/20 text-sky-200 text-xs font-semibold mb-6">
            <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
            {t('tdm_systems')} &bull; {t('knowledge_is_power')}
          </div>

          <h1 className="font-display text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight leading-[1.1] mb-6">
            <span className="block text-white">{t('empowering_education_title_part1')} {t('empowering_education_title_part2')}</span>
            <span className="block bg-gradient-to-r from-sky-400 via-sky-300 to-indigo-300 bg-clip-text text-transparent mt-1">
              {t('empowering_education_title_part3')} {t('empowering_education_title_part4')}
            </span>
          </h1>

          <p className="text-lg sm:text-xl text-sky-100/90 leading-relaxed mb-8 max-w-xl">
            {t('empowering_education_subtitle_part1')} {t('empowering_education_subtitle_part2')}
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center md:justify-start">
            <Link
              href={`/${i18n.language}/hub`}
              className="inline-flex items-center justify-center px-7 py-3.5 rounded-xl bg-sky-500 text-white hover:bg-sky-400 transition-all font-semibold text-base shadow-lg shadow-sky-500/25 hover:shadow-sky-500/40 hover:-translate-y-0.5"
            >
              {t('get_started')} &rarr;
            </Link>
            <Link
              href={`/${i18n.language}/solutions`}
              className="inline-flex items-center justify-center px-7 py-3.5 rounded-xl bg-white/10 backdrop-blur-md border border-white/20 text-white hover:bg-white/20 transition-all font-semibold text-base hover:-translate-y-0.5"
            >
              {t('explore_solutions')}
            </Link>
          </div>
        </div>

        {/* Right Side: Showcase Image Card */}
        <div className="md:w-1/2 mt-12 md:mt-0 w-full max-w-lg md:max-w-none">
          <div className="relative mx-auto rounded-2xl bg-gradient-to-tr from-white/20 to-white/5 p-2 backdrop-blur-md shadow-2xl border border-white/20">
            <Image
              src="/examt.jpg"
              alt="TDM Systems Educational Technology Platform"
              width={600}
              height={400}
              priority
              className="rounded-xl w-full h-auto object-cover shadow-lg"
            />
          </div>
        </div>
      </div>
    </section>
  );
}

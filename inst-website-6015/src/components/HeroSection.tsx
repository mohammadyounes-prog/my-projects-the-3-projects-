"use client";

import { useTranslation } from "react-i18next";
import Image from "next/image"; // Assuming you might add an image later
import Link from "next/link";

export default function HeroSection() {
  const { t, i18n } = useTranslation('common');

  return (
    <section id="hero" style={{ backgroundColor: '#2c5282' }} className="text-white min-h-screen flex items-center pt-24">
      <div className="container mx-auto flex flex-col md:flex-row items-start justify-between px-4">
        {/* Left Side: Text and Buttons */}
        <div className="md:w-1/2 text-center md:text-start md:pe-12 md:pl-12">
          <h1 className="text-7xl font-bold leading-none mb-4">
            <div className="text-white mb-0">{t('empowering_education_title_part1')}</div>
            <div className="text-white mb-0">{t('empowering_education_title_part2')}</div>
            <div className="text-sky-500 mb-0 mt-[-4px]">{t('empowering_education_title_part3')}</div>
            <div className="text-sky-500 mb-0 mt-[-4px]">{t('empowering_education_title_part4')}</div>
          </h1>
          <div className="text-xl text-sky-300 mb-8">
            <div>{t('empowering_education_subtitle_part1')}</div>
            <div>{t('empowering_education_subtitle_part2')}</div>
          </div>
          <div className="flex flex-col sm:flex-row gap-4 justify-center md:justify-start">
            <Link href={`/${i18n.language}/solutions`} className="border border-white px-8 py-3 rounded-md hover:bg-light-blue hover:text-gray-900 transition-colors text-lg font-semibold shadow-md">
              {t('get_started')}
            </Link>
            <Link href={`/${i18n.language}/solutions`} className="border border-white px-8 py-3 rounded-md hover:bg-light-blue hover:text-gray-900 transition-colors text-lg font-semibold shadow-md">
              {t('explore_solutions')}
            </Link>
          </div>
        </div>

        {/* Right Side: Picture Placeholder */}
        <div className="md:w-1/2 mb-8 md:mb-0 md:ps-12 mt-12">
          <Image src="/examt.jpg" alt="Hero Image" width={500} height={300} className="rounded-lg shadow-lg w-3/4 h-auto mx-auto" />
        </div>
      </div>
    </section>
  );
}

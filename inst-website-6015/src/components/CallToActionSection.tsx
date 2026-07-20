"use client";

import { useTranslation } from "react-i18next";
import Link from "next/link";

export default function CallToActionSection() {
  const { t } = useTranslation('common');

  return (
    <section className="bg-primary-blue text-white py-20">
      <div className="container mx-auto px-4 text-center">
        <h2 className="text-4xl font-bold mb-4">
          {t('call_to_action_title')}
        </h2>
        <p className="text-xl mb-8 max-w-3xl mx-auto">
          {t('call_to_action_subtitle')}
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center mb-8">
          <button className="bg-white text-primary-blue px-8 py-3 rounded-md hover:bg-light-blue transition-colors text-lg font-semibold shadow-md">
            {t('get_in_touch')}
          </button>
          <button className="border border-white px-8 py-3 rounded-md hover:bg-white hover:text-primary-blue transition-colors text-lg font-semibold shadow-md">
            {t('learn_more')}
          </button>
        </div>
        <Link href="#" className="text-lg font-semibold hover:text-light-blue">
          {t('tdm_systems')}
        </Link>
      </div>
    </section>
  );
}

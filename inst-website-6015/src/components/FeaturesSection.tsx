"use client";

import { useTranslation } from "react-i18next";
import Link from "next/link";
import { publicAppLinks } from "@/lib/publicEnv";

export default function FeaturesSection() {
  const { t, i18n } = useTranslation('common');

  const features = [
    {
      id: 'elearning',
      title: t('feature_elearning_title'),
      description: t('feature_elearning_description'),
      buttonText: t('try_elearning'),
      link: `/${i18n.language}/hub`,
    },
    {
      id: 'assessment',
      title: t('feature_assessment_title'),
      description: t('feature_assessment_description'),
      buttonText: t('try_assessment'),
      link: `/${i18n.language}/hub`,
    },
    {
      id: 'ai-education',
      title: t('feature_ai_education_title'),
      description: t('feature_ai_education_description'),
      buttonText: t('try_ai_tools'),
      link: `/${i18n.language}/hub`,
    },
  ];

  return (
    <section id="features" className="bg-slate-50 py-24 border-t border-b border-slate-200/80">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 max-w-7xl">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <span className="inline-block px-3.5 py-1 rounded-full bg-[#2c5282]/10 text-[#2c5282] text-xs font-bold uppercase tracking-wide mb-3">
            Core Features
          </span>
          <h2 className="font-display text-3xl sm:text-4xl font-extrabold tracking-tight text-slate-900">
            {t('features_title')}
          </h2>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <div
              key={feature.id}
              className="suite-motion-card suite-card-hover flex flex-col justify-between bg-white p-8 rounded-2xl border border-slate-200/80 shadow-sm hover:border-[#2c5282]/40 transition-all duration-300"
              style={{ animationDelay: `${index * 100}ms` }}
            >
              <div>
                <h3 className="font-display text-xl font-bold text-[#2c5282] mb-3">{feature.title}</h3>
                <p className="text-sm text-slate-600 leading-relaxed mb-6">{feature.description}</p>
              </div>
              <Link
                href={feature.link}
                className="inline-flex items-center justify-center w-full bg-[#2c5282] text-white px-5 py-3 rounded-xl font-semibold text-sm hover:bg-[#1e3a8a] transition-colors shadow-sm"
              >
                {feature.buttonText} &rarr;
              </Link>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

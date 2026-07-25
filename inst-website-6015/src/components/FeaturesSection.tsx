"use client";

import { useTranslation } from "react-i18next";
import Link from "next/link";
import { publicAppLinks } from "@/lib/publicEnv";

export default function FeaturesSection() {
  const { t } = useTranslation('common');

  const features = [
    {
      id: 'elearning',
      title: t('feature_elearning_title'),
      description: t('feature_elearning_description'),
      buttonText: t('try_elearning'),
      link: "/elearning-try-it", // Placeholder link
    },
    {
      id: 'assessment',
      title: t('feature_assessment_title'),
      description: t('feature_assessment_description'),
      buttonText: t('try_assessment'),
      link: publicAppLinks.onlineExamAdmin,
    },
    {
      id: 'ai-education',
      title: t('feature_ai_education_title'),
      description: t('feature_ai_education_description'),
      buttonText: t('try_ai_tools'),
      link: publicAppLinks.dashboardLogin,
    },
  ];

  return (
    <section id="features" className="bg-white py-20">
      <div className="container mx-auto px-4">
        <h2 className="text-4xl font-bold text-center text-text-color mb-12">
          {t('features_title')}
        </h2>

        <div className="grid md:grid-cols-3 gap-8">
          {features.map((feature) => (
            <div key={feature.id} className="bg-white p-8 rounded-lg shadow-lg text-center border border-gray-200">
              <h3 className="text-2xl font-semibold text-primary-blue mb-4">{feature.title}</h3>
              <p className="text-text-color mb-6">{feature.description}</p>
              <Link href={feature.link} className="inline-block bg-primary-blue text-white px-6 py-2 rounded-md hover:bg-blue-700 transition-colors">
                {feature.buttonText}
              </Link>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

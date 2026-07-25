"use client";

import { useTranslation } from "react-i18next";
import Link from "next/link";
import { FaGraduationCap, FaClipboardCheck, FaRobot } from "react-icons/fa";
import { publicAppLinks } from "@/lib/publicEnv";

export default function FeaturesSection() {
  const { t, i18n } = useTranslation('common');

  const features = [
    {
      id: 'elearning',
      icon: FaGraduationCap,
      title: t('feature_elearning_title'),
      description: t('feature_elearning_description'),
      buttonText: t('try_elearning'),
      link: `/${i18n.language}/hub`,
    },
    {
      id: 'assessment',
      icon: FaClipboardCheck,
      title: t('feature_assessment_title'),
      description: t('feature_assessment_description'),
      buttonText: t('try_assessment'),
      link: `/${i18n.language}/hub`,
    },
    {
      id: 'ai-education',
      icon: FaRobot,
      title: t('feature_ai_education_title'),
      description: t('feature_ai_education_description'),
      buttonText: t('try_ai_tools'),
      link: `/${i18n.language}/hub`,
    },
  ];

  return (
    <section id="features" className="bg-nebula-bg-deep py-24 relative z-10">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 max-w-7xl">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <span className="inline-block px-3.5 py-1 rounded-full bg-nebula-accent-cyan-dim text-nebula-accent-cyan border border-nebula-border-glow text-xs font-bold uppercase tracking-wide mb-3 shadow-[0_0_10px_rgba(0,229,255,0.1)]">
            Core Features
          </span>
          <h2 className="font-display text-3xl sm:text-4xl font-extrabold tracking-tight text-white nebula-text-glow">
            {t('features_title')}
          </h2>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <div
              key={feature.id}
              className="nebula-motion-card nebula-glass-card flex flex-col justify-between p-8 group"
              style={{ animationDelay: `${index * 150}ms` }}
            >
              <div>
                <div className="mb-5 flex h-14 w-14 items-center justify-center rounded-xl bg-nebula-accent-cyan-dim text-nebula-accent-cyan border border-nebula-border-glow transition-all duration-300 group-hover:bg-nebula-accent-cyan group-hover:text-nebula-on-accent group-hover:shadow-[0_0_20px_rgba(0,229,255,0.4)]">
                  <feature.icon className="h-6 w-6" aria-hidden />
                </div>
                <h3 className="font-display text-xl font-bold text-white mb-3 group-hover:text-nebula-accent-cyan transition-colors">{feature.title}</h3>
                <p className="text-sm text-nebula-text-muted leading-relaxed mb-6">{feature.description}</p>
              </div>
              <Link
                href={feature.link}
                className="inline-flex items-center justify-center w-full bg-nebula-bg-surface border border-nebula-border-glow text-nebula-accent-cyan px-5 py-3 rounded-xl font-semibold text-sm hover:bg-nebula-accent-cyan-dim transition-all shadow-[0_0_10px_rgba(0,229,255,0.1)] hover:shadow-[0_0_15px_rgba(0,229,255,0.2)] hover:-translate-y-0.5"
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

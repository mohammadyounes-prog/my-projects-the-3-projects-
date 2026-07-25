"use client";

import { useTranslation } from "react-i18next";
import { FaGraduationCap, FaBrain, FaBook, FaServer, FaExchangeAlt, FaCode, FaChartBar } from "react-icons/fa";

export default function SolutionsPage() {
  const { t } = useTranslation('common');

  const solutionCards = [
    {
      icon: FaGraduationCap,
      title: t('tams_title'),
      desc: t('tams_description'),
      points: [t('tams_kp1'), t('tams_kp2'), t('tams_kp3'), t('tams_kp4'), t('tams_kp5')],
      badge: "Assessment Engine",
    },
    {
      icon: FaBrain,
      title: t('aiquest_title'),
      desc: t('aiquest_description'),
      points: [t('aiquest_kp1'), t('aiquest_kp2'), t('aiquest_kp3'), t('aiquest_kp4'), t('aiquest_kp5')],
      badge: "AI Generation",
    },
    {
      icon: FaBook,
      title: t('lms_title'),
      desc: t('lms_description'),
      points: [t('lms_kp1'), t('lms_kp2'), t('lms_kp3'), t('lms_kp4'), t('lms_kp5')],
      badge: "Learning Hub",
    },
    {
      icon: FaServer,
      title: t('open_source_support_title'),
      desc: t('open_source_support_description'),
      points: [t('open_source_support_kp1'), t('open_source_support_kp2'), t('open_source_support_kp3'), t('open_source_support_kp4')],
      badge: "Infrastructure",
    },
    {
      icon: FaExchangeAlt,
      title: t('system_integration_title'),
      desc: t('system_integration_description'),
      points: [t('system_integration_kp1'), t('system_integration_kp2'), t('system_integration_kp3'), t('system_integration_kp4')],
      badge: "Integrations",
    },
    {
      icon: FaCode,
      title: t('custom_software_title'),
      desc: t('custom_software_description'),
      points: [t('tech_stack_kp1'), t('tech_stack_kp2'), t('tech_stack_kp3'), t('tech_stack_kp4')],
      badge: "Custom Dev",
    },
    {
      icon: FaChartBar,
      title: t('automation_reporting_title'),
      desc: t('automation_reporting_description'),
      points: [t('automation_reporting_kp1'), t('automation_reporting_kp2'), t('automation_reporting_kp3'), t('automation_reporting_kp4'), t('automation_reporting_kp5')],
      badge: "Analytics & ETL",
    },
  ];

  return (
    <div className="nebula-motion-page bg-nebula-bg-deep text-white min-h-screen pt-28 pb-20 font-sans relative z-10">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 max-w-7xl">
        {/* Header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <span className="inline-block px-3.5 py-1 rounded-full bg-nebula-accent-cyan-dim text-nebula-accent-cyan border border-nebula-border-glow text-xs font-bold uppercase tracking-wide mb-3 shadow-[0_0_10px_rgba(0,229,255,0.1)]">
            {t('tdm_systems')} Solutions
          </span>
          <h1 className="font-display text-4xl sm:text-5xl font-extrabold tracking-tight text-white mb-4 nebula-text-glow">
            {t('our_solutions_title')}
          </h1>
          <p className="text-lg text-nebula-text-muted leading-relaxed">
            Discover our complete suite of educational technology, assessment tools, AI engines, and enterprise integrations.
          </p>
        </div>

        {/* Featured Solution — flagship product gets a wide banner instead of
            competing equally with the secondary cards below it. */}
        {(() => {
          const [featured, ...rest] = solutionCards;
          return (
            <>
              <div className="nebula-motion-card nebula-glass-card group relative overflow-hidden p-8 sm:p-10 mb-8 border-nebula-border-glow">
                <div className="relative z-10 flex flex-col sm:flex-row sm:items-center gap-8">
                  <div className="flex h-20 w-20 flex-shrink-0 items-center justify-center rounded-2xl bg-nebula-accent-cyan-dim text-nebula-accent-cyan border border-nebula-border-glow shadow-[0_0_20px_rgba(0,229,255,0.2)]">
                    <featured.icon className="h-9 w-9" aria-hidden />
                  </div>
                  <div className="flex-1">
                    <span className="inline-block text-xs font-semibold text-nebula-accent-cyan bg-nebula-accent-cyan-dim border border-[rgba(0,229,255,0.2)] px-2.5 py-1 rounded-full mb-3">
                      {featured.badge} · Flagship
                    </span>
                    <h2 className="font-display text-2xl sm:text-3xl font-bold text-white mb-3 group-hover:text-nebula-accent-cyan transition-colors">
                      {featured.title}
                    </h2>
                    <p className="text-sm sm:text-base text-nebula-text-muted leading-relaxed mb-5 max-w-3xl">
                      {featured.desc}
                    </p>
                    <ul className="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-2 text-xs sm:text-sm text-nebula-text-muted">
                      {featured.points.map((point, pIdx) => (
                        <li key={pIdx} className="flex items-start gap-2">
                          <span className="text-nebula-accent-cyan font-bold mt-0.5 drop-shadow-[0_0_5px_rgba(0,229,255,0.5)]">✓</span>
                          <span>{point}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>

              {/* Secondary Solutions Grid — 6 cards, two even rows */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                {rest.map((card, index) => (
                  <div
                    key={index}
                    className="nebula-motion-card nebula-glass-card nebula-shimmer-hover group flex flex-col justify-between p-8 relative overflow-hidden transition-all duration-300"
                    style={{ animationDelay: `${index * 150}ms` }}
                  >
                    <div className="relative z-10">
                      <div className="flex items-center justify-between mb-6">
                        <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-nebula-accent-cyan-dim text-nebula-accent-cyan border border-nebula-border-glow transition-transform group-hover:scale-110 group-hover:bg-nebula-accent-cyan group-hover:text-nebula-on-accent group-hover:shadow-[0_0_15px_rgba(0,229,255,0.4)]">
                          <card.icon className="h-6 w-6" aria-hidden />
                        </div>
                        <span className="text-xs font-semibold text-nebula-accent-cyan bg-nebula-accent-cyan-dim border border-[rgba(0,229,255,0.2)] px-2.5 py-1 rounded-full shadow-[0_0_8px_rgba(0,229,255,0.1)]">
                          {card.badge}
                        </span>
                      </div>

                      <h2 className="font-display text-xl font-bold text-white mb-3 group-hover:text-nebula-accent-cyan transition-colors">
                        {card.title}
                      </h2>
                      <p className="text-sm text-nebula-text-muted leading-relaxed mb-6">
                        {card.desc}
                      </p>

                      <div className="border-t border-nebula-border pt-4">
                        <ul className="space-y-2 text-xs text-nebula-text-muted">
                          {card.points.map((point, pIdx) => (
                            <li key={pIdx} className="flex items-start gap-2">
                              <span className="text-nebula-accent-cyan font-bold mt-0.5 drop-shadow-[0_0_5px_rgba(0,229,255,0.5)]">✓</span>
                              <span>{point}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </>
          );
        })()}
      </div>
    </div>
  );
}

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
    <div className="bg-slate-50 text-slate-900 min-h-screen pt-28 pb-20 font-sans">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 max-w-7xl">
        {/* Header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <span className="inline-block px-3.5 py-1 rounded-full bg-[#2c5282]/10 text-[#2c5282] text-xs font-bold uppercase tracking-wide mb-3">
            {t('tdm_systems')} Solutions
          </span>
          <h1 className="font-display text-4xl sm:text-5xl font-extrabold tracking-tight text-slate-900 mb-4">
            {t('our_solutions_title')}
          </h1>
          <p className="text-lg text-slate-600 leading-relaxed">
            Discover our complete suite of educational technology, assessment tools, AI engines, and enterprise integrations.
          </p>
        </div>

        {/* Solutions Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {solutionCards.map((card, index) => (
            <div
              key={index}
              className="suite-motion-card suite-card-hover group flex flex-col justify-between bg-white rounded-2xl p-8 border border-slate-200/80 shadow-sm transition-all duration-300 hover:border-[#2c5282]/40 hover:shadow-xl"
            >
              <div>
                <div className="flex items-center justify-between mb-6">
                  <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-[#2c5282]/10 text-[#2c5282] transition-transform group-hover:scale-110 group-hover:bg-[#2c5282] group-hover:text-white">
                    <card.icon className="h-6 w-6" aria-hidden />
                  </div>
                  <span className="text-xs font-semibold text-[#2c5282] bg-[#2c5282]/10 px-2.5 py-1 rounded-full">
                    {card.badge}
                  </span>
                </div>

                <h2 className="font-display text-xl font-bold text-slate-900 mb-3 group-hover:text-[#2c5282] transition-colors">
                  {card.title}
                </h2>
                <p className="text-sm text-slate-600 leading-relaxed mb-6">
                  {card.desc}
                </p>

                <div className="border-t border-slate-100 pt-4">
                  <ul className="space-y-2 text-xs text-slate-600">
                    {card.points.map((point, pIdx) => (
                      <li key={pIdx} className="flex items-start gap-2">
                        <span className="text-emerald-500 font-bold mt-0.5">&bull;</span>
                        <span>{point}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

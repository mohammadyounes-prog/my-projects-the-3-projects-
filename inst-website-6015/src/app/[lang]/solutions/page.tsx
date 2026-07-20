"use client";

import { useTranslation } from "react-i18next";

export default function SolutionsPage() {
  const { t } = useTranslation('common');

  return (
    <div className="bg-white text-gray-900 min-h-screen pt-24">
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-5xl font-bold text-center mb-12 text-sky-500">{t('our_solutions_title')}</h1>

        <div className="space-y-12">
          {/* TAMS Section */}
          <section>
            <h2 className="text-3xl font-bold text-sky-500 mb-4">
              {t('tams_title')}
            </h2>
            <p className="mb-4 text-gray-700">
              {t('tams_description')}
            </p>
            <ul className="list-disc list-inside space-y-2 text-gray-700">
              <li>{t('tams_kp1')}</li>
              <li>{t('tams_kp2')}</li>
              <li>{t('tams_kp3')}</li>
              <li>{t('tams_kp4')}</li>
              <li>{t('tams_kp5')}</li>
            </ul>
          </section>

          <div className="h-8"></div> {/* Spacer */}

          {/* AIquest Section */}
          <section>
            <h2 className="text-3xl font-bold text-sky-500 mb-4">
              {t('aiquest_title')}
            </h2>
            <p className="mb-4 text-gray-700">
              {t('aiquest_description')}
            </p>
            <ul className="list-disc list-inside space-y-2 text-gray-700">
              <li>{t('aiquest_kp1')}</li>
              <li>{t('aiquest_kp2')}</li>
              <li>{t('aiquest_kp3')}</li>
              <li>{t('aiquest_kp4')}</li>
              <li>{t('aiquest_kp5')}</li>
            </ul>
          </section>

          <div className="h-8"></div> {/* Spacer */}

          {/* LMS Section */}
          <section>
            <h2 className="text-3xl font-bold text-sky-500 mb-4">
              {t('lms_title')}
            </h2>
            <p className="mb-4 text-gray-700">
              {t('lms_description')}
            </p>
            <ul className="list-disc list-inside space-y-2 text-gray-700">
              <li>{t('lms_kp1')}</li>
              <li>{t('lms_kp2')}</li>
              <li>{t('lms_kp3')}</li>
              <li>{t('lms_kp4')}</li>
              <li>{t('lms_kp5')}</li>
            </ul>
          </section>

          <div className="h-8"></div> {/* Spacer */}

          {/* Open-Source Application Support Section */}
          <section>
            <h2 className="text-3xl font-bold text-sky-500 mb-4">
              {t('open_source_support_title')}
            </h2>
            <p className="mb-4 text-gray-700">
              {t('open_source_support_description')}
            </p>
            <ul className="list-disc list-inside space-y-2 text-gray-700">
              <li>{t('open_source_support_kp1')}</li>
              <li>{t('open_source_support_kp2')}</li>
              <li>{t('open_source_support_kp3')}</li>
              <li>{t('open_source_support_kp4')}</li>
            </ul>
          </section>

          <div className="h-8"></div> {/* Spacer */}

          {/* Seamless System Integration Section */}
          <section>
            <h2 className="text-3xl font-bold text-sky-500 mb-4">
              {t('system_integration_title')}
            </h2>
            <p className="mb-4 text-gray-700">
              {t('system_integration_description')}
            </p>
            <ul className="list-disc list-inside space-y-2 text-gray-700">
              <li>{t('system_integration_kp1')}</li>
              <li>{t('system_integration_kp2')}</li>
              <li>{t('system_integration_kp3')}</li>
              <li>{t('system_integration_kp4')}</li>
            </ul>
          </section>

          <div className="h-8"></div> {/* Spacer */}

          {/* Custom Software Development Section */}
          <section>
            <h2 className="text-3xl font-bold text-sky-500 mb-4">
              {t('custom_software_title')}
            </h2>
            <p className="mb-4 text-gray-700">
              {t('custom_software_description')}
            </p>
            <h3 className="text-xl font-bold text-sky-500 mb-2">{t('tech_stack_title')}</h3>
            <ul className="list-disc list-inside space-y-2 text-gray-700">
              <li>{t('tech_stack_kp1')}</li>
              <li>{t('tech_stack_kp2')}</li>
              <li>{t('tech_stack_kp3')}</li>
              <li>{t('tech_stack_kp4')}</li>
            </ul>
          </section>

          <div className="h-8"></div> {/* Spacer */}

          {/* Automation, Reporting & Insights Section */}
          <section>
            <h2 className="text-3xl font-bold text-sky-500 mb-4">
              {t('automation_reporting_title')}
            </h2>
            <p className="mb-4 text-gray-700">
              {t('automation_reporting_description')}
            </p>
            <ul className="list-disc list-inside space-y-2 text-gray-700">
              <li>{t('automation_reporting_kp1')}</li>
              <li>{t('automation_reporting_kp2')}</li>
              <li>{t('automation_reporting_kp3')}</li>
              <li>{t('automation_reporting_kp4')}</li>
              <li>{t('automation_reporting_kp5')}</li>
            </ul>
          </section>
        </div>
      </div>
    </div>
  );
}

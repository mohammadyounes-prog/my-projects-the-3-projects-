"use client";

import { useTranslation } from "react-i18next";
import Link from "next/link";

export default function Footer() {
  const { t, i18n } = useTranslation('common');
  const currentYear = new Date().getFullYear();
  const lang = i18n.language;

  const footerNavGroups = [
    {
      title: t('solutions'),
      items: [
        { name: t('explore_solutions'), href: `/${lang}/solutions` },
        { name: t('back_to_hub', 'Hub'), href: `/${lang}/hub` },
      ],
    },
    {
      title: t('company'),
      items: [
        { name: t('home'), href: `/${lang}` },
        { name: t('login'), href: `/${lang}/login` },
      ],
    },
  ];

  return (
    <footer className="bg-primary-blue text-white py-12">
      <div className="container mx-auto px-4">
        <div className="flex flex-col md:flex-row justify-between items-center md:items-start border-b border-light-blue pb-8 mb-8">
          {/* Headline */}
          <div className="md:w-1/3 text-center md:text-start mb-8 md:mb-0">
            <h3 className="text-2xl font-bold mb-4">
              {t('footer_headline')}
            </h3>
            <Link href={`/${lang}`} className="font-semibold hover:text-light-blue">
              {t('tdm_systems')}
            </Link>
          </div>

          {/* Navigation Links */}
          <div className="md:w-2/3 grid grid-cols-2 sm:grid-cols-2 gap-8 text-center md:text-start">
            {footerNavGroups.map((group, index) => (
              <div key={index}>
                <h4 className="font-semibold text-lg mb-3">{group.title}</h4>
                <ul>
                  {group.items.map((item) => (
                    <li key={item.name} className="mb-2">
                      <Link href={item.href} className="hover:text-light-blue text-sm">
                        {item.name}
                      </Link>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>

        {/* Copyright */}
        <div className="text-center text-sm">
          {t('copyright', { year: currentYear })}
        </div>
      </div>
    </footer>
  );
}

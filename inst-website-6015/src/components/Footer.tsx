"use client";

import { useTranslation } from "react-i18next";
import Link from "next/link";
import { FaGithub, FaLinkedin } from 'react-icons/fa'; // Assuming react-icons is installed

export default function Footer() {
  const { t } = useTranslation('common');
  const currentYear = new Date().getFullYear();

  const footerNavGroups = [
    {
      title: t('resources'),
      items: [
        { name: t('documentation'), href: "#" },
        { name: t('blog'), href: "#" },
        { name: t('community'), href: "#" },
        { name: t('open_source'), href: "#" },
      ],
    },
    {
      title: t('company'),
      items: [
        { name: t('about_us'), href: "#" },
        { name: t('contact'), href: "#" },
      ],
    },
    {
      title: t('legal'),
      items: [
        { name: t('acceptable_use_policy'), href: "#" },
        { name: t('privacy_policy'), href: "#" },
        { name: t('security_policy'), href: "#" },
        { name: t('service_level_agreement'), href: "#" },
      ],
    },
  ];

  return (
    <footer className="bg-primary-blue text-white py-12">
      <div className="container mx-auto px-4">
        <div className="flex flex-col md:flex-row justify-between items-center md:items-start border-b border-light-blue pb-8 mb-8">
          {/* Headline and Social */}
          <div className="md:w-1/3 text-center md:text-start mb-8 md:mb-0">
            <h3 className="text-2xl font-bold mb-4">
              {t('footer_headline')}
            </h3>
            <div className="flex justify-center md:justify-start space-x-4">
              <Link href="#" aria-label="GitHub" className="hover:text-light-blue">
                <FaGithub size={24} />
              </Link>
              <Link href="#" aria-label="LinkedIn" className="hover:text-light-blue">
                <FaLinkedin size={24} />
              </Link>
            </div>
          </div>

          {/* Navigation Links */}
          <div className="md:w-2/3 grid grid-cols-2 sm:grid-cols-4 gap-8 text-center md:text-start">
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

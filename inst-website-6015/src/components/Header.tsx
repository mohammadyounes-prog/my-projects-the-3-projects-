"use client";

import Link from "next/link";
import { useTranslation } from "react-i18next";
import { usePathname, useRouter } from "next/navigation";
import { useState, useEffect } from "react";

export default function Header() {
  const { t, i18n } = useTranslation('common');
  const router = useRouter();
  const pathname = usePathname();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);
  const [user, setUser] = useState<string | null>(null);
  const [showLogoutModal, setShowLogoutModal] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10);
    };
    window.addEventListener('scroll', handleScroll);

    const updateUserInfo = () => {
      const token = localStorage.getItem('access_token');
      if (token) {
        setUser(localStorage.getItem('user_name'));
      } else {
        setUser(null);
      }
    };

    updateUserInfo();
    window.addEventListener('storage', updateUserInfo);

    return () => {
      window.removeEventListener('scroll', handleScroll);
      window.removeEventListener('storage', updateUserInfo);
    };
  }, []);

  // Sync state on every render in case storage changed in the same window
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      setUser(localStorage.getItem('user_name'));
    } else {
      setUser(null);
    }
  });

  const performLogout = () => {
    const authKeys = ['user_name', 'token', 'access_token', 'sso_token'];
    authKeys.forEach(key => localStorage.removeItem(key));
    setUser(null);
    setShowLogoutModal(false);
    router.push(`/`);
  };

  const handleGoToHub = () => {
    setShowLogoutModal(false);
    router.push(`/${i18n.language}/hub`);
  };

  const changeLanguage = (lng: string) => {
    i18n.changeLanguage(lng);
    const newPath = `/${lng}${pathname.substring(3)}`;
    router.push(newPath);
  };

  const navItems = [
    { name: t('home'), href: `/${i18n.language}` },
    { name: t('solutions'), href: `/${i18n.language}/solutions` },
  ];

  // Specific check for login page to handle the unique color transition
  const isLogin = pathname?.includes('/login');

  const headerBg = isLogin 
    ? (isScrolled ? 'bg-white' : 'bg-[#2c5282]') 
    : (isScrolled ? 'bg-sky-600' : 'bg-white');

  const textColor = isLogin
    ? (isScrolled ? 'text-sky-600' : 'text-white')
    : (isScrolled ? 'text-white' : 'text-black');

  const logoSubColor = isLogin
    ? (isScrolled ? 'text-sky-500' : 'text-sky-100')
    : (isScrolled ? 'text-sky-100' : 'text-sky-500');

  return (
    <header className={`fixed top-0 left-0 right-0 z-50 w-full transition-all duration-300 backdrop-blur-md ${
      isScrolled ? 'bg-white/95 shadow-md py-2.5 border-b border-slate-200/80' : 'bg-white/80 py-3.5 border-b border-slate-100'
    }`}>
      <div className="mx-auto flex w-full max-w-screen-xl items-center justify-between gap-4 px-4 sm:px-6 lg:px-8">
        {/* Logo & Brand Lockup */}
        <Link href={`/${i18n.language}`} className="flex min-w-0 shrink flex-col leading-tight group">
          <span className="font-display text-xl font-bold tracking-tight text-[#2c5282] sm:text-2xl transition-colors group-hover:text-sky-700">
            {t('tdm_systems')}
          </span>
          <span className="text-xs font-medium text-slate-500 transition-colors group-hover:text-slate-700">
            {t('knowledge_is_power')}
          </span>
        </Link>

        {/* Desktop Navigation */}
        <nav className="hidden items-center gap-8 md:flex">
          {navItems.map((item) => (
            <Link
              key={item.name}
              href={item.href}
              className={`font-semibold text-sm transition-colors hover:text-[#2c5282] ${
                pathname === item.href ? 'text-[#2c5282] font-bold' : 'text-slate-600'
              }`}
            >
              {item.name}
            </Link>
          ))}
        </nav>

        {/* Language Switcher & Actions */}
        <div className="hidden items-center gap-4 md:flex">
          <Link
            href={`/${i18n.language}/solutions`}
            className="text-xs font-semibold text-[#2c5282] border border-[#2c5282]/30 px-4 py-2 rounded-lg transition-all hover:bg-[#2c5282] hover:text-white hover:border-[#2c5282] shadow-sm"
          >
            {t('explore_solutions')}
          </Link>

          {user ? (
            <div className="flex items-center gap-3">
              {pathname !== '/' && (
                <span className="text-sm font-semibold text-slate-700 bg-slate-100 px-3 py-1.5 rounded-lg border border-slate-200/60">
                  {user}
                </span>
              )}
              <button
                onClick={() => setShowLogoutModal(true)}
                className="text-xs font-semibold text-rose-600 hover:text-rose-700 px-3 py-2 rounded-lg hover:bg-rose-50 transition-colors"
              >
                {t('logout')}
              </button>
            </div>
          ) : (
            <Link
              href={`/${i18n.language}/login`}
              className="text-xs font-semibold bg-[#2c5282] text-white px-4 py-2 rounded-lg transition-all hover:bg-[#1e3a8a] shadow-sm"
            >
              {t('login')}
            </Link>
          )}

          {/* Logout Modal */}
          {showLogoutModal && (
            <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-sm p-4">
              <div className="bg-white p-6 rounded-2xl shadow-2xl max-w-sm w-full border border-slate-100 text-slate-800 animate-in fade-in zoom-in duration-200">
                <h3 className="text-lg font-bold mb-4 font-display text-slate-900">{t('logout_confirm')}</h3>
                <div className="flex flex-col gap-2.5">
                  <button
                    onClick={performLogout}
                    className="w-full px-4 py-2.5 bg-rose-600 text-white rounded-xl font-semibold hover:bg-rose-700 transition-colors text-sm shadow-sm"
                  >
                    {t('logout')}
                  </button>
                  <button
                    onClick={handleGoToHub}
                    className="w-full px-4 py-2.5 bg-[#2c5282] text-white rounded-xl font-semibold hover:bg-[#1e3a8a] transition-colors text-sm shadow-sm"
                  >
                    {t('back_to_hub')}
                  </button>
                  <button
                    onClick={() => setShowLogoutModal(false)}
                    className="w-full px-4 py-2.5 bg-slate-100 text-slate-700 rounded-xl font-semibold hover:bg-slate-200 transition-colors text-sm"
                  >
                    {t('cancel')}
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Language Switcher Pills */}
          <div className="flex items-center rounded-lg border border-slate-200 bg-slate-50/80 p-1 text-xs font-bold shadow-inner">
            <button
              onClick={() => changeLanguage('en')}
              className={`px-2.5 py-1 rounded-md transition-all ${
                i18n.language === 'en' ? 'bg-[#2c5282] text-white shadow-sm' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              EN
            </button>
            <button
              onClick={() => changeLanguage('ar')}
              className={`px-2.5 py-1 rounded-md transition-all ${
                i18n.language === 'ar' ? 'bg-[#2c5282] text-white shadow-sm' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              العربية
            </button>
          </div>
        </div>

        {/* Mobile Menu Button */}
        <div className="md:hidden flex items-center gap-3">
          <div className="flex items-center rounded-md border border-slate-200 bg-slate-50 p-0.5 text-xs font-bold">
            <button
              onClick={() => changeLanguage('en')}
              className={`px-2 py-0.5 rounded ${i18n.language === 'en' ? 'bg-[#2c5282] text-white' : 'text-slate-600'}`}
            >
              EN
            </button>
            <button
              onClick={() => changeLanguage('ar')}
              className={`px-2 py-0.5 rounded ${i18n.language === 'ar' ? 'bg-[#2c5282] text-white' : 'text-slate-600'}`}
            >
              ع
            </button>
          </div>
          <button
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="p-2 rounded-lg text-slate-600 hover:bg-slate-100 transition-colors"
            aria-label="Toggle menu"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              {isMobileMenuOpen ? (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
              ) : (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16" />
              )}
            </svg>
          </button>
        </div>
      </div>

      {/* Mobile Drawer Menu */}
      {isMobileMenuOpen && (
        <div className="md:hidden border-t border-slate-200 bg-white/95 backdrop-blur-md px-6 py-5 shadow-xl space-y-4 animate-in slide-in-from-top duration-200">
          <nav className="flex flex-col space-y-3">
            {navItems.map((item) => (
              <Link
                key={item.name}
                href={item.href}
                onClick={() => setIsMobileMenuOpen(false)}
                className={`text-base font-semibold py-2 transition-colors ${
                  pathname === item.href ? 'text-[#2c5282] font-bold' : 'text-slate-700'
                }`}
              >
                {item.name}
              </Link>
            ))}
          </nav>
          <div className="pt-4 border-t border-slate-100 flex flex-col gap-3">
            <Link
              href={`/${i18n.language}/solutions`}
              onClick={() => setIsMobileMenuOpen(false)}
              className="w-full text-center text-sm font-semibold text-[#2c5282] border border-[#2c5282] py-2.5 rounded-xl"
            >
              {t('explore_solutions')}
            </Link>
            {user ? (
              <button
                onClick={() => {
                  setIsMobileMenuOpen(false);
                  setShowLogoutModal(true);
                }}
                className="w-full text-center text-sm font-semibold text-rose-600 bg-rose-50 py-2.5 rounded-xl"
              >
                {t('logout')} ({user})
              </button>
            ) : (
              <Link
                href={`/${i18n.language}/login`}
                onClick={() => setIsMobileMenuOpen(false)}
                className="w-full text-center text-sm font-semibold bg-[#2c5282] text-white py-2.5 rounded-xl shadow-sm"
              >
                {t('login')}
              </Link>
            )}
          </div>
        </div>
      )}
    </header>
  );
}

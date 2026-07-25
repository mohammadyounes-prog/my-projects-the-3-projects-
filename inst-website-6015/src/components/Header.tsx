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

  return (
    <header className={`fixed top-0 left-0 right-0 z-50 w-full transition-all duration-300 backdrop-blur-[16px] ${
      isScrolled ? 'bg-[rgba(10,14,26,0.8)] shadow-md shadow-[rgba(0,229,255,0.05)] py-2.5 border-b border-nebula-border' : 'bg-[rgba(10,14,26,0.4)] py-3.5 border-b border-transparent'
    }`}>
      <div className="mx-auto flex w-full max-w-screen-xl items-center justify-between gap-4 px-4 sm:px-6 lg:px-8">
        {/* Logo & Brand Lockup */}
        <Link href={`/${i18n.language}`} className="flex min-w-0 shrink flex-col leading-tight group">
          <span className="font-display text-xl font-bold tracking-tight text-white sm:text-2xl transition-colors group-hover:text-transparent group-hover:bg-clip-text group-hover:bg-gradient-to-r group-hover:from-nebula-accent-cyan group-hover:to-nebula-accent-purple nebula-text-glow">
            {t('tdm_systems')}
          </span>
          <span className="text-xs font-medium text-nebula-text-muted transition-colors group-hover:text-nebula-accent-cyan">
            {t('knowledge_is_power')}
          </span>
        </Link>

        {/* Desktop Navigation */}
        <nav className="hidden items-center gap-8 md:flex">
          {navItems.map((item) => (
            <Link
              key={item.name}
              href={item.href}
              className={`font-semibold text-sm transition-colors hover:text-nebula-accent-cyan hover:drop-shadow-[0_0_8px_rgba(0,229,255,0.5)] ${
                pathname === item.href ? 'text-nebula-accent-cyan font-bold drop-shadow-[0_0_8px_rgba(0,229,255,0.5)]' : 'text-slate-300'
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
            className="text-xs font-semibold text-nebula-accent-cyan border border-nebula-border-glow px-4 py-2 rounded-lg transition-all hover:bg-nebula-accent-cyan-dim hover:text-white shadow-[0_0_10px_rgba(0,229,255,0.1)] hover:shadow-[0_0_15px_rgba(0,229,255,0.3)]"
          >
            {t('explore_solutions')}
          </Link>

          {user ? (
            <div className="flex items-center gap-3">
              {pathname !== '/' && (
                <span className="text-sm font-semibold text-white bg-nebula-bg-surface px-3 py-1.5 rounded-lg border border-nebula-border">
                  {user}
                </span>
              )}
              <button
                onClick={() => setShowLogoutModal(true)}
                className="text-xs font-semibold text-pink-400 hover:text-pink-300 px-3 py-2 rounded-lg hover:bg-pink-500/10 transition-colors"
              >
                {t('logout')}
              </button>
            </div>
          ) : (
            <Link
              href={`/${i18n.language}/login`}
              className="text-xs font-semibold bg-gradient-to-r from-[#00e5ff] to-[#a855f7] text-white px-4 py-2 rounded-lg transition-all hover:shadow-[0_0_20px_rgba(168,85,247,0.4)] hover:brightness-110 shadow-[0_0_10px_rgba(0,229,255,0.2)]"
            >
              {t('login')}
            </Link>
          )}

          {/* Logout Modal */}
          {showLogoutModal && (
            <div className="fixed inset-0 z-50 flex items-center justify-center bg-[#0a0e1a]/80 backdrop-blur-md p-4">
              <div className="bg-nebula-bg-surface p-6 rounded-2xl shadow-[0_0_40px_rgba(0,229,255,0.15)] max-w-sm w-full border border-nebula-border-glow text-white animate-in fade-in zoom-in duration-200">
                <h3 className="text-lg font-bold mb-4 font-display text-white">{t('logout_confirm')}</h3>
                <div className="flex flex-col gap-2.5">
                  <button
                    onClick={performLogout}
                    className="w-full px-4 py-2.5 bg-rose-500/20 text-rose-400 border border-rose-500/30 rounded-xl font-semibold hover:bg-rose-500/30 transition-colors text-sm shadow-sm hover:shadow-[0_0_15px_rgba(244,63,94,0.3)]"
                  >
                    {t('logout')}
                  </button>
                  <button
                    onClick={handleGoToHub}
                    className="w-full px-4 py-2.5 bg-gradient-to-r from-[#00e5ff] to-[#a855f7] text-white rounded-xl font-semibold hover:brightness-110 transition-all text-sm shadow-[0_0_15px_rgba(168,85,247,0.3)]"
                  >
                    {t('back_to_hub')}
                  </button>
                  <button
                    onClick={() => setShowLogoutModal(false)}
                    className="w-full px-4 py-2.5 bg-slate-800 text-slate-300 rounded-xl font-semibold hover:bg-slate-700 transition-colors text-sm"
                  >
                    {t('cancel')}
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Language Switcher Pills */}
          <div className="flex items-center rounded-lg border border-nebula-border bg-nebula-bg-surface p-1 text-xs font-bold shadow-inner">
            <button
              onClick={() => changeLanguage('en')}
              className={`px-2.5 py-1 rounded-md transition-all ${
                i18n.language === 'en' ? 'bg-nebula-accent-cyan-dim text-nebula-accent-cyan border border-nebula-border-glow shadow-[0_0_10px_rgba(0,229,255,0.2)]' : 'text-slate-400 hover:text-white'
              }`}
            >
              EN
            </button>
            <button
              onClick={() => changeLanguage('ar')}
              className={`px-2.5 py-1 rounded-md transition-all ${
                i18n.language === 'ar' ? 'bg-nebula-accent-cyan-dim text-nebula-accent-cyan border border-nebula-border-glow shadow-[0_0_10px_rgba(0,229,255,0.2)]' : 'text-slate-400 hover:text-white'
              }`}
            >
              العربية
            </button>
          </div>
        </div>

        {/* Mobile Menu Button */}
        <div className="md:hidden flex items-center gap-3">
          <div className="flex items-center rounded-md border border-nebula-border bg-nebula-bg-surface p-0.5 text-xs font-bold">
            <button
              onClick={() => changeLanguage('en')}
              className={`px-2 py-0.5 rounded ${i18n.language === 'en' ? 'bg-nebula-accent-cyan-dim text-nebula-accent-cyan' : 'text-slate-400'}`}
            >
              EN
            </button>
            <button
              onClick={() => changeLanguage('ar')}
              className={`px-2 py-0.5 rounded ${i18n.language === 'ar' ? 'bg-nebula-accent-cyan-dim text-nebula-accent-cyan' : 'text-slate-400'}`}
            >
              ع
            </button>
          </div>
          <button
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="p-2 rounded-lg text-slate-300 hover:bg-slate-800 transition-colors hover:text-white"
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
        <div className="md:hidden border-t border-nebula-border bg-[rgba(10,14,26,0.95)] backdrop-blur-xl px-6 py-5 shadow-[0_10px_40px_rgba(0,229,255,0.1)] space-y-4 animate-in slide-in-from-top duration-200">
          <nav className="flex flex-col space-y-3">
            {navItems.map((item) => (
              <Link
                key={item.name}
                href={item.href}
                onClick={() => setIsMobileMenuOpen(false)}
                className={`text-base font-semibold py-2 transition-colors ${
                  pathname === item.href ? 'text-nebula-accent-cyan font-bold drop-shadow-[0_0_8px_rgba(0,229,255,0.5)]' : 'text-slate-300'
                }`}
              >
                {item.name}
              </Link>
            ))}
          </nav>
          <div className="pt-4 border-t border-slate-800 flex flex-col gap-3">
            <Link
              href={`/${i18n.language}/solutions`}
              onClick={() => setIsMobileMenuOpen(false)}
              className="w-full text-center text-sm font-semibold text-nebula-accent-cyan border border-nebula-border-glow py-2.5 rounded-xl bg-nebula-accent-cyan-dim shadow-[0_0_10px_rgba(0,229,255,0.1)]"
            >
              {t('explore_solutions')}
            </Link>
            {user ? (
              <button
                onClick={() => {
                  setIsMobileMenuOpen(false);
                  setShowLogoutModal(true);
                }}
                className="w-full text-center text-sm font-semibold text-pink-400 bg-pink-500/10 border border-pink-500/30 py-2.5 rounded-xl"
              >
                {t('logout')} ({user})
              </button>
            ) : (
              <Link
                href={`/${i18n.language}/login`}
                onClick={() => setIsMobileMenuOpen(false)}
                className="w-full text-center text-sm font-semibold bg-gradient-to-r from-[#00e5ff] to-[#a855f7] text-white py-2.5 rounded-xl shadow-[0_0_15px_rgba(168,85,247,0.3)]"
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

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
    <header className={`fixed top-0 inset-inline-0 z-50 transition-all duration-300 ${headerBg} ${textColor} shadow-md border-t-2 border-blue-500`}>
      <div className="container mx-auto flex justify-between items-center p-4">
        {/* Logo */}
        <Link href="/" className="flex flex-col me-auto ms-8">
          <span className="text-3xl font-bold">
            {t('tdm_systems')}
          </span>
          <span className={`text-xl ${logoSubColor} mt-4 font-bold transition-colors duration-300`}>
            {t('knowledge_is_power')}
          </span>
        </Link>

        {/* Desktop Navigation */}
        <nav className="hidden md:flex items-center gap-6 mx-auto">
          {navItems.map((item) => (
            <Link key={item.name} href={item.href} className="font-bold hover:text-sky-300 transition-colors">
              {item.name}
            </Link>
          ))}
        </nav>

        {/* Language Switcher & Call to Action Buttons Container */}
        <div className="hidden md:flex items-center gap-6 ms-auto">
          {/* Explore Solutions Button */}
          <Link 
            href={`/${i18n.language}/solutions`} 
            className={`font-bold border px-4 py-2 rounded-md transition-all ${
              isLogin
                ? (isScrolled ? 'text-sky-600 border-sky-600 hover:bg-sky-600 hover:text-white' : 'text-white border-white hover:bg-white hover:text-[#2c5282]')
                : (isScrolled ? 'text-white border-white hover:bg-sky-500' : 'text-sky-600 border-sky-600 hover:bg-sky-600 hover:text-white')
            }`}
          >
            {t('explore_solutions')}
          </Link>
          
          {user ? (
            <div className="flex items-center gap-4">
              {pathname !== '/' && (
                <span className="font-bold">
                  {user}
                </span>
              )}
              <button 
                onClick={() => setShowLogoutModal(true)}
                className="font-bold hover:opacity-80"
              >
                {t('logout')}
              </button>
            </div>
          ) : (
            <Link href={`/${i18n.language}/login`} className="font-bold hover:opacity-80">
              {t('login')}
            </Link>
          )}

          {/* Logout Confirmation Modal */}
          {showLogoutModal && (
            <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
              <div className="bg-white p-6 rounded-lg shadow-xl text-black">
                <h3 className="text-lg font-bold mb-4">{t('logout_confirm')}</h3>
                <div className="flex flex-col gap-2">
                  <button onClick={performLogout} className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600">
                    {t('logout')}
                  </button>
                  <button onClick={handleGoToHub} className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
                    {t('back_to_hub')}
                  </button>
                  <button onClick={() => setShowLogoutModal(false)} className="px-4 py-2 bg-gray-300 text-black rounded hover:bg-gray-400">
                    {t('cancel')}
                  </button>
                </div>
              </div>
            </div>
          )}
          
          {/* Language Switcher */}
          <div className="relative group">
            <button className="font-bold focus:outline-none hover:opacity-80">
              {i18n.language.toUpperCase()}
            </button>
            <div className="absolute hidden group-hover:block group-focus-within:block bg-white text-gray-800 shadow-lg rounded-md mt-2 w-24 start-0">
              <button
                onClick={() => changeLanguage('en')}
                className="block w-full text-start px-4 py-2 text-gray-800 hover:bg-gray-100 font-bold"
              >
                EN
              </button>
              <button
                onClick={() => changeLanguage('ar')}
                className="block w-full text-start px-4 py-2 text-gray-800 hover:bg-gray-100 font-bold"
              >
                AR
              </button>
            </div>
          </div>
        </div>

        {/* Mobile Menu Button */}
        <div className="md:hidden">
          <button onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)} className="focus:outline-none">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16"></path>
            </svg>
          </button>
        </div>
      </div>

      {/* Mobile Menu */}
      {isMobileMenuOpen && (
        <div className="md:hidden mt-4 p-4 space-y-2 bg-white text-black">
          {navItems.map((item) => (
            <Link key={item.name} href={item.href} className="block py-2 hover:text-sky-300 font-bold">
              {item.name}
            </Link>
          ))}
          <div className="pt-2 border-t border-sky-100">
            <button
              onClick={() => changeLanguage('en')}
              className="block w-full text-start py-2 hover:text-sky-300 font-bold"
            >
              EN
            </button>
            <button
              onClick={() => changeLanguage('ar')}
              className="block w-full text-start py-2 hover:text-sky-300 font-bold"
            >
              AR
            </button>
          </div>
        </div>
      )}
    </header>
  );
}

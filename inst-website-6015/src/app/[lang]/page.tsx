"use client";

import HeroSection from "@/components/HeroSection";
import FeaturesSection from "@/components/FeaturesSection";
import TestimonialsSection from "@/components/TestimonialsSection";
import CallToActionSection from "@/components/CallToActionSection";
import { useTranslation } from "react-i18next";


export default function Home() {
  const { t } = useTranslation('common');

  return (
    <div className="flex flex-col w-full max-w-screen-xl mx-auto">
      <HeroSection />
      <main>
        <FeaturesSection />
        <TestimonialsSection />
        <CallToActionSection />
      </main>
    </div>
  );
}

"use client";

import HeroSection from "@/components/HeroSection";
import FeaturesSection from "@/components/FeaturesSection";
import TestimonialsSection from "@/components/TestimonialsSection";
import CallToActionSection from "@/components/CallToActionSection";
import { useTranslation } from "react-i18next";


export default function Home() {
  const { t } = useTranslation('common');

  return (
    // No page-level max-width here: each section below manages its own
    // `container mx-auto max-w-7xl` for content, while its outer <section>
    // stays full-bleed (background gradients/glows need to reach the
    // viewport edge — an outer `max-w-screen-xl` was clipping that).
    <div className="flex flex-col w-full">
      <HeroSection />
      <main>
        <FeaturesSection />
        <TestimonialsSection />
        <CallToActionSection />
      </main>
    </div>
  );
}

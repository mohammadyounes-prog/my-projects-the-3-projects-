"use client";

import { useTranslation } from "react-i18next";

export default function TestimonialsSection() {
  const { t } = useTranslation("common");

  const testimonials = [
    {
      id: 1,
      quote: t("testimonial_1_quote"),
      author: t("testimonial_1_author"),
      title: t("testimonial_1_title"),
    },
    {
      id: 2,
      quote: t("testimonial_2_quote"),
      author: t("testimonial_2_author"),
      title: t("testimonial_2_title"),
    },
    {
      id: 3,
      quote: t("testimonial_3_quote"),
      author: t("testimonial_3_author"),
      title: t("testimonial_3_title"),
    },
  ];

  return (
    <section id="testimonials" className="bg-nebula-bg-deep py-20 relative z-10">
      <div className="container mx-auto px-4 max-w-7xl">
        <h2 className="font-display text-4xl font-bold text-center text-white mb-12 nebula-text-glow">
          {t("testimonials_title")}
        </h2>

        <div className="grid md:grid-cols-3 gap-6">
          {testimonials.map((testimonial, index) => (
            <div
              key={testimonial.id}
              className="nebula-glass-card p-6 pt-8 text-center relative mt-6 nebula-motion-card"
              style={{ animationDelay: `${index * 150}ms` }}
            >
              {/* Glowing Quotation Mark Accent */}
              <div className="absolute -top-5 left-1/2 -translate-x-1/2 w-10 h-10 rounded-full nebula-glass border border-nebula-border-glow flex items-center justify-center shadow-[0_0_15px_rgba(168,85,247,0.3)] bg-nebula-bg-surface">
                <span className="text-2xl font-display text-nebula-accent-purple pt-1.5">&ldquo;</span>
              </div>
              <p className="italic text-nebula-text-muted mb-5 pt-2 text-sm leading-relaxed">
                &ldquo;{testimonial.quote}&rdquo;
              </p>
              
              <div className="flex flex-col items-center gap-1.5">
                <div className="w-10 h-10 rounded-full bg-nebula-bg-surface border-2 border-nebula-accent-cyan shadow-[0_0_10px_rgba(0,229,255,0.3)] mb-1 flex items-center justify-center">
                  <span className="text-nebula-accent-cyan font-bold">{testimonial.author.charAt(0)}</span>
                </div>
                <p className="font-semibold text-white">
                  {testimonial.author}
                </p>
                <p className="text-xs text-nebula-accent-cyan opacity-80">{testimonial.title}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

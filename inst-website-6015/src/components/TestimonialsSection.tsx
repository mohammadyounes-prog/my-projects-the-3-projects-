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
    <section id="testimonials" className="bg-light-blue py-20">
      <div className="container mx-auto px-4">
        <h2 className="text-4xl font-bold text-center text-text-color mb-12">
          {t("testimonials_title")}
        </h2>

        <div className="grid md:grid-cols-3 gap-8">
          {testimonials.map((testimonial) => (
            <div
              key={testimonial.id}
              className="bg-white p-8 rounded-lg shadow-lg text-center border border-gray-200"
            >
              <p className="italic text-text-color mb-4">
                &ldquo;{testimonial.quote}&rdquo;
              </p>
              <p className="font-semibold text-primary-blue">
                {testimonial.author}
              </p>
              <p className="text-sm text-gray-600">{testimonial.title}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

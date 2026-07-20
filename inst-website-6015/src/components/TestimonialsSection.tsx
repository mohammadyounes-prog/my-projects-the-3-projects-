"use client";

import { useTranslation } from "react-i18next";

export default function TestimonialsSection() {
  const { t } = useTranslation('common');

  // Placeholder data for testimonials
  const testimonials = [
    {
      id: 1,
      quote: "This platform has revolutionized our teaching methods and student engagement.",
      author: "Dr. Emily Smith",
      title: "University Professor",
    },
    {
      id: 2,
      quote: "The AI assessment tools are incredibly powerful and save us so much time.",
      author: "Mr. John Doe",
      title: "High School Principal",
    },
    {
      id: 3,
      quote: "Seamless integration and intuitive design make learning a joy for our students.",
      author: "Ms. Jane Roe",
      title: "Educational Consultant",
    },
  ];

  return (
    <section id="testimonials" className="bg-light-blue py-20">
      <div className="container mx-auto px-4">
        <h2 className="text-4xl font-bold text-center text-text-color mb-12">
          {t('testimonials_title')}
        </h2>

        <div className="grid md:grid-cols-3 gap-8">
          {testimonials.map((testimonial) => (
            <div key={testimonial.id} className="bg-white p-8 rounded-lg shadow-lg text-center border border-gray-200">
              <p className="italic text-text-color mb-4">"{testimonial.quote}"</p>
              <p className="font-semibold text-primary-blue">{testimonial.author}</p>
              <p className="text-sm text-gray-600">{testimonial.title}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

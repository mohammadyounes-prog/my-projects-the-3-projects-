import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "LMS Platform",
  description: "Empowering education through new technology",
};

/**
 * Root layout must exist for App Router, but lang/dir belong on [lang].
 * Nested [lang]/layout owns <html> / <body> (next-intl pattern).
 */
export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return children;
}

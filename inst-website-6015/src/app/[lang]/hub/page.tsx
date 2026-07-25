"use client";

import { useRouter, useParams } from "next/navigation";
import { useTranslation } from "react-i18next";
import {
  FaGraduationCap,
  FaChartLine,
  FaQuestionCircle,
  FaFileAlt,
  FaChalkboardTeacher,
  FaBookOpen,
} from "react-icons/fa";
import { publicAppLinks, publicEnv } from "@/lib/publicEnv";

type HubApp = {
  id: string;
  icon: typeof FaGraduationCap;
  nameKey: string;
  descKey: string;
};

export default function HubPage() {
  const router = useRouter();
  const params = useParams();
  const { t } = useTranslation("common");

  const availableApps: HubApp[] = [
    {
      id: "online-exam",
      icon: FaGraduationCap,
      nameKey: "hub_app_online_exam",
      descKey: "hub_app_online_exam_desc",
    },
    {
      id: "dashboard",
      icon: FaChartLine,
      nameKey: "hub_app_dashboard",
      descKey: "hub_app_dashboard_desc",
    },
    {
      id: "question-retrieval",
      icon: FaQuestionCircle,
      nameKey: "hub_app_question_retrieval",
      descKey: "hub_app_question_retrieval_desc",
    },
  ];

  const upcomingApps: HubApp[] = [
    {
      id: "e-scan",
      icon: FaFileAlt,
      nameKey: "hub_app_e_scan",
      descKey: "hub_app_e_scan_desc",
    },
    {
      id: "virtual-class",
      icon: FaChalkboardTeacher,
      nameKey: "hub_app_virtual_class",
      descKey: "hub_app_virtual_class_desc",
    },
    {
      id: "lms",
      icon: FaBookOpen,
      nameKey: "hub_app_lms",
      descKey: "hub_app_lms_desc",
    },
  ];

  const handleRedirect = async (app: string) => {
    const accessToken = localStorage.getItem("access_token");
    if (!accessToken) {
      alert(t("hub_session_expired"));
      router.push(`/${params.lang}/login`);
      return;
    }

    if (!publicEnv.apiUrl) {
      alert(t("hub_auth_failed"));
      return;
    }

    let token = "";
    try {
      const ssoRes = await fetch(
        `${publicEnv.apiUrl}/api/v1/auth/generate-sso-token`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${accessToken}`,
            "Content-Type": "application/json",
          },
        }
      );

      if (!ssoRes.ok) throw new Error("Failed to generate token");

      const ssoData = await ssoRes.json();
      token = ssoData.sso_token;
    } catch (error) {
      console.error("SSO generation error:", error);
      alert(t("hub_auth_failed"));
      router.push(`/${params.lang}/login`);
      return;
    }

    document.cookie = `sso_token=${token}; path=/; domain=localhost; max-age=3600; SameSite=Lax`;

    const urls: { [key: string]: string } = {
      "online-exam": publicAppLinks.onlineExamAdminSso(token),
      dashboard: publicAppLinks.dashboardHome(token),
      "question-retrieval": publicAppLinks.questionRetrievalHomeSso(token),
    };

    window.open(urls[app], "_blank");
  };

  return (
    <div className="nebula-motion-page min-h-screen bg-nebula-bg-deep font-sans pt-28 pb-20 relative z-10">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        {/* Hub Header */}
        <header className="mb-14 text-center max-w-2xl mx-auto">
          <span className="inline-block px-3.5 py-1 rounded-full bg-nebula-accent-cyan-dim text-nebula-accent-cyan border border-nebula-border-glow text-xs font-bold tracking-wide uppercase mb-3 shadow-[0_0_10px_rgba(0,229,255,0.1)]">
            {t("tdm_systems")}
          </span>
          <h1 className="font-display text-4xl sm:text-5xl font-extrabold tracking-tight text-white mb-4 nebula-text-glow">
            {t("hub_title")}
          </h1>
          <p className="text-lg text-nebula-text-muted leading-relaxed">{t("hub_subtitle")}</p>
        </header>

        {/* Available Apps Grid */}
        <section aria-labelledby="hub-available-heading" className="mb-20">
          <div className="flex items-center justify-between mb-8 border-b border-nebula-border pb-4">
            <h2 id="hub-available-heading" className="font-display text-xl font-bold text-white flex items-center gap-2 drop-shadow-md">
              <span className="h-2.5 w-2.5 rounded-full bg-nebula-accent-cyan shadow-[0_0_8px_rgba(0,229,255,0.8)]" />
              {t("hub_available_section")}
            </h2>
            <span className="text-xs font-semibold text-nebula-text-muted bg-nebula-bg-surface border border-nebula-border px-2.5 py-1 rounded-md">
              3 Active Apps
            </span>
          </div>

          <div className="flex flex-col gap-3 max-w-2xl">
            {availableApps.map((app, index) => (
              <button
                key={app.id}
                type="button"
                onClick={() => handleRedirect(app.id)}
                className="nebula-motion-card group flex w-full items-center gap-4 rounded-xl border border-nebula-border bg-nebula-bg-glass p-4 text-start backdrop-blur-md transition-all duration-200 hover:border-nebula-border-glow hover:bg-nebula-bg-surface"
                style={{ animationDelay: `${index * 100}ms` }}
              >
                <div className="flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-lg bg-nebula-accent-cyan-dim text-nebula-accent-cyan transition-all duration-300 group-hover:bg-nebula-accent-cyan group-hover:text-nebula-on-accent group-hover:shadow-[0_0_15px_rgba(0,229,255,0.4)] border border-nebula-border-glow">
                  <app.icon className="h-5 w-5" aria-hidden />
                </div>

                <div className="min-w-0 flex-1">
                  <h3 className="font-display text-base font-bold text-white group-hover:text-nebula-accent-cyan transition-colors">
                    {t(app.nameKey)}
                  </h3>
                  <p className="text-sm text-nebula-text-muted leading-snug truncate">
                    {t(app.descKey)}
                  </p>
                </div>

                <span className="hidden sm:inline-flex flex-shrink-0 items-center rounded-full bg-nebula-success-dim px-2.5 py-1 text-xs font-semibold text-nebula-success border border-[rgba(16,185,129,0.3)]">
                  Available
                </span>

                <svg className="h-4 w-4 flex-shrink-0 text-nebula-text-dim group-hover:text-nebula-accent-cyan transition-colors rtl:rotate-180" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5l7 7-7 7" />
                </svg>
              </button>
            ))}
          </div>
        </section>

        {/* Upcoming Modules Grid */}
        <section aria-labelledby="hub-upcoming-heading">
          <div className="flex items-center justify-between mb-8 border-b border-nebula-border pb-4">
            <h2 id="hub-upcoming-heading" className="font-display text-xl font-bold text-white flex items-center gap-2 opacity-80">
              <span className="h-2.5 w-2.5 rounded-full bg-nebula-accent-purple shadow-[0_0_8px_rgba(168,85,247,0.8)]" />
              {t("hub_upcoming_section")}
            </h2>
            <span className="text-xs font-semibold text-nebula-text-dim bg-nebula-bg-surface border border-nebula-border px-2.5 py-1 rounded-md">
              In Development
            </span>
          </div>

          <div className="flex flex-col gap-3 max-w-2xl">
            {upcomingApps.map((app) => (
              <div
                key={app.id}
                className="flex w-full items-center gap-4 rounded-xl border border-nebula-border bg-nebula-bg-glass p-4 opacity-60 backdrop-blur-sm transition-opacity hover:opacity-80"
              >
                <div className="flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-lg bg-nebula-bg-surface text-nebula-text-dim border border-nebula-border">
                  <app.icon className="h-5 w-5" aria-hidden />
                </div>

                <div className="min-w-0 flex-1">
                  <h3 className="font-display text-base font-bold text-slate-300">
                    {t(app.nameKey)}
                  </h3>
                  <p className="text-sm text-nebula-text-dim leading-snug truncate">
                    {t(app.descKey)}
                  </p>
                </div>

                <span className="flex-shrink-0 rounded-full bg-nebula-bg-surface border border-nebula-border px-2.5 py-1 text-xs font-semibold text-nebula-text-dim cursor-not-allowed">
                  {t("hub_upcoming")}
                </span>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}

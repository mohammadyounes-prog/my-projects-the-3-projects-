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
    <div className="suite-motion-page min-h-screen bg-surface font-sans">
      <div className="mx-auto max-w-6xl px-4 py-12 sm:px-6 lg:px-8">
        <header className="mb-12 text-center">
          <p className="mb-2 text-sm font-medium text-primary">
            {t("tdm_systems")}
          </p>
          <h1 className="font-display text-3xl font-bold tracking-tight text-suite-text sm:text-4xl">
            {t("hub_title")}
          </h1>
          <p className="mt-3 text-lg text-suite-muted">{t("hub_subtitle")}</p>
        </header>

        <section aria-labelledby="hub-available-heading" className="mb-16">
          <h2 id="hub-available-heading" className="sr-only">
            {t("hub_available_section")}
          </h2>
          <div className="flex flex-wrap justify-center gap-6">
            {availableApps.map((app, index) => (
              <div
                key={app.id}
                className="suite-motion-card suite-card-hover group flex w-full flex-col items-center rounded-lg border border-suite-border bg-surface-raised p-8 text-center shadow-suite1 sm:w-64 md:w-72"
                style={{ animationDelay: `${index * 80}ms` }}
              >
                <button
                  type="button"
                  onClick={() => handleRedirect(app.id)}
                  className="flex w-full cursor-pointer flex-col items-center"
                >
                  <div className="mb-6 rounded-md bg-primary-soft p-4 text-primary transition-transform duration-300 group-hover:scale-105">
                    <app.icon className="h-8 w-8" aria-hidden />
                  </div>
                  <h3 className="mb-2 font-display text-xl font-bold text-suite-text">
                    {t(app.nameKey)}
                  </h3>
                  <p className="mb-6 text-sm text-suite-muted">
                    {t(app.descKey)}
                  </p>
                </button>
                <button
                  type="button"
                  onClick={() => handleRedirect(app.id)}
                  className="w-full rounded-md bg-primary px-4 py-2.5 font-semibold text-white transition-colors hover:bg-primary-dark"
                >
                  {t("hub_open")}
                </button>
              </div>
            ))}
          </div>
        </section>

        <section aria-labelledby="hub-upcoming-heading">
          <div className="mb-8 flex items-center gap-4">
            <div className="h-px flex-1 bg-suite-border" />
            <h2
              id="hub-upcoming-heading"
              className="shrink-0 font-display text-sm font-semibold uppercase tracking-wide text-suite-muted"
            >
              {t("hub_upcoming_section")}
            </h2>
            <div className="h-px flex-1 bg-suite-border" />
          </div>

          <div className="flex flex-wrap justify-center gap-6 opacity-70">
            {upcomingApps.map((app) => (
              <div
                key={app.id}
                className="flex w-full cursor-not-allowed flex-col items-center rounded-lg border border-suite-border bg-surface-raised p-8 text-center shadow-suite0 sm:w-64 md:w-72"
              >
                <div className="mb-6 rounded-md bg-surface p-4 text-suite-muted">
                  <app.icon className="h-8 w-8" aria-hidden />
                </div>
                <h3 className="mb-2 font-display text-xl font-bold text-suite-text">
                  {t(app.nameKey)}
                </h3>
                <p className="mb-6 text-sm text-suite-muted">
                  {t(app.descKey)}
                </p>
                <span className="w-full rounded-md bg-surface px-4 py-2.5 text-center text-sm font-semibold text-suite-muted">
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

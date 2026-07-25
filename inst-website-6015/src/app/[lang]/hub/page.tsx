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
    <div className="suite-motion-page min-h-screen bg-slate-50 font-sans pt-28 pb-20">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        {/* Hub Header */}
        <header className="mb-14 text-center max-w-2xl mx-auto">
          <span className="inline-block px-3.5 py-1 rounded-full bg-[#2c5282]/10 text-[#2c5282] text-xs font-bold tracking-wide uppercase mb-3">
            {t("tdm_systems")}
          </span>
          <h1 className="font-display text-4xl sm:text-5xl font-extrabold tracking-tight text-slate-900 mb-4">
            {t("hub_title")}
          </h1>
          <p className="text-lg text-slate-600 leading-relaxed">{t("hub_subtitle")}</p>
        </header>

        {/* Available Apps Grid */}
        <section aria-labelledby="hub-available-heading" className="mb-20">
          <div className="flex items-center justify-between mb-8 border-b border-slate-200/80 pb-4">
            <h2 id="hub-available-heading" className="font-display text-xl font-bold text-slate-900 flex items-center gap-2">
              <span className="h-2.5 w-2.5 rounded-full bg-emerald-500" />
              {t("hub_available_section")}
            </h2>
            <span className="text-xs font-semibold text-slate-500 bg-slate-200/60 px-2.5 py-1 rounded-md">
              3 Active Apps
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {availableApps.map((app, index) => (
              <div
                key={app.id}
                className="suite-motion-card suite-card-hover group relative flex flex-col justify-between rounded-2xl border border-slate-200/80 bg-white p-8 shadow-sm transition-all duration-300 hover:border-[#2c5282]/40 hover:shadow-xl"
                style={{ animationDelay: `${index * 100}ms` }}
              >
                <div>
                  <div className="mb-6 flex items-center justify-between">
                    <div className="flex h-14 w-14 items-center justify-center rounded-xl bg-[#2c5282]/10 text-[#2c5282] transition-transform duration-300 group-hover:scale-110 group-hover:bg-[#2c5282] group-hover:text-white">
                      <app.icon className="h-7 w-7" aria-hidden />
                    </div>
                    <span className="inline-flex items-center rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-semibold text-emerald-700 border border-emerald-200/60">
                      Available
                    </span>
                  </div>

                  <h3 className="mb-3 font-display text-2xl font-bold text-slate-900 group-hover:text-[#2c5282] transition-colors">
                    {t(app.nameKey)}
                  </h3>
                  <p className="text-sm text-slate-600 leading-relaxed mb-8">
                    {t(app.descKey)}
                  </p>
                </div>

                <button
                  type="button"
                  onClick={() => handleRedirect(app.id)}
                  className="w-full inline-flex items-center justify-center gap-2 rounded-xl bg-[#2c5282] px-5 py-3.5 text-sm font-semibold text-white transition-all duration-200 hover:bg-[#1e3a8a] shadow-md shadow-[#2c5282]/20 hover:shadow-lg"
                >
                  <span>{t("hub_open")}</span>
                  <svg className="w-4 h-4 rtl:rotate-180" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
                  </svg>
                </button>
              </div>
            ))}
          </div>
        </section>

        {/* Upcoming Modules Grid */}
        <section aria-labelledby="hub-upcoming-heading">
          <div className="flex items-center justify-between mb-8 border-b border-slate-200/80 pb-4">
            <h2 id="hub-upcoming-heading" className="font-display text-xl font-bold text-slate-900 flex items-center gap-2">
              <span className="h-2.5 w-2.5 rounded-full bg-amber-400" />
              {t("hub_upcoming_section")}
            </h2>
            <span className="text-xs font-semibold text-slate-500 bg-slate-200/60 px-2.5 py-1 rounded-md">
              In Development
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {upcomingApps.map((app) => (
              <div
                key={app.id}
                className="relative flex flex-col justify-between rounded-2xl border border-slate-200/60 bg-white/60 p-8 shadow-sm opacity-80 backdrop-blur-sm"
              >
                <div>
                  <div className="mb-6 flex items-center justify-between">
                    <div className="flex h-14 w-14 items-center justify-center rounded-xl bg-slate-100 text-slate-400">
                      <app.icon className="h-7 w-7" aria-hidden />
                    </div>
                    <span className="inline-flex items-center rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-500 border border-slate-200">
                      {t("hub_upcoming")}
                    </span>
                  </div>

                  <h3 className="mb-3 font-display text-xl font-bold text-slate-800">
                    {t(app.nameKey)}
                  </h3>
                  <p className="text-sm text-slate-500 leading-relaxed mb-8">
                    {t(app.descKey)}
                  </p>
                </div>

                <div className="w-full rounded-xl bg-slate-100/80 px-4 py-3 text-center text-xs font-semibold text-slate-500 cursor-not-allowed">
                  {t("hub_upcoming")}
                </div>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}

"use client";

import { useRouter, useParams } from "next/navigation";
import { useTranslation } from "react-i18next";
import { FaGraduationCap, FaChartLine, FaQuestionCircle, FaFileAlt, FaChalkboardTeacher, FaBookOpen } from 'react-icons/fa';

export default function HubPage() {
  const router = useRouter();
  const params = useParams();
  const { t } = useTranslation('common');

  const availableApps = [
    { id: "online-exam", icon: FaGraduationCap, color: "bg-indigo-500" },
    { id: "dashboard", icon: FaChartLine, color: "bg-emerald-500" },
    { id: "question-retrieval", icon: FaQuestionCircle, color: "bg-sky-500" },
  ];

  const upcomingApps = [
    { id: "e-scan", icon: FaFileAlt, color: "bg-rose-500" },
    { id: "virtual-class", icon: FaChalkboardTeacher, color: "bg-amber-500" },
    { id: "lms", icon: FaBookOpen, color: "bg-purple-500" },
  ];

  const handleRedirect = async (app: string) => {
    const accessToken = localStorage.getItem("access_token");
    if (!accessToken) {
        alert("Session expired, please log in again.");
        router.push(`/${params.lang}/login`);
        return;
    }

    let token = "";
    try {
        const ssoRes = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/auth/generate-sso-token`, {
            method: "POST",
            headers: { 
                "Authorization": `Bearer ${accessToken}`, 
                "Content-Type": "application/json" 
            }
        });
        
        if (!ssoRes.ok) throw new Error("Failed to generate token");
        
        const ssoData = await ssoRes.json();
        token = ssoData.sso_token;
    } catch (error) {
        console.error("SSO generation error:", error);
        alert("Authentication failed. Please log in again.");
        router.push(`/${params.lang}/login`);
        return;
    }

    document.cookie = `sso_token=${token}; path=/; domain=localhost; max-age=3600; SameSite=Lax`;
    console.log("DEBUG: Token:", token);

    const questionRetrievalUrl = `${process.env.NEXT_PUBLIC_QUESTION_RETRIEVAL_URL}/home.html?sso_token=${token}`;
    console.log("DEBUG: Final URL constructed:", questionRetrievalUrl);
    console.log("DEBUG: Contains '?' :", questionRetrievalUrl.includes('?'));

    const urls: { [key: string]: string } = {
        "online-exam": `${process.env.NEXT_PUBLIC_ONLINE_EXAM_URL}/admin/?sso_token=${token}`,
        "dashboard": `${process.env.NEXT_PUBLIC_DASHBOARD_URL}/?sso_token=${token}`,
        "question-retrieval": questionRetrievalUrl,
    };
    console.log("DEBUG: Redirect URL for question-retrieval:", urls["question-retrieval"]);
    console.log("DEBUG: Process ENV:", process.env.NEXT_PUBLIC_QUESTION_RETRIEVAL_URL);

    console.log("DEBUG: Final URL to be opened by window.open:", urls[app]);
    console.log("DEBUG: --- SSO REDIRECT DIAGNOSTICS ---");
    console.log("DEBUG: Target App:", app);
    console.log("DEBUG: Token used:", token);
    console.log("DEBUG: Final URL:", urls[app]);
    console.log("DEBUG: -------------------------------");
    window.open(urls[app], "_blank");
  };

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-6xl mx-auto">
        <header className="mb-12 text-center">
            <h1 className="text-4xl font-extrabold text-gray-900 tracking-tight">Select Application</h1>
            <p className="text-gray-600 mt-2 text-lg">Choose a system to manage your institution</p>
        </header>
        
        {/* Available Apps */}
        <div className="flex flex-wrap justify-center gap-6 mb-12">
          {availableApps.map((app) => (
            <div
              key={app.id}
              className="group w-full sm:w-64 md:w-72 flex flex-col items-center bg-white p-8 rounded-2xl shadow-sm border border-gray-200 hover:shadow-xl transition-all duration-300 hover:-translate-y-2 text-center"
            >
              <div onClick={() => handleRedirect(app.id)} className="cursor-pointer w-full flex flex-col items-center">
                <div className={`p-4 rounded-full ${app.color} text-white mb-6 group-hover:scale-110 transition-transform duration-300`}>
                  <app.icon className="w-8 h-8" />
                </div>
                <h2 className="text-xl font-bold text-gray-800 mb-2 capitalize">
                  {app.id.replace("-", " ")}
                </h2>
                <p className="text-gray-500 text-sm mb-6">Manage your {app.id.replace("-", " ")} operations</p>
              </div>
              <button
                onClick={() => handleRedirect(app.id)}
                className="w-full py-2 px-4 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors"
              >
                Open
              </button>
            </div>
          ))}
        </div>

        {/* Coming Soon Separator */}
        <div className="flex flex-col items-center mb-12" data-test-id="gemini-separator-block">
            <div className="h-8 w-64 bg-blue-500 rounded-lg mb-4"></div> {/* Made larger and blue */}
            <h1 className="text-blue-700 font-extrabold text-3xl" data-test-id="gemini-separator-text">Coming Soon!</h1> {/* Highly visible text */}
        </div>

        {/* Upcoming Apps */}
        <div className="flex flex-wrap justify-center gap-6 opacity-60 grayscale-[0.5]">
          {upcomingApps.map((app) => (
            <div
              key={app.id}
              className="w-full sm:w-64 md:w-72 flex flex-col items-center bg-white p-8 rounded-2xl shadow-sm border border-gray-200 text-center cursor-not-allowed"
            >
              <div className="w-full flex flex-col items-center">
                <div className={`p-4 rounded-full ${app.color} text-white mb-6`}>
                  <app.icon className="w-8 h-8" />
                </div>
                <h2 className="text-xl font-bold text-gray-800 mb-2 capitalize">
                  {app.id.replace("-", " ")}
                </h2>
                <p className="text-gray-500 text-sm mb-6">Coming Soon</p>
              </div>
              <button
                disabled
                className="w-full py-2 px-4 bg-gray-400 text-white font-semibold rounded-lg cursor-not-allowed"
              >
                Coming Soon
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

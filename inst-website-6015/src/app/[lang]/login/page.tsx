"use client";

import { useState } from "react";
import { useRouter, useParams } from "next/navigation";
import { useTranslation } from "react-i18next";
import { publicEnv } from "@/lib/publicEnv";

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();
  const params = useParams();
  const { t, i18n } = useTranslation("common");

  const API_URL = publicEnv.apiUrl;
  const GOOGLE_CLIENT_ID =
    "828352184347-2bblb1ansh4q7cs8g3fgqj37gr9e9b1o.apps.googleusercontent.com";

  const requireApiUrl = (): boolean => {
    if (API_URL) return true;
    setError(
      t("login_api_unavailable", {
        defaultValue:
          "Auth API URL is not configured. Set NEXT_PUBLIC_API_URL (see .env.example).",
      })
    );
    return false;
  };

  const handleGoogleLogin = () => {
    setError(null);
    if (!requireApiUrl()) return;

    const redirectUri = "http://localhost:6015/api/auth/callback/google";
    const scope = "email profile";
    const authUrl = `https://accounts.google.com/o/oauth2/v2/auth?client_id=${GOOGLE_CLIENT_ID}&redirect_uri=${encodeURIComponent(redirectUri)}&response_type=token&scope=${encodeURIComponent(scope)}`;

    const width = 500;
    const height = 600;
    const left = window.screen.width / 2 - width / 2;
    const top = window.screen.height / 2 - height / 2;
    const popup = window.open(
      authUrl,
      "GoogleLogin",
      `width=${width},height=${height},top=${top},left=${left}`
    );

    window.addEventListener("message", async (event) => {
      if (event.origin !== window.location.origin) return;
      if (event.data.type === "google-auth-success") {
        popup?.close();
        const res = await fetch(`${API_URL}/api/v1/auth/google`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ token: event.data.token }),
        });
        if (res.ok) {
          const authData = await res.json();
          await finishLogin(authData);
        } else {
          setError(t("login_failed", { defaultValue: "Login failed" }));
        }
      }
    });
  };

  const finishLogin = async (authData: any) => {
    if (process.env.NODE_ENV === "development") {
      console.debug("finishLogin authData keys:", Object.keys(authData ?? {}));
    }

    const ssoRes = await fetch(`${API_URL}/api/v1/auth/generate-sso-token`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${authData.access_token}`,
        "Content-Type": "application/json",
      },
    });

    const ssoData = await ssoRes.json();

    if (ssoData.sso_token) {
      localStorage.setItem("access_token", authData.access_token);
      localStorage.setItem("sso_token", ssoData.sso_token);

      const usernameToSave =
        authData.name ||
        authData.username ||
        (authData.is_super_admin ? "superadmin" : "User");
      localStorage.setItem("user_name", usernameToSave);

      const targetLang = params.lang || "en";
      router.push(`/${targetLang}/hub`);
    } else {
      setError(
        t("login_sso_failed", {
          defaultValue: "Failed to receive SSO token",
        })
      );
    }
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (!requireApiUrl()) return;

    const authParams = new URLSearchParams();
    authParams.append("username", username);
    authParams.append("password", password);
    authParams.append("grant_type", "password");

    const authRes = await fetch(`${API_URL}/token`, {
      method: "POST",
      body: authParams,
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    });

    if (authRes.ok) {
      const authData = await authRes.json();
      await finishLogin(authData);
    } else {
      setError(t("login_failed", { defaultValue: "Login failed" }));
    }
  };

  const isRtl = i18n.dir() === "rtl";

  return (
    <div className="suite-motion-page flex min-h-screen flex-col items-center justify-center bg-surface px-6 pb-12 pt-28 font-sans">
      <div className="mb-10 text-center">
        <p className="mb-2 text-sm font-medium text-primary">
          {t("tdm_systems")}
        </p>
        <h1 className="font-display text-3xl font-bold tracking-tight text-suite-text sm:text-4xl">
          {t("login_title")}
        </h1>
      </div>

      <div className="flex w-full max-w-4xl flex-col items-start gap-8 md:flex-row">
        <aside
          className={`w-full rounded-lg border border-suite-border bg-primary-soft p-8 text-suite-text shadow-suite1 md:w-96 ${
            isRtl ? "order-2" : "order-1"
          }`}
        >
          <p className="mb-4 font-display text-base font-bold text-primary">
            {t("after_login_choose_app")}
          </p>
          <ul className="list-inside list-disc space-y-2 text-sm text-suite-text">
            <li>{t("app_1")}</li>
            <li>{t("app_2")}</li>
            <li>{t("app_3")}</li>
            <li>{t("app_4")}</li>
          </ul>
        </aside>

        <form
          onSubmit={handleLogin}
          className={`w-full rounded-lg border border-suite-border bg-surface-raised p-8 shadow-suite1 md:w-96 ${
            isRtl ? "order-1" : "order-2"
          }`}
        >
          {error && (
            <div
              role="alert"
              className="mb-4 rounded-md border border-suite-danger bg-surface px-3 py-2 text-sm font-medium text-suite-danger"
            >
              {error}
            </div>
          )}

          <div className="space-y-4">
            <div>
              <label className="mb-1 block text-sm font-medium text-suite-text">
                {t("username")}
              </label>
              <input
                className="w-full rounded-md border border-suite-border bg-surface p-3 text-suite-text outline-none transition-all focus:border-primary focus:bg-surface-raised focus:ring-2 focus:ring-primary"
                type="text"
                onChange={(e) => setUsername(e.target.value)}
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-suite-text">
                {t("password")}
              </label>
              <input
                className="w-full rounded-md border border-suite-border bg-surface p-3 text-suite-text outline-none transition-all focus:border-primary focus:bg-surface-raised focus:ring-2 focus:ring-primary"
                type="password"
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
            <button
              className="w-full rounded-md bg-primary p-3 font-semibold text-white transition-colors hover:bg-primary-dark"
              type="submit"
            >
              {t("login_button")}
            </button>
          </div>

          <div className="relative my-6">
            <div className="absolute inset-0 flex items-center">
              <span className="w-full border-t border-suite-border"></span>
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-surface-raised px-2 text-suite-muted">
                {t("or_continue_with")}
              </span>
            </div>
          </div>

          <button
            type="button"
            onClick={handleGoogleLogin}
            className="flex w-full items-center justify-center gap-2 rounded-md border border-suite-border p-3 font-semibold text-suite-text transition-colors hover:bg-surface"
          >
            {t("continue_with_google")}
          </button>
        </form>
      </div>
    </div>
  );
}

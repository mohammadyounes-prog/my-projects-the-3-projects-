/**
 * Public (NEXT_PUBLIC_*) env with defaults matching `.env.example`.
 * Ensures missing env never produces `undefined/...` hrefs or fetch URLs.
 *
 * Local suite ports:
 * - Website (this app):     :6015
 * - Auth / SSO API:         :8000
 * - Online exam admin:      :8080
 * - Dashboard (static/serve): :6019  (CRA/dev often :6018)
 * - QuestAI / question retrieval: :6016
 */

const DEFAULTS = {
  apiUrl: "http://localhost:8000",
  onlineExamUrl: "http://localhost:8080",
  dashboardUrl: "http://localhost:6019",
  questionRetrievalUrl: "http://localhost:6016",
} as const;

function trimTrailingSlash(url: string): string {
  return url.replace(/\/+$/, "");
}

function readPublicUrl(
  envValue: string | undefined,
  fallback: string
): string {
  const raw = (envValue ?? "").trim();
  if (!raw || raw === "undefined") return fallback;
  return trimTrailingSlash(raw);
}

export const publicEnv = {
  /** Auth / SSO API base (login `/token`, generate-sso-token, google). */
  apiUrl: readPublicUrl(process.env.NEXT_PUBLIC_API_URL, DEFAULTS.apiUrl),

  /** Online exam / assessment admin app. */
  onlineExamUrl: readPublicUrl(
    process.env.NEXT_PUBLIC_ONLINE_EXAM_URL,
    DEFAULTS.onlineExamUrl
  ),

  /** Dashboard CRA (route `/login`, not `/login.html`). */
  dashboardUrl: readPublicUrl(
    process.env.NEXT_PUBLIC_DASHBOARD_URL,
    DEFAULTS.dashboardUrl
  ),

  /** QuestAI / question retrieval static frontend. */
  questionRetrievalUrl: readPublicUrl(
    process.env.NEXT_PUBLIC_QUESTION_RETRIEVAL_URL,
    DEFAULTS.questionRetrievalUrl
  ),
} as const;

/** Feature / hub deep links built from publicEnv (never `undefined/...`). */
export const publicAppLinks = {
  onlineExamAdmin: `${publicEnv.onlineExamUrl}/admin`,
  /** Dashboard CRA login route. */
  dashboardLogin: `${publicEnv.dashboardUrl}/login`,
  dashboardHome: (ssoToken: string) =>
    `${publicEnv.dashboardUrl}/?sso_token=${encodeURIComponent(ssoToken)}`,
  onlineExamAdminSso: (ssoToken: string) =>
    `${publicEnv.onlineExamUrl}/admin/?sso_token=${encodeURIComponent(ssoToken)}`,
  questionRetrievalHomeSso: (ssoToken: string) =>
    `${publicEnv.questionRetrievalUrl}/home.html?sso_token=${encodeURIComponent(ssoToken)}`,
} as const;

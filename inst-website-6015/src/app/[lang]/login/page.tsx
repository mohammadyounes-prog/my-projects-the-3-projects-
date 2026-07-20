"use client";

import { useState } from "react";
import { useRouter, useParams } from "next/navigation";
import { useTranslation } from "react-i18next";

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const router = useRouter();
  const params = useParams();
  const { t, i18n } = useTranslation('common');

  const API_URL = process.env.NEXT_PUBLIC_API_URL;
  const GOOGLE_CLIENT_ID = "828352184347-2bblb1ansh4q7cs8g3fgqj37gr9e9b1o.apps.googleusercontent.com"; 

  const handleGoogleLogin = () => {
    const redirectUri = "http://localhost:6015/api/auth/callback/google"; 
    const scope = "email profile";
    const authUrl = `https://accounts.google.com/o/oauth2/v2/auth?client_id=${GOOGLE_CLIENT_ID}&redirect_uri=${encodeURIComponent(redirectUri)}&response_type=token&scope=${encodeURIComponent(scope)}`;
    
    // Open popup
    const width = 500;
    const height = 600;
    const left = window.screen.width / 2 - width / 2;
    const top = window.screen.height / 2 - height / 2;
    const popup = window.open(authUrl, "GoogleLogin", `width=${width},height=${height},top=${top},left=${left}`);
    
    // Note: The callback URL needs to handle returning the token to the parent window via postMessage
    window.addEventListener("message", async (event) => {
        if (event.origin !== window.location.origin) return;
        if (event.data.type === "google-auth-success") {
            popup?.close();
            // Send token to backend
            const res = await fetch(`${API_URL}/api/v1/auth/google`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ token: event.data.token }),
            });
            if (res.ok) {
                const authData = await res.json();
                await finishLogin(authData);
            } else {
                alert("Login failed");
            }
        }
    });
  };
  
  const finishLogin = async (authData: any) => {
    console.log("DEBUG: authData received in finishLogin:", authData);
    const ssoRes = await fetch(`${API_URL}/api/v1/auth/generate-sso-token`, {
      method: "POST",
      headers: { "Authorization": `Bearer ${authData.access_token}`, "Content-Type": "application/json" }
    });
    
    const ssoData = await ssoRes.json();
    
    if (ssoData.sso_token) {
      localStorage.setItem("access_token", authData.access_token);
      localStorage.setItem("sso_token", ssoData.sso_token);
      
      // Use a fallback if authData.name is missing
      const usernameToSave = authData.name || authData.username || (authData.is_super_admin ? "superadmin" : "User");
      localStorage.setItem("user_name", usernameToSave);
      
      const targetLang = params.lang || 'en';
      router.push(`/${targetLang}/hub`);
    } else {
      alert("Failed to receive SSO token");
    }
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    const authParams = new URLSearchParams();
    authParams.append('username', username);
    authParams.append('password', password);
    authParams.append('grant_type', 'password');
    
    const authRes = await fetch(`${API_URL}/token`, {
      method: "POST",
      body: authParams,
      headers: { "Content-Type": "application/x-www-form-urlencoded" }
    });

    if (authRes.ok) {
      const authData = await authRes.json();
      await finishLogin(authData);
    } else {
      alert("Login failed");
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-blue-100 p-6 mt-24">
      <div className="flex flex-col md:flex-row gap-8 max-w-4xl w-full items-start">
        <div className={`p-8 bg-blue-100 border border-blue-200 rounded-xl shadow-sm w-full md:w-96 text-blue-900 font-bold ${i18n.dir() === 'rtl' ? 'order-2' : 'order-1'}`}>
          <p className="mb-4 font-bold text-blue-900">{t('after_login_choose_app')}</p>
          <ul className="space-y-2 list-disc list-inside text-blue-900 font-normal">
            <li>{t('app_1')}</li>
            <li>{t('app_2')}</li>
            <li>{t('app_3')}</li>
            <li>{t('app_4')}</li>
          </ul>
        </div>

        <form onSubmit={handleLogin} className={`p-8 bg-white border border-slate-200 rounded-xl shadow-lg w-full md:w-96 ${i18n.dir() === 'rtl' ? 'order-1' : 'order-2'}`}>
          <h1 className="text-2xl font-bold mb-6 text-center text-slate-900">{t('login_title')}</h1>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">{t('username')}</label>
              <input className="w-full p-3 bg-blue-100 text-blue-900 font-bold border border-blue-200 rounded-lg focus:bg-white focus:ring-2 focus:ring-primary-500 outline-none transition-all" type="text" onChange={(e) => setUsername(e.target.value)} />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">{t('password')}</label>
              <input className="w-full p-3 bg-blue-100 text-blue-900 font-bold border border-blue-200 rounded-lg focus:bg-white focus:ring-2 focus:ring-primary-500 outline-none transition-all" type="password" onChange={(e) => setPassword(e.target.value)} />
            </div>
            <button className="w-full p-3 bg-primary-900 hover:bg-primary-500 text-white font-bold rounded-lg transition-all" type="submit">
              {t('login_button')}
            </button>
          </div>

          <div className="relative my-6">
            <div className="absolute inset-0 flex items-center">
              <span className="w-full border-t border-slate-200"></span>
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-white px-2 text-slate-500">{t('or_continue_with')}</span>
            </div>
          </div>

          <button 
            type="button"
            onClick={handleGoogleLogin}
            className="w-full p-3 border border-slate-300 rounded-lg hover:bg-slate-50 transition-all font-bold text-slate-700 flex justify-center items-center gap-2"
          >
            {t('continue_with_google')}
          </button>
        </form>
      </div>
    </div>
  );
}

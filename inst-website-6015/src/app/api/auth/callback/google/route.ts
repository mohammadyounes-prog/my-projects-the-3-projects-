import { NextResponse } from 'next/server';

export async function GET(request: Request) {
  // We need to return an HTML page that extracts the token from the URL hash 
  // and posts it to the opener window.
  const html = `
    <!DOCTYPE html>
    <html>
    <body>
      <script>
        const hash = window.location.hash.substring(1);
        const params = new URLSearchParams(hash);
        const token = params.get("access_token"); // or "id_token" based on response_type

        if (token) {
          window.opener.postMessage({
            type: "google-auth-success",
            token: token
          }, window.location.origin);
        } else {
          // Handle error case
          window.opener.postMessage({
            type: "google-auth-error",
            error: "No token found"
          }, window.location.origin);
        }
      </script>
    </body>
    </html>
  `;
  return new NextResponse(html, {
    headers: { 'Content-Type': 'text/html' },
  });
}

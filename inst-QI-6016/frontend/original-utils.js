function handleUnauthorized(errorDetail) {
    alert(`Your session has expired. Please log in again. Details: ${errorDetail}`);
    localStorage.removeItem('access_token');
    localStorage.removeItem('isAdmin');
    localStorage.removeItem('isSuperAdmin');
    window.location.href = 'login.html';
}

let tokenRefreshTimeout;

async function refreshToken() {

    const currentAccessToken = localStorage.getItem('access_token');
    if (!currentAccessToken) {
    
        handleUnauthorized("No access token found for refresh.");
        return;
    }

    try {
        const baseUrl = (typeof window !== 'undefined' && window.BACKEND_BASE_URL) ? window.BACKEND_BASE_URL : 'http://127.0.0.1:8000';

        const response = await fetch(`${baseUrl}/refresh_token`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${currentAccessToken}`
            }
        });


        if (!response.ok) {
            const errorData = await response.json();

            if (response.status === 401) {
                handleUnauthorized(errorData.detail || 'Token refresh failed: Unauthorized');
            } else {
                throw new Error(errorData.detail || `Token refresh failed with status: ${response.status}`);
            }
            return;
        }

        const data = await response.json();

        localStorage.setItem('access_token', data.access_token);

        return true;
    } catch (error) {

        handleUnauthorized(`Error during token refresh: ${error.message}`);
        return false;
    }
}



function getUserIdFromToken() {
    const token = localStorage.getItem('access_token');
    if (!token) {
        return null;
    }
    try {
        const base64Url = token.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
            return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
        }).join(''));
        const payload = JSON.parse(jsonPayload);
        return payload.sub; // Assuming 'sub' (subject) claim holds the user ID
    } catch (e) {
        console.error("Error decoding token:", e);
        return null;
    }
}

async function fetchWithAuth(url, options = {}, retries = 1) {
    const token = localStorage.getItem('access_token');

    const headers = {
        ...options.headers,
        'Authorization': `Bearer ${token}`
    };
    const newOptions = { ...options, headers };

    // Add Content-Type: application/json if a body is present and not explicitly set
    if (options.body && !headers['Content-Type']) {
        headers['Content-Type'] = 'application/json';
    }

    const response = await fetch(url, newOptions);

    if (response.status === 401) {
        handleUnauthorized('Session expired');
    }

    return response;
}

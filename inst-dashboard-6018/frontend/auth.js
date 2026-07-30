async function updateUserInfo() {
    const currentUserNameSpan = document.getElementById('currentUserName');
    const settingsNavItem = document.getElementById('settingsNavItem');
    const adminNavItem = document.getElementById('adminNavItem');
    const takeATestNavItem = document.getElementById('takeATestNavItem');

    let username = localStorage.getItem('username');
    let isAdmin = localStorage.getItem('isAdmin') === '1' || localStorage.getItem('isAdmin') === 'true';
    let isSuperAdmin = localStorage.getItem('isSuperAdmin') === '1' || localStorage.getItem('isSuperAdmin') === 'true';
    let role = localStorage.getItem('role');

    if (!username || !role) { // Also fetch if role is not in localStorage
        try {
            const baseUrl = (typeof window !== 'undefined' && window.BACKEND_BASE_URL) ? window.BACKEND_BASE_URL : 'http://127.0.0.1:8000';
            const response = await fetchWithAuth(`${baseUrl}/users/me`);

            if (!response.ok) {
                throw new Error('Failed to fetch user details');
            }

            const userData = await response.json();
            username = userData.username;
            isAdmin = userData.is_admin;
            isSuperAdmin = userData.is_super_admin;
            role = userData.role; // Get role from user data

            localStorage.setItem('username', username);
            localStorage.setItem('isAdmin', isAdmin ? '1' : '0');
            localStorage.setItem('isSuperAdmin', isSuperAdmin ? '1' : '0');
            localStorage.setItem('role', role || ''); // Ensure role is always set, even if empty/null

        } catch (error) {
            console.error('Error fetching user info:', error);
            if (currentUserNameSpan) currentUserNameSpan.textContent = 'Error';
            return;
        }
    } else { // If username and role are already in localStorage, ensure isAdmin/isSuperAdmin/role reflect them
        localStorage.setItem('isAdmin', isAdmin ? '1' : '0');
        localStorage.setItem('isSuperAdmin', isSuperAdmin ? '1' : '0');
        localStorage.setItem('role', role || '');
    }

    if (currentUserNameSpan) {
        currentUserNameSpan.textContent = username;
    }

    const canSeeAdmin = (isAdmin || isSuperAdmin);

    if (canSeeAdmin) {
        if (settingsNavItem) settingsNavItem.style.display = 'block';
        if (adminNavItem) adminNavItem.style.display = 'block';
    } else {
        if (settingsNavItem) settingsNavItem.style.display = 'none';
        if (adminNavItem) adminNavItem.style.display = 'none';
    }
    
    if (takeATestNavItem) {
        takeATestNavItem.style.display = 'block'; // Always show for all logged-in users
    }

    // NEW: Handle Result Report Nav Item Visibility
    const resultReportNavItem = document.getElementById('resultReportNavItem');
    if (resultReportNavItem) {
        const hasGenerated = sessionStorage.getItem('questionsGeneratedThisSession') === 'true';
        if (role === 'teacher' || role === 'student' || hasGenerated) {
            resultReportNavItem.style.display = 'block';
        } else {
            resultReportNavItem.style.display = 'none';
        }
    }

}

document.addEventListener('DOMContentLoaded', function() {
    // Skip user info update on public pages to avoid 401 alerts
    const publicPages = ['login.html', 'register.html'];
    const currentPage = window.location.pathname.split('/').pop().toLowerCase();
    
    // Check if SSO is in progress to avoid race conditions with updateUserInfo
    const urlParams = new URLSearchParams(window.location.search);
    const hasSSOToken = urlParams.has('sso_token');
    
    if (!publicPages.includes(currentPage) && !hasSSOToken) {
        updateUserInfo();
    }

    const logoutButton = document.getElementById('logoutButton');
    if(logoutButton) {
        logoutButton.addEventListener('click', function() {
            localStorage.removeItem('access_token');
            localStorage.removeItem('username');
            localStorage.removeItem('isAdmin');
            localStorage.removeItem('isSuperAdmin');
            sessionStorage.removeItem('questionsGeneratedThisSession'); // Clear session-specific flag
            window.location.href = 'login.html';
        });
    }
});

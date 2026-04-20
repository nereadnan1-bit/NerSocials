// Common frontend utilities
window.API_BASE = window.location.hostname === 'localhost' 
    ? 'http://localhost:5000' 
    : 'https://nersocials.onrender.com';

// Update nav based on auth status (called from auth.js)
function updateAuthUI() {
    const token = localStorage.getItem('access_token');
    const loginLink = document.getElementById('loginLink');
    const dashboardLink = document.getElementById('dashboardLink');
    const logoutBtn = document.getElementById('logoutBtn');

    if (token) {
        if (loginLink) loginLink.style.display = 'none';
        if (dashboardLink) dashboardLink.style.display = 'inline';
        if (logoutBtn) {
            logoutBtn.style.display = 'inline';
            logoutBtn.addEventListener('click', (e) => {
                e.preventDefault();
                localStorage.clear();
                window.location.href = 'index.html';
            });
        }
    } else {
        if (loginLink) loginLink.style.display = 'inline';
        if (dashboardLink) dashboardLink.style.display = 'none';
        if (logoutBtn) logoutBtn.style.display = 'none';
    }
}

// Helper for authenticated fetch
async function authFetch(url, options = {}) {
    const token = localStorage.getItem('access_token');
    if (!token) {
        window.location.href = '/login.html';
        throw new Error('Not authenticated');
    }
    const headers = {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        ...options.headers
    };
    return fetch(url, { ...options, headers });
}

document.addEventListener('DOMContentLoaded', updateAuthUI);
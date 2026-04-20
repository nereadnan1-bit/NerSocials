// Hardcode your backend URL (replace with actual Render URL after deploy)
window.API_BASE = 'https://nersocials-api.onrender.com';  // or your actual backend URL

function updateAuthUI() {
    const token = localStorage.getItem('access_token');
    const loginLink = document.getElementById('loginLink');
    const registerLink = document.getElementById('registerLink');
    const dashboardLink = document.getElementById('dashboardLink');
    const logoutBtn = document.getElementById('logoutBtn');

    if (token) {
        if (loginLink) loginLink.style.display = 'none';
        if (registerLink) registerLink.style.display = 'none';
        if (dashboardLink) dashboardLink.style.display = 'inline';
        if (logoutBtn) {
            logoutBtn.style.display = 'inline';
            logoutBtn.onclick = (e) => {
                e.preventDefault();
                localStorage.clear();
                window.location.href = 'index.html';
            };
        }
    } else {
        if (loginLink) loginLink.style.display = 'inline';
        if (registerLink) registerLink.style.display = 'inline';
        if (dashboardLink) dashboardLink.style.display = 'none';
        if (logoutBtn) logoutBtn.style.display = 'none';
    }
}

document.addEventListener('DOMContentLoaded', updateAuthUI);
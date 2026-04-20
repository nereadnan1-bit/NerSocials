// Auth related functions and UI updates
// Extend main.js

// Re-run updateAuthUI after DOM loads
document.addEventListener('DOMContentLoaded', () => {
    if (typeof updateAuthUI === 'function') updateAuthUI();
});

// Logout function
function logout() {
    localStorage.clear();
    window.location.href = '/index.html';
}

// Expose logout globally if needed
window.logout = logout;
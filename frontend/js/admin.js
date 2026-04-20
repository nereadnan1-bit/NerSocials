// Admin panel logic
document.addEventListener('DOMContentLoaded', async () => {
    const token = localStorage.getItem('access_token');
    if (!token) {
        window.location.href = '/login.html';
        return;
    }

    // Verify admin status
    try {
        const res = await authFetch(`${API_BASE}/api/auth/me`);
        const user = await res.json();
        if (!user.is_admin) {
            alert('Admin access required');
            window.location.href = '/dashboard.html';
            return;
        }
    } catch (err) {
        window.location.href = '/login.html';
        return;
    }

    // Setup UI elements
    const newPostBtn = document.getElementById('newPostBtn');
    const formContainer = document.getElementById('postFormContainer');
    const cancelBtn = document.getElementById('cancelForm');
    const postForm = document.getElementById('postForm');
    const formTitle = document.getElementById('formTitle');
    const postsTbody = document.querySelector('#postsTable tbody');

    let editingSlug = null;

    // Load posts table
    async function loadPosts() {
        try {
            const res = await authFetch(`${API_BASE}/api/blog/admin/posts`);
            const posts = await res.json();
            postsTbody.innerHTML = posts.map(post => `
                <tr>
                    <td>${post.title}</td>
                    <td>${post.slug}</td>
                    <td>${post.published ? '✅' : '❌'}</td>
                    <td>
                        <button class="edit-btn" data-slug="${post.slug}">Edit</button>
                        <button class="delete-btn" data-slug="${post.slug}">Delete</button>
                    </td>
                </tr>
            `).join('');

            // Attach event listeners to edit/delete buttons
            document.querySelectorAll('.edit-btn').forEach(btn => {
                btn.addEventListener('click', () => editPost(btn.dataset.slug));
            });
            document.querySelectorAll('.delete-btn').forEach(btn => {
                btn.addEventListener('click', () => deletePost(btn.dataset.slug));
            });
        } catch (err) {
            console.error(err);
        }
    }

    async function editPost(slug) {
        try {
            const res = await authFetch(`${API_BASE}/api/blog/admin/posts`);
            const posts = await res.json();
            const post = posts.find(p => p.slug === slug);
            if (!post) return;

            editingSlug = slug;
            formTitle.textContent = 'Edit Post';
            document.getElementById('title').value = post.title;
            document.getElementById('slug').value = post.slug;
            document.getElementById('excerpt').value = post.excerpt || '';
            document.getElementById('content').value = post.content;
            document.getElementById('published').checked = post.published;
            document.getElementById('postSlug').value = post.slug;
            formContainer.style.display = 'block';
        } catch (err) {
            console.error(err);
        }
    }

    async function deletePost(slug) {
        if (!confirm('Are you sure you want to delete this post?')) return;
        try {
            await authFetch(`${API_BASE}/api/blog/admin/posts/${slug}`, { method: 'DELETE' });
            loadPosts();
        } catch (err) {
            alert('Delete failed');
        }
    }

    newPostBtn.addEventListener('click', () => {
        editingSlug = null;
        formTitle.textContent = 'Create New Post';
        postForm.reset();
        document.getElementById('postSlug').value = '';
        formContainer.style.display = 'block';
    });

    cancelBtn.addEventListener('click', () => {
        formContainer.style.display = 'none';
        postForm.reset();
    });

    postForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = {
            title: document.getElementById('title').value,
            slug: document.getElementById('slug').value,
            excerpt: document.getElementById('excerpt').value,
            content: document.getElementById('content').value,
            published: document.getElementById('published').checked
        };

        const method = editingSlug ? 'PUT' : 'POST';
        const url = editingSlug 
            ? `${API_BASE}/api/blog/admin/posts/${editingSlug}`
            : `${API_BASE}/api/blog/admin/posts`;

        try {
            const res = await authFetch(url, {
                method,
                body: JSON.stringify(formData)
            });
            if (!res.ok) throw new Error('Save failed');
            formContainer.style.display = 'none';
            loadPosts();
        } catch (err) {
            alert('Error saving post');
        }
    });

    // Logout
    document.getElementById('logoutBtn').addEventListener('click', (e) => {
        e.preventDefault();
        logout();
    });

    // Initial load
    loadPosts();
});
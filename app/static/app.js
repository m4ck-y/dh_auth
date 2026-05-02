const message = document.getElementById('message');

async function fetchProfile() {
    try {
        const response = await fetch('/v1/auth/me');
        if (response.ok) {
            const data = await response.json();
            document.getElementById('profile-data').innerText = JSON.stringify(data, null, 2);
            document.getElementById('login-container').style.display = 'none';
            document.getElementById('auth-container').style.display = 'block';
        } else {
            document.getElementById('login-container').style.display = 'block';
            document.getElementById('auth-container').style.display = 'none';
        }
    } catch (err) {
        console.error('Error fetching profile', err);
    }
}

document.getElementById('login-btn').addEventListener('click', async () => {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    try {
        const response = await fetch('/v1/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        if (response.ok) {
            message.innerText = 'Login successful!';
            message.style.color = 'green';
            await fetchProfile();
        } else {
            const data = await response.json();
            message.innerText = data.detail || 'Login failed';
            message.style.color = 'red';
        }
    } catch (err) {
        message.innerText = 'Error connecting to server';
    }
});

document.getElementById('logout-btn').addEventListener('click', async () => {
    try {
        const response = await fetch('/v1/auth/logout', { method: 'POST' });
        if (response.ok) {
            document.getElementById('login-container').style.display = 'block';
            document.getElementById('auth-container').style.display = 'none';
            message.innerText = 'Logged out';
            message.style.color = 'blue';
            document.getElementById('profile-data').innerText = 'Loading profile...';
        }
    } catch (err) {
        console.error('Logout error', err);
    }
});

// Check session on load
fetchProfile();

/**
 * DH Auth — Test UI
 *
 * Class-oriented client for login, session check, profile display, and logout.
 * Communicates with dh_auth via HttpOnly cookies (access_token / refresh_token).
 */

class AuthClient {
  constructor(baseURL = '') {
    this.baseURL = baseURL;
    this.messageEl = document.getElementById('message');
  }

  async me() {
    const response = await fetch(`${this.baseURL}/v1/auth/me`);
    if (!response.ok) return null;
    return response.json();
  }

  async login(username, password) {
    const response = await fetch(`${this.baseURL}/v1/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });
    const data = await response.json().catch(() => ({}));
    return { ok: response.ok, data };
  }

  async logout() {
    const response = await fetch(`${this.baseURL}/v1/auth/logout`, { method: 'POST' });
    return response.ok;
  }

  setMessage(text, color = 'red') {
    this.messageEl.innerText = text;
    this.messageEl.style.color = color;
  }
}


class AuthUI {
  constructor(client) {
    this.client = client;
    this.loginContainer = document.getElementById('login-panel');
    this.authContainer = document.getElementById('session-panel');
    this.profileData = document.getElementById('profile-data');
    this.usernameInput = document.getElementById('username');
    this.passwordInput = document.getElementById('password');
  }

  showLogin() {
    this.loginContainer.style.display = 'block';
    this.authContainer.style.display = 'none';
  }

  showAuthenticated(profile) {
    this.loginContainer.style.display = 'none';
    this.authContainer.style.display = 'block';
    this.profileData.innerText = JSON.stringify(profile, null, 2);
  }

  resetProfile() {
    this.profileData.innerText = 'Loading profile...';
  }
}


class App {
  constructor() {
    this.client = new AuthClient();
    this.ui = new AuthUI(this.client);

    this.bindEvents();
    this.boot();
  }

  bindEvents() {
    document.getElementById('login-btn').addEventListener('click', () => this.handleLogin());
    document.getElementById('logout-btn').addEventListener('click', () => this.handleLogout());
  }

  async boot() {
    const profile = await this.client.me();
    if (profile) {
      this.ui.showAuthenticated(profile);
    } else {
      this.ui.showLogin();
    }
  }

  async handleLogin() {
    const username = this.ui.usernameInput.value;
    const password = this.ui.passwordInput.value;

    const { ok, data } = await this.client.login(username, password);

    if (ok) {
      this.client.setMessage('Login successful!', 'green');
      const profile = await this.client.me();
      if (profile) {
        this.ui.showAuthenticated(profile);
      }
    } else {
      this.client.setMessage(data.detail || 'Login failed');
    }
  }

  async handleLogout() {
    const ok = await this.client.logout();
    if (ok) {
      this.ui.resetProfile();
      this.ui.showLogin();
      this.client.setMessage('Logged out', 'blue');
    }
  }
}


document.addEventListener('DOMContentLoaded', () => {
  new App();
});
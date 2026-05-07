from dh_shared.testui.templates.spa import render_spa_page
from dh_shared.testui.components import render_button, render_input, render_json_pre


def build(root_path: str) -> str:
    js = f"{root_path}/static/app.js"

    login_form = f"""<form id="login-form" onsubmit="return false">
    <table>
        <tr><td>{render_input("username", "user@example.com", "USERNAME:", input_id="username", size=30)}</td></tr>
        <tr><td>{render_input("password", "********", "PASSWORD:", input_type="password", input_id="password", size=30)}</td></tr>
        <tr><td>{render_button("LOGIN", "POST", "login-btn")}</td></tr>
    </table>
</form>

<p>$ Enter your credentials to initialize session.</p>"""

    login_panel = f"""<h2>> LOGIN</h2>
{login_form}"""

    session_panel = f"""<h2>> SESSION ACTIVE</h2>

<table>
    <tr><td><b>STATUS:</b></td><td><font color="#00ff88">Authenticated (HttpOnly cookies)</font></td></tr>
    <tr><td><b>ACCESS TOKEN:</b></td><td><tt>JWT | HttpOnly | 15 min TTL</tt></td></tr>
    <tr><td><b>REFRESH TOKEN:</b></td><td><tt>Random | HttpOnly | 30 day TTL</tt></td></tr>
</table>

<h3>> PROFILE (GET /v1/auth/me)</h3>
{render_json_pre("profile-data", "Loading profile...")}

<br>
{render_button("REFRESH", "GET", "refresh-profile-btn")}
&nbsp;&nbsp;
{render_button("LOGOUT", "POST", "logout-btn")}"""

    return render_spa_page(
        root_path=root_path,
        title="DIGITAL HOSPITAL // AUTH SERVICE",
        panels={
            "login-panel": login_panel,
            "session-panel": session_panel,
        },
        js_module=js,
        active_panel="login-panel",
    )

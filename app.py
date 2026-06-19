import streamlit as st
from core.config import ensure_dirs, APP_NAME, DEFAULT_PROVIDER
from core.auth import authenticate, create_user, init_users
from ui.theme import apply_theme, hero
from ui.dashboard import render_dashboard
from ui.project_form import render_new_project
from ui.writing_studio import render_writing_studio
from ui.story_bible_ui import render_story_bible
from ui.export_ui import render_exports
from ui.settings_ui import render_settings
from core.storage import load_project_bundle

ensure_dirs()
init_users()
apply_theme()

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "page" not in st.session_state:
    st.session_state.page = "Dashboard"
if "provider" not in st.session_state:
    st.session_state.provider = DEFAULT_PROVIDER


def login_page():
    hero(APP_NAME, "Your personal AI writing studio for novels, poems, spoken word, stories, and non-fiction.")
    tab1, tab2 = st.tabs(["Login", "Create Local User"])
    with tab1:
        with st.form("login"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login", type="primary")
        if submitted:
            if authenticate(username, password):
                st.session_state.authenticated = True
                st.session_state.username = username
                st.success("Logged in.")
                st.rerun()
            else:
                st.error("Invalid username or password.")
    with tab2:
        with st.form("create_user"):
            new_username = st.text_input("New username")
            new_password = st.text_input("New password", type="password")
            submitted = st.form_submit_button("Create User")
        if submitted:
            ok, msg = create_user(new_username, new_password)
            st.success(msg) if ok else st.error(msg)


if not st.session_state.authenticated:
    login_page()
    st.stop()

with st.sidebar:
    st.markdown(f"# 📚 {APP_NAME}")
    st.caption(f"Logged in as {st.session_state.username}")
    selected = st.radio("Navigate", ["Dashboard", "New Project", "Writing Studio", "Story Bible", "Export Centre", "Settings"], index=["Dashboard", "New Project", "Writing Studio", "Story Bible", "Export Centre", "Settings"].index(st.session_state.page))
    st.session_state.page = selected
    if st.button("Logout"):
        for k in ["authenticated", "username", "current_project_id"]:
            st.session_state.pop(k, None)
        st.rerun()

hero(APP_NAME, "Plan, write, rewrite, approve, remember, and export your stories from one beautiful dashboard.")

page = st.session_state.page
if page == "Dashboard":
    render_dashboard(st.session_state.username)
elif page == "New Project":
    render_new_project(st.session_state.username)
elif page == "Writing Studio":
    render_writing_studio(st.session_state.provider)
elif page == "Story Bible":
    pid = st.session_state.get("current_project_id")
    if not pid:
        st.warning("Open a project first from the Dashboard.")
    else:
        render_story_bible(load_project_bundle(pid))
elif page == "Export Centre":
    pid = st.session_state.get("current_project_id")
    if not pid:
        st.warning("Open a project first from the Dashboard.")
    else:
        render_exports(load_project_bundle(pid), st.session_state.provider)
elif page == "Settings":
    render_settings()

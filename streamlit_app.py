from __future__ import annotations

import textwrap
import time
from datetime import date, timedelta

import streamlit as st
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv() #Loading enviorment file (API Key)

from app.extensions import db
from app.models import User, Subject, Topic, StudySession

"""from app.services.ocr.pipeline import process_syllabus_pdf"""

""""
from app.services import topics as topics_service
from app.services.scheduler.rebalance import (
    regenerate_schedule as _rebalance_regenerate_schedule,
    auto_detect_missed_sessions as _rebalance_auto_detect_missed_sessions,
)
"""


#Stlye Block 
APP_CSS = """
<style>
.block-container { padding-top: 2.5rem; max-width: 1400px; }
div[data-testid="stSidebarNav"] {
    display: none;
}
#Hides Streamlit's default multipage navigation

.chip {
    display:inline-block; padding: 0.2rem 0.65rem;
    font-size: 0.75rem; font-weight: 600; line-height: 1.4;
    white-space: nowrap;
    border: 1px solid;
}

#Scheduled button
.chip-scheduled {
    background-color: #E8F1FD;
    border-color: #90BFF0;
    color: #1D4E89;
}

#done button
.chip-done {
    background-color: #E6F6EC;
    border-color: #8FD3A8;
    color: #1E6B3C;
}


.chip-upnext {
    background-color: #FFF6DF;
    border-color: #F2CE6B;
    color: #8A6416;
}

.row-item {
    padding: 0.65rem 0.9rem;
    border-bottom: 1px solid;
}
.row-item:last-child { border-bottom: none; }
.row-title {
    font-weight: 600;
    font-size: 0.95rem;
    display: -webkit-box;
    -webkit-line-clamp: 1;
    -webkit-box-orient: vertical;
    overflow: hidden;
    text-overflow: ellipsis;
}
.row-meta { font-size: 0.82rem; }

.subject-eyebrow {
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.02em;
}
</style>
"""
#Not a multiline-string block, this is custom css against st css, thats why wrapped in Style Block

# st.html lets us inject our own css, INSTEAD of St's own css. 
def inject_css():
    st.html(APP_CSS) #could also have used ,st.markdown(APP_CSS, unsafe_allow_html=True), btw

def truncate(text: str, limit: int = 70) -> str: 
    text = (text or "").strip() #Reminder - strip removes leading or trailing spaces + new lines if we to be created, also text can be text or just empty space ""
    if len(text) <= limit:
        return text
    return textwrap.shorten(text, width=limit, placeholder="...")
    #Textwrap.shorten function --> this function returns a string of length = limit, with end text
    #ending with ...


#initialising Dictionary elements
GOAL_LABELS = {
    "competitive_exam": "Competitive Exam",
    "school_boards": "School Boards",
    "college_semester": "College Semester",
}
#Dictionary : Difficulty_Labels[1] = "Easy"
DIFFICULTY_LABELS = {1: "Easy", 2: "Medium", 3: "Hard"}

"""
#call forward functions :
# when default hours is called (e.g. _default_hours_for(tanish, 2)), it returns time set by the user (that is lets say tanish set medium hours = 100)
def _default_hours_for(user, difficulty: int) -> float:
    return topics_service.default_hours_for(user, difficulty)
"""  #I havent defined topics_Service yet


#st.session_state - Just an empty Dictionary (temporary memory) when the page first loads
# Every time a user clicks a button or interacts with a Streamlit app, the entire Python script reruns from top to bottom. To prevent the app from completely forgetting what the user was doing, Streamlit uses a special storage Dictionary called st.session_state 
def init_state():
    defaults = { # defaults defines the starting configuration for a fresh user session
        "user_id": None, #which user is logged in rn
        "nav": "schedule", #The tab opened rn
        "auth_mode": "login", #whether they are signing in
        "onboarding_topics": [], 
        "onboarding_auto_parsed": False,
        "onboarding_upload_failed": False,
        "pomo_running": False,
        "pomo_blocks": [],
        "pomo_block_index": 0,
        "pomo_seconds_left": 0,
        "pomo_topic_id": None,
        "pomo_started": False,
    }
    #This function sets up that default session state 
    for k, v in defaults.items(): #dictionary.items(), generally used in for loops to iterate each (key,value) pair over dictionary elements
        if k not in st.session_state: 
            st.session_state[k] = v 
    #when the user refreshes the browser, or quits the browser ; only then, this memory is wiped out

#Info about Current User - e.g. it returns who is currently using the app (that is, it returns user row)
def current_user():
    if st.session_state.get("user_id") is None:
        return None # breaks from here if no one is logged in
    user = User.query.get(st.session_state.user_id) #sql alchemy : User.query.get (user(table).query.get(fetch))
    #user = user row from the table : user. (that is our user table have : name, email, password_hash)

    if user is None: #user id exist, but user deleted the acc
        st.session_state.user_id = None

    return user


def logout():
    st.session_state.user_id = None
    st.session_state.nav = "schedule"


#AUTHENTICATION PAGE 
def render_auth():
    left, right = st.columns([1, 1], gap="large") #divided into two with equal ratio with a wide gap between them

    with left:
        st.markdown(
            "<div style='font-size:1.7rem; font-weight:600;'>Smart Study Planner</div>",
            unsafe_allow_html=True,
        )
        st.caption("Adaptive, evidence-based")
        st.markdown(
            "#### A study plan that adapts to your time, your topics, "
            "and your exam dates."
        )
        with st.container(border=True):
            st.markdown("**Data Structures and Algorithms**")
            st.caption("90 min · Scheduled for today")
            st.markdown('<span class="chip chip-upnext">Up next</span>', unsafe_allow_html=True)
            st.progress(0.67)


    with right:
        mode = st.radio(
            "mode", ["Log in", "Sign up"],
            index=0 if st.session_state.auth_mode == "login" else 1,
            horizontal=True, label_visibility="collapsed", #label like below one : what are u studying for
        )
        st.session_state.auth_mode = "login" if mode == "Log in" else "signup"

        if st.session_state.auth_mode == "signup":
            st.markdown("#### Create your account")
            st.caption(
                "Start with your subjects and deadlines — your first "
                "schedule takes under two minutes to generate."
            )
            with st.form("signup_form"):
                name = st.text_input("Full name", placeholder="e.g. Tanish Jaiswal")
                email = st.text_input("Email address", placeholder="Tanish@outlook.com")
                password = st.text_input("Password", type="password", placeholder="••••••••••")
                st.caption("At least 8 characters.")
                goal = st.radio(
                    "What are you studying for?",
                    options=list(GOAL_LABELS.keys()),
                    format_func=lambda g: GOAL_LABELS[g],
                    horizontal=True,
                )
                submitted = st.form_submit_button("Create account", use_container_width=True, type="primary")

            if submitted: #USER clicks on submit (if str : = if true :)
                name = (name or "").strip()
                email = (email or "").strip().lower()
                password = password or ""
                if not name:
                    st.error("You forgot to type your name")
                elif not email:
                    st.error("A valid email is required")
                elif len(password) < 8:
                    st.error("password must require at least 8 characters")
                elif User.query.filter_by(email=email).first() is not None:
                    st.error("An account with that email already exists.")
                else:
                    user = User( #we imported User class above, we are intialising an instance here btw
                        name=name, email=email,
                        password_hash=generate_password_hash(password),
                        goal=goal,
                    )
                    db.session.add(user) #session = read or write
                    db.session.commit()
                    st.session_state.user_id = user.id
                    st.session_state.nav = "schedule"
                    st.rerun()

            st.caption("Already have an account? Switch to **Log in** above.")

        else:
            st.markdown("#### Welcome back")
            st.caption("Log in to pick up right where your plan left off.")
            with st.form("login_form"):
                email = st.text_input("Email address", placeholder="you@example.com")
                password = st.text_input("Password", type="password", placeholder="••••••••••")
                submitted = st.form_submit_button("Log in", use_container_width=True, type="primary")

            if submitted:
                email = (email or "").strip().lower()
                password = password or ""
                user = User.query.filter_by(email=email).first() 
                if user is None or not check_password_hash(user.password_hash, password):
                    st.error("Invalid email or password.")
                else:
                    st.session_state.user_id = user.id
                    st.session_state.nav = "schedule"
                    st.rerun()

            st.caption("New here? Switch to **Sign up** above.")


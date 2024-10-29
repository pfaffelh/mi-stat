import streamlit as st
from streamlit_extras.switch_page_button import switch_page 
import time
import pymongo
import pandas as pd
from bson import ObjectId


# Seiten-Layout
st.set_page_config(page_title="STAT", page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)

# check if session_state is initialized if not change to main page
if 'logged_in' not in st.session_state:
    switch_page("STAT")

from misc.config import *
import misc.util as util
import misc.tools as tools

tools.delete_temporary()

# load css styles
from misc.css_styles import init_css
init_css()

# make all neccesary variables available to session_state
# setup_session_state()

# Navigation in Sidebar anzeigen
tools.display_navigation()

# Es geht hier vor allem um diese Collection:
collection = util.stat_semester

if st.session_state.page != "Statistik":
    st.session_state.edit = ""
st.session_state.page = "Statistik"

# Ab hier wird die Webseite erzeugt
if st.session_state.logged_in:
    st.header("Semester-Statistiken Grafiken")

else:
    switch_page("STAT")

st.sidebar.button("logout", on_click = tools.logout)



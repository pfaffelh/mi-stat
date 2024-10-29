import streamlit as st
import pymongo
import time

st.set_page_config(page_title="STAT", page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)

from misc.config import *
import misc.util as util
import misc.tools as tools

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# load css styles
from misc.css_styles import init_css
init_css()

if st.session_state.logged_in:
    pg = st.navigation({
        "Statistiken": [
            st.Page("pages/01_Semester.py", title="Semester"),
            st.Page("pages/01_Semester_edit.py", title="Semester"),
            st.Page("pages/02_Veranstaltung.py", title="Veranstaltung"),
            st.Page("pages/02_Veranstaltung_edit.py", title="Veranstaltung"),
        ],
        "Grafiken": [
            st.Page("pages/01_Semester_Grafik.py", title="Semester"),
            st.Page("pages/02_Veranstaltung_Grafik.py", title="Veranstaltung"),
        ],
    }, position = "hidden")
    st.markdown("<style>.st-emotion-cache-16txtl3 { padding: 2rem 2rem; }</style>", unsafe_allow_html=True)
    with st.sidebar:
        st.image("static/ufr.png", use_column_width=True)
        semesters = list(util.semester.find(sort=[("kurzname", pymongo.DESCENDING)]))
        st.session_state.semester_id = st.selectbox(label="Semester", options = [x["_id"] for x in semesters], index = [s["_id"] for s in semesters].index(st.session_state.semester_id), format_func = (lambda a: util.semester.find_one({"_id": a})["name_de"]), placeholder = "Wähle ein Semester", label_visibility = "collapsed", key = "master_semester_choice")
 
        st.write("<hr style='height:1px;margin:0px;;border:none;color:#333;background-color:#333;' /> ", unsafe_allow_html=True)
        st.page_link("pages/01_Semester.py", label="Semester")
        st.page_link("pages/02_Veranstaltung.py", label="Veranstaltung")
        st.write("<hr style='height:1px;margin:0px;;border:none;color:#333;background-color:#333;' /> ", unsafe_allow_html=True)
        st.page_link("pages/01_Semester_Grafik.py", label="Semester Grafik")
        st.page_link("pages/02_Veranstaltung_Grafik.py", label="Veranstaltung Grafik")
        st.write("<hr style='height:1px;margin:0px;;border:none;color:#333;background-color:#333;' /> ", unsafe_allow_html=True)

else:
    pg = st.navigation([st.Page("login.py", title="Log in", icon=":material/login:")])

pg.run()






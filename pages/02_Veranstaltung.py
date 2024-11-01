import streamlit as st
import time
import pymongo
import pandas as pd
from bson import ObjectId

# check if session_state is initialized if not change to main page
if 'logged_in' not in st.session_state:
    st.switch_page("STAT.py")

from misc.config import *
import misc.util as util
import misc.tools as tools

#tools.delete_temporary()

# load css styles
from misc.css_styles import init_css
init_css()

# make all neccesary variables available to session_state
# setup_session_state()

# Navigation in Sidebar anzeigen
# tools.display_navigation()

# Es geht hier vor allem um diese Collection:
collection = util.stat_veranstaltung

if st.session_state.page != "veranstaltung":
    st.session_state.edit = ""
st.session_state.page = "veranstaltung"

# Ab hier wird die Webseite erzeugt
if st.session_state.logged_in:
    st.header("Veranstaltungs-Statistiken")
    st.write("Dies sind Statistiken für Veranstaltungen, die eventuell von einem Studiengang abhängen dürfen. Beispiele sind Belegzahlen.")
    st.write(" ")
    if st.button('**Neue Statistik hinzufügen**'):
        st.session_state.edit = "new"
        st.session_state.expanded = "grunddaten"
        st.switch_page("pages/01_Veranstaltung_edit.py")

    stat = list(util.stat_veranstaltung.find({}, sort = [("rang", pymongo.ASCENDING)]))

    for x in stat:
        co1, co2, co3 = st.columns([1,1,23]) 
        with co1: 
            st.button('↓', key=f'down-{x["_id"]}', on_click = tools.move_down, args = (collection, x, ))
        with co2:
            st.button('↑', key=f'up-{x["_id"]}', on_click = tools.move_up, args = (collection, x, ))
        with co3:
            abk = f"{x['name'].strip()}"
            submit = st.button(abk, key=f"edit-{x['_id']}")
        if submit:
            st.session_state.edit = x["_id"]
            st.switch_page("pages/02_Veranstaltung_edit.py")

else:
    st.switch_page("STAT.py")

st.sidebar.button("logout", on_click = tools.logout)



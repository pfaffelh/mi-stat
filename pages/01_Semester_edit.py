import streamlit as st
from streamlit_extras.switch_page_button import switch_page 
import pandas as pd
import time
import pymongo
from bson import ObjectId

def kurzname_of_id(id):
    try:
        x = util.semester.find_one({"_id": id})["kurzname"]
    except:
        x = util.studiengang.find_one({"_id": id})["kurzname"]        
    return x

def id_of_kurzname(kurzname):
    x = util.semester.find_one({"kurzname": kurzname})["_id"]
    return x


# Seiten-Layout
st.set_page_config(page_title="STAT", page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)

# check if session_state is initialized if not change to main page
if 'logged_in' not in st.session_state:
    switch_page("STAT")

from misc.config import *
import misc.util as util
from misc.util import logger
import misc.tools as tools

tools.delete_temporary()

# load css styles
from misc.css_styles import init_css
init_css()

# Navigation in Sidebar anzeigen
tools.display_navigation()

# Es geht hier vor allem um diese Collection:
collection = util.stat_semester

new_entry = False

# Ab hier wird die Webseite erzeugt
if st.session_state.logged_in:
    st.header("Semesterabhängige Statistik")

    # check if entry can be found in database
    if st.session_state.edit == "new":
        new_entry = True
        x = st.session_state.new[collection]
        x["semester"] = [st.session_state.semester_id]
        x["_id"] = "new"

    else:
        x = collection.find_one({"_id": st.session_state.edit})
        st.subheader(tools.repr(collection, x["_id"], False))
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Zurück ohne Speichern"):
            switch_page("Statistik")
    with col2:
        with st.popover('Statistik löschen'):
            if not new_entry:
                st.write("Eintrag wirklich löschen?")
                colu1, colu2, colu3 = st.columns([1,1,1])
                with colu1:
                    submit = st.button(label = "Ja", type = 'primary', key = f"delete-{x['_id']}")
                if submit: 
                    tools.delete_item(collection, x["_id"])
                with colu3: 
                    st.button(label="Nein", on_click = st.success, args=("Nicht gelöscht!",), key = f"not-deleted-{x['_id']}")

    with st.form(f'ID-{x["_id"]}'):
        name=st.text_input('Name', x["name"], key = f"name_{x['_id']}")
        kommentar=st.text_input('Kommentar', x["kommentar"], key = f"kommentar_{x['_id']}")

        semester_list = [s["_id"] for s in list(util.semester.find(sort = [("kurzname", pymongo.DESCENDING)]))]

        for s in util.semester:
            st.write(repr(util.semester, s, False, True))
            for item in [item for item in x["stat"] if item["semester"] == s]:
                if len(item["studiengang"]) == 0:
                    st.write("Alle Studiengänge")
                else:
                    st.write(", ".join([repr(util.studiengang, s, False, True) for s in stu]))
                st.number_input(item["wert"])
                st.text_input(item["kommentar"])

            stu_list = st.multiselect("Studiengänge", [x["_id"] for x in util.studiengang.find({"sichtbar": True}, sort = [("name", pymongo.ASCENDING)])], [], format_func = (lambda a: tools.repr(util.studiengang, a, False)), placeholder = "Bitte auswählen", key = f"studiengang_{x['_id']}")
            stu = list(util.studiengang.find({"_id": {"$in": stu_list}}, sort=[("name", pymongo.ASCENDING)]))
            stu_list = [str(x["_id"]) for s in stu]
            

            # show stat for available entries, which can be edited or deleted
            # Show extra line where one can choose another studiengang and entry


        s_updated = ({"name": name, "semester": semester_list, "studiengang": [ObjectId(s) for s in stu_list], "stat": stat, "kommentar": kommentar})

        submit = st.form_submit_button('Speichern', type = 'primary', key = f"submit_{x['_id']}")
        if submit:
            tools.update_confirm(collection, s, s_updated, )
            time.sleep(.1)
        
            
            
    st.write("### Veranstaltungsstatistiken")
    with st.expander(f'Neue Statistik anlegen'):
        st.write("")
        
        
        
        if submit:
            if new_entry:
                tools.new(collection, ini = x_updated, switch=False)
            else: 
                tools.update_confirm(collection, x, x_updated, )
            time.sleep(2)
            st.session_state.edit = ""
            switch_page("personen")
        



else:
    switch_page("VVZ")

st.sidebar.button("logout", on_click = tools.logout)

import streamlit as st
import time
import pymongo

def kurzname_of_id(id):
    try:
        x = util.semester.find_one({"_id": id})["kurzname"]
    except:
        x = util.studiengang.find_one({"_id": id})["kurzname"]        
    return x

def id_of_kurzname(kurzname):
    x = util.semester.find_one({"kurzname": kurzname})["_id"]
    return x

# check if session_state is initialized if not change to main page
if 'logged_in' not in st.session_state:
    st.switch_page("STAT.py")

from misc.config import *
import misc.util as util
from misc.util import logger
import misc.tools as tools

tools.delete_temporary()

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
            st.switch_page("pages/01_Semester.py")
    with col2:
        with st.popover('Statistik löschen'):
            if not new_entry:
                st.write("Eintrag wirklich löschen?")
                colu1, colu2, colu3 = st.columns([1,1,1])
                with colu1:
                    submit = st.button(label = "Ja", type = 'primary', key = f"delete-{x['_id']}")
                if submit: 
                    tools.update_one(collection, x["_id"])
                with colu3: 
                    st.button(label="Nein", on_click = st.success, args=("Nicht gelöscht!",), key = f"not-deleted-{x['_id']}")

    with st.expander("Grunddaten", expanded = True if st.session_state.expanded == "grunddaten" else False):
        col0, col1 = st.columns([3,1])
        name=col0.text_input('Name', x["name"], key = f"name_{x['_id']}")
        einheit=col1.text_input('Einheit', x["einheit"], key = f"einheit_{x['_id']}")
        kommentar=st.text_area('Kommentar', x["kommentar"], key = f"kommentar_{x['_id']}")
        x_updated = {"name" : name, "kommentar": kommentar}
        st.session_state.expanded = ""
        save = st.button('Speichern', on_click = tools.update_or_insert, args = (collection, x, x_updated), key = f"save_grunddaten")

    st.write("### Alle Werte")
    
    semester_list = [s["_id"] for s in list(util.semester.find(sort = [("kurzname", pymongo.DESCENDING)]))]

    col = st.columns([1,3,1,5,1,1])
    col[0].write("Semester")
    col[1].write("Studiengänge")
    col[2].markdown(f"<div style='text-align: right'>Wert</div>", unsafe_allow_html=True)
    col[3].write("Kommentar")
    for s in semester_list:
        if s in [item["semester"] for item in x["stat"]]:
            write_sem = True
            for i, item in enumerate(x["stat"]):
                if item["semester"] == s:
                    if write_sem:
                        st.write("<hr style='height:1px;margin:0px;border:none;color:#333;background-color:#333;' /> ", unsafe_allow_html=True)
                    col = st.columns([1,3,1,5,1,1])
                    if write_sem:
                        col[0].write(tools.repr(util.semester, s, False, True))
                        write_sem = False

                if st.session_state.subedit == i:
                    dict = {"semester" : s}  
                    stu_list = col[1].multiselect("Studiengänge", [x["_id"] for x in util.studiengang.find({ "$or" : [{ "_id" : { "$in" : item["studiengang"]}}, {"sichtbar": True}]}, sort = [("name", pymongo.ASCENDING)])], [], format_func = (lambda a: tools.repr(util.studiengang, a, False, True)), placeholder = "Bitte auswählen", key = f"studiengang_{i}", label_visibility="hidden")
                    stu = list(util.studiengang.find({"_id": {"$in": stu_list}}, sort=[("name", pymongo.ASCENDING)]))
                    dict["studiengang"] = [s["_id"] for s in stu]
                    dict["wert"] = col[2].number_input("Wert", value = item["wert"], label_visibility="hidden", step=1.0, key = f"wert_{i}")
                    dict["kommentar"] = col[3].text_input(item["kommentar"], label_visibility="hidden", key = f"kommentar_{i}")

                    with col[4]:
                        save = st.button('Speichern', key = f"save_subedit_{i}")
                        if save:
                            st.write(i)
                            dict["wert"] = float(dict["wert"])
                            collection.update_one({"_id" : x["_id"]}, { "$set" : { f"stat.{i}" : dict}})
                            st.session_state.subedit = ""
                            st.rerun()
                    with col[5]:
                        with st.popover('Löschen', use_container_width=True):
                            colu1, colu2, colu3 = st.columns([1,1,1])
                            with colu1:
                                submit = st.button(label = "Wirklich löschen!", type = 'primary', key = f"delete-{i}")
                            if submit: 
                                tools.delete_item(collection, x["_id"])
                            with colu3: 
                                st.button(label="Abbrechen", on_click = st.success, args=("Nicht gelöscht!",), key = f"not-deleted-{i}")


                else:
                    col[1].write(", ".join([tools.repr(util.studiengang, id, False, True) for id in item["studiengang"]])) 
                    wert = f"{item['wert']:.2g}"
                    col[2].markdown(f"<div style='text-align: right'>{wert}</div>", unsafe_allow_html=True)
                
                    col[2].write()
                    col[3].write(item["kommentar"])
                    edit = col[4].button("Bearbeiten", use_container_width=True, key = f"subedit_sem_{kurzname_of_id(s)}_{i}")
                    if edit:
                        st.session_state.subedit = i
                        st.rerun()
                    
                                
            # show stat for available entries, which can be edited or deleted
            # Show extra line where one can choose another studiengang and entry
            
    st.write("### Neuer Wert")
    col = st.columns([1,3,1,5,1,1], vertical_alignment="center")    
    dict = {}
    semesters = list(util.semester.find(sort=[("kurzname", pymongo.DESCENDING)]))
    dict["semester"] = col[0].selectbox(label="Semester", options = [x["_id"] for x in semesters], index = [s["_id"] for s in semesters].index(st.session_state.semester_id), format_func = (lambda a: util.semester.find_one({"_id": a})["kurzname"]), placeholder = "Wähle ein Semester", label_visibility = "collapsed", key = "semester_choice")
    stu_list = col[1].multiselect("Studiengänge", [x["_id"] for x in util.studiengang.find({ "$or" : [{"sichtbar": True}]}, sort = [("name", pymongo.ASCENDING)])], [], format_func = (lambda a: tools.repr(util.studiengang, a, False)), placeholder = "Bitte auswählen", label_visibility = "collapsed", key = f"studiengang_{x['_id']}")
    stu = list(util.studiengang.find({"_id": {"$in": stu_list}}, sort=[("name", pymongo.ASCENDING)]))
    dict["studiengang"] = [s["_id"] for s in stu]
    dict["wert"] = col[2].number_input("Wert", value = None, label_visibility = "collapsed", step=1)
    dict["kommentar"] = col[3].text_input("", label_visibility = "collapsed")
    
    submit = st.button('Speichern', type = 'primary', key = f"new_entry_{x['_id']}")
    if submit:
        st.write(dict)
        if dict["wert"] is not None:
            dict["wert"] = float(dict["wert"])
            collection.update_one({"_id" : x["_id"]}, { "$push" : {"stat" : dict}})
            st.success("Eintrag übernommen!")
            dict = {}
            st.rerun()
        else:
            st.warning("Das Feld Wert ist leer. Eintrag nicht übernommen!")
        time.sleep(0.1)
    
        

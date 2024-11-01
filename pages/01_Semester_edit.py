import streamlit as st
import time
import pymongo

from misc.config import *
import misc.util as util
from misc.util import logger
import misc.tools as tools

col_list = [1,2,1,5,1,1]

def save_new_entry(stat, dict):
    if dict["wert"] is not None:
        dict["wert"] = float(dict["wert"])
        stat.append(dict)
        for s in stat:
            s["semester_name"] = tools.repr(util.semester, s["semester"], False, True)
            s["studiengang_name"] = ", ".join([tools.repr(util.studiengang, id, False, True) for id in s["studiengang"]])
        stat = sorted(stat, key=lambda x: (x["semester_name"], x["studiengang_name"], x["wert"]))
        for s in stat:
            s.pop("semester_name")
            s.pop("studiengang_name")

        collection.update_one({"_id" : x["_id"]}, { "$set" : {"stat" : stat}})
        st.toast("Eintrag übernommen!")
        
        st.session_state.dict = {}
#        st.session_state["dict_new_wert"] = None
#        st.session_state["dict_new_studiengang"] = []
#        st.session_state["dict_new_kommentar"] = ""
    else:
        st.toast("Das Feld Wert ist leer. Eintrag nicht übernommen!")
    time.sleep(0.4)

# Eine Statistik soll nur dann dargestellt werden, wenn alle Studiengänge angezeigt werden sollen
def show(item):
    return (item["studiengang"] == [] or st.session_state.studiengang == [] or len([stu for stu in item["studiengang"] if stu in st.session_state.studiengang])>0)
    
    
# check if session_state is initialized if not change to main page
if 'logged_in' not in st.session_state:
    st.switch_page("STAT.py")

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
#        x["semester"] = [st.session_state.semester_id]
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
        x_updated = {"name" : name, "einheit": einheit, "kommentar": kommentar}
        st.session_state.expanded = ""
        save = st.button('Speichern', type = "primary", on_click = tools.update_or_insert, args = (collection, x, x_updated, False), key = f"save_grunddaten")

    
    st.write("### Alle Werte")
    
    st.write("Nur folgendes anzeigen: (Kein Eintrag bei _Studiengänge_ bedeutet _alle Studiengänge_.)")
    col0, col1, col2 = st.columns([1,1,1], vertical_alignment="bottom")
    with col0: 
        st.session_state.studiengang = st.multiselect("Studiengänge", [x["_id"] for x in util.studiengang.find({"sichtbar": True}, sort = [("name", pymongo.ASCENDING)])], [], format_func = (lambda a: tools.repr(util.studiengang, a, False, True)), placeholder = "alle", key = f"anzeige_studiengaenge")

    semesters = list(util.semester.find(sort=[("rang", pymongo.DESCENDING)]))
    with col1:
        st.write("von...")
        semester_id_von = st.selectbox(label="von", options = [x["_id"] for x in semesters], index = [s["_id"] for s in semesters].index(st.session_state.semester_id), format_func = (lambda a: util.semester.find_one({"_id": a})["kurzname"]), placeholder = "Wähle ein Semester", label_visibility = "collapsed", key = "semester_von")
        semester_von = util.semester.find_one({"_id": semester_id_von})
    with col2:
        st.write("...bis...")
        semester_id_bis = st.selectbox(label="bis", options = [x["_id"] for x in semesters], index = [s["_id"] for s in semesters].index(st.session_state.semester_id), format_func = (lambda a: util.semester.find_one({"_id": a})["kurzname"]), placeholder = "Wähle ein Semester", label_visibility = "collapsed", key = "semester_bis")
        semester_bis = util.semester.find_one({"_id": semester_id_bis})
    st.session_state.semester_auswahl = [s["_id"] for s in list(util.semester.find({"rang": {"$gte": semester_von["rang"], "$lte": semester_bis["rang"]}}))]
    
    st.divider()
    
    semester_list = [s["_id"] for s in list(util.semester.find(sort = [("kurzname", pymongo.DESCENDING)]))]


    col = st.columns(col_list)
    col[0].write("Semester")
    col[1].write("Studiengänge")
    col[2].markdown(f"<div style='text-align: right'>Wert</div>", unsafe_allow_html=True)
    col[3].write("Kommentar")
    
    st.write("### Neuer Wert")
    with st.form("Neuer Wert", clear_on_submit=True):
        col = st.columns(col_list, vertical_alignment="center")    
        st.session_state.dict = {}
        semesters = list(util.semester.find(sort=[("kurzname", pymongo.DESCENDING)]))
        st.session_state.dict["semester"] = col[0].selectbox(label="Semester", options = st.session_state.semester_auswahl, index = len(st.session_state.semester_auswahl)-1, format_func = (lambda a: util.semester.find_one({"_id": a})["kurzname"]), placeholder = "Wähle ein Semester", label_visibility = "collapsed", key = "dict_new_semester")
        stu_list = col[1].multiselect("Studiengänge", [x["_id"] for x in util.studiengang.find({"sichtbar": True}, sort = [("name", pymongo.ASCENDING)])], [], format_func = (lambda a: tools.repr(util.studiengang, a, False)), placeholder = "alle", label_visibility = "collapsed", key = "dict_new_studiengang")
        stu = list(util.studiengang.find({"_id": {"$in": stu_list}}, sort=[("name", pymongo.ASCENDING)]))
        st.session_state.dict["studiengang"] = [s["_id"] for s in stu]
        st.session_state.dict["wert"] = col[2].number_input("Wert", value = None, label_visibility = "collapsed", step=1, key = "dict_new_wert")
        st.session_state.dict["kommentar"] = col[3].text_input("", label_visibility = "collapsed", key = "dict_new_kommentar")
        submit = col[4].form_submit_button('Speichern', type = 'primary')
        if submit:
            save_new_entry(x["stat"], st.session_state.dict)
            st.rerun()


    for s in semester_list:
        if s in st.session_state.semester_auswahl and s in [item["semester"] for item in x["stat"]]:
            write_sem = True
            for i, item in enumerate(x["stat"]):
                if item["semester"] == s:
                    if show(item):
                        if write_sem:
                            st.write("<hr style='height:1px;margin:0px;border:none;color:#333;background-color:#333;' /> ", unsafe_allow_html=True)
                        col = st.columns(col_list, vertical_alignment="top" if st.session_state.subedit != i else "bottom")
                        if write_sem:
                            col[0].write(tools.repr(util.semester, s, False, True))
                            write_sem = False
                        if st.session_state.subedit == i:
                            st.session_state.dict = {"semester" : s, "studiengang" : item["studiengang"]}  
                            if item["studiengang"] == []:
                                col[1].write("alle")
                            else:
                                col[1].write(", ".join([tools.repr(util.studiengang, id, False, True) for id in item["studiengang"]])) 
                            #stu_list = col[1].multiselect("Studiengänge", [x["_id"] for x in util.studiengang.find({ "$or" : [{ "_id" : { "$in" : item["studiengang"]}}, {"sichtbar": True}]}, sort = [("name", pymongo.ASCENDING)])], [], format_func = (lambda a: tools.repr(util.studiengang, a, False, True)), placeholder = "alle", key = f"studiengang_{i}", label_visibility="hidden")
                            #stu = list(util.studiengang.find({"_id": {"$in": stu_list}}, sort=[("name", pymongo.ASCENDING)]))
                            #st.session_state.dict["studiengang"] = [s["_id"] for s in stu]
                            st.session_state.dict["wert"] = col[2].number_input("Wert", value = item["wert"], label_visibility="hidden", step=1.0, key = f"wert_{i}")
                            st.session_state.dict["kommentar"] = col[3].text_input(item["kommentar"], label_visibility="hidden", key = f"kommentar_{i}")

                            with col[4]:
                                save = st.button('Speichern', type = "primary")
                                if save:
                                    st.session_state.dict["wert"] = float(st.session_state.dict["wert"])
                                    collection.update_one({"_id" : x["_id"]}, { "$set" : { f"stat.{i}" : st.session_state.dict}})
                                    st.session_state.subedit = ""
                                    st.session_state.dict = {}                            
                                    st.rerun()
                            with col[5]:
                                with st.popover('Löschen', use_container_width=True):
                                    colu1, colu2, colu3 = st.columns([1,1,1])
                                    with colu1:
                                        submit = st.button(label = "Wirklich löschen!", type = 'primary', key = f"delete-{i}")
                                    if submit: 
                                        stat = x["stat"]
                                        del stat[i]
                                        collection.update_one({"_id" : x["_id"]}, { "$set" : { "stat" : stat}})
                                        collection.update_one({"_id" : x["_id"]}, { "$pull" : { "stat" : None}})
                                        st.session_state.subedit = ""                                
                                        st.rerun()
                                    with colu3: 
                                        st.button(label="Abbrechen", on_click = st.success, args=("Nicht gelöscht!",), key = f"not-deleted-{i}")

                        else:
                            if item["studiengang"] == []:
                                col[1].write("alle")
                            else:
                                col[1].write(", ".join([tools.repr(util.studiengang, id, False, True) for id in item["studiengang"]])) 
                            wert = item['wert']
                            col[2].markdown(f"<div style='text-align: right'>{wert}</div>", unsafe_allow_html=True)
                        
                            col[2].write()
                            col[3].write(item["kommentar"])
                            edit = col[4].button("Bearbeiten", use_container_width=True, key = f"subedit_sem_{tools.kurzname_of_id(s)}_{i}")
                            if edit:
                                st.session_state.subedit = i
                                st.rerun()

        
else:
    st.switch_page("STAT")

st.sidebar.button("logout", on_click = tools.logout)

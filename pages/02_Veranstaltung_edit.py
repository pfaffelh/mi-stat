import streamlit as st
import time
import pymongo
import altair as alt

col_list = [1,1,3,1,3,1,1]

def reset():
    st.session_state["dict_new_wert"] = None
    st.session_state["dict_new_studiengang"] = []
    st.session_state["dict_new_veranstaltung"] = None
    st.session_state["dict_new_kommentar"] = ""


def save_new_entry(stat, dict):
    if dict["wert"] is not None:
        dict["wert"] = float(dict["wert"])
        stat.append(dict)
        for s in stat:
            v = util.veranstaltung.find_one({"_id": s["veranstaltung"]})
            s["semester_name"] = tools.repr(util.semester, v["semester"], False, True)
            r = util.rubrik.find_one({"_id": v["rubrik"]})
            s["rubrik_rang"] = r["rang"]
            s["rang"] = v["rang"]
            s["studiengang_name"] = ", ".join([tools.repr(util.studiengang, id, False, True) for id in s["studiengang"]])
        stat = sorted(stat, key=lambda x: (x["semester_name"], x["studiengang_name"], x["rubrik_rang"], x["rang"]))
        for s in stat:
            s.pop("semester_name")
            s.pop("studiengang_name")
            s.pop("rang")
            s.pop("rubrik_rang")

        collection.update_one({"_id" : x["_id"]}, { "$set" : {"stat" : stat}})

        st.toast("Eintrag übernommen!")
        st.session_state.dict = {}
    else:
        st.toast("Das Feld Wert ist leer. Eintrag nicht übernommen!")
    time.sleep(0.4)

# Eine Statistik soll nur dann dargestellt werden, wenn alle Studiengänge angezeigt werden sollen
def show(item):
    cond0 = item["studiengang"] == []
    cond1 = st.session_state.studiengang == []
    cond2 = len([stu for stu in item["studiengang"] if stu in st.session_state.studiengang])>0
    v = util.veranstaltung.find_one({"_id": item["veranstaltung"]})
    cond3 = (v["semester"] in st.session_state.semester_auswahl)
    return (cond0 or cond1 or cond2) and cond3
    
# check if session_state is initialized if not change to main page
if 'logged_in' not in st.session_state:
    st.switch_page("STAT.py")

from misc.config import *
import misc.util as util
from misc.util import logger
import misc.tools as tools

tools.delete_temporary()

# Es geht hier vor allem um diese Collection:
collection = util.stat_veranstaltung

new_entry = False

# Ab hier wird die Webseite erzeugt
if st.session_state.logged_in:

    # check if entry can be found in database
    if st.session_state.edit == "new":
        new_entry = True
        x = st.session_state.new[collection]
#        x["semester"] = [st.session_state.semester_id]
        x["_id"] = "new"
    else:
        x = collection.find_one({"_id": st.session_state.edit})
    st.subheader(f"Veranstaltungs-Statistik {': ' + tools.repr(collection, x['_id'], False) if st.session_state.edit != 'new' else ''}")
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Zurück ohne Speichern"):
            st.switch_page("pages/02_Veranstaltung.py")
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

    col0, col1, col2, col3 = st.columns([1,2,2,2], vertical_alignment="bottom")
    col0.write("Nur folgendes anzeigen:")
    with col1:
        st.session_state.studiengang = st.multiselect("Studiengänge", [x["_id"] for x in util.studiengang.find({"sichtbar": True}, sort = [("name", pymongo.ASCENDING)])], [], format_func = (lambda a: tools.repr(util.studiengang, a, False, True)), placeholder = "alle", key = f"anzeige_studiengaenge")
        semesters = list(util.semester.find(sort=[("rang", pymongo.DESCENDING)]))
    with col2:
        st.write("von...")
        semester_id_von = st.selectbox(label="von", options = [x["_id"] for x in semesters], index = [s["_id"] for s in semesters].index(st.session_state.semester_id), format_func = (lambda a: util.semester.find_one({"_id": a})["kurzname"]), placeholder = "Wähle ein Semester", label_visibility = "collapsed", key = "semester_von")
        semester_von = util.semester.find_one({"_id": semester_id_von})
    with col3:
        st.write("...bis...")
        semester_id_bis = st.selectbox(label="bis", options = [x["_id"] for x in semesters], index = [s["_id"] for s in semesters].index(st.session_state.semester_id), format_func = (lambda a: util.semester.find_one({"_id": a})["kurzname"]), placeholder = "Wähle ein Semester", label_visibility = "collapsed", key = "semester_bis")
        semester_bis = util.semester.find_one({"_id": semester_id_bis})


    st.session_state.semester_auswahl = [s["_id"] for s in list(util.semester.find({"rang": {"$gte": semester_von["rang"], "$lte": semester_bis["rang"]}}))]
    
    st.divider()
    
    semester_list = [s["_id"] for s in list(util.semester.find(sort = [("kurzname", pymongo.DESCENDING)]))]

    col = st.columns(col_list)
    col[0].write("Semester")
    col[1].write("Studiengänge")
    col[2].write("Veranstaltung")
    col[3].markdown(f"<div style='text-align: right'>Wert</div>", unsafe_allow_html=True)
    col[4].write("Kommentar")

    ver = list(util.veranstaltung.find({"hp_sichtbar": True, "semester": { "$in" : st.session_state.semester_auswahl}}))    
    for v in ver:
        v["semester_name"] = tools.repr(util.semester, v["semester"], False, True)
        r = util.rubrik.find_one({"_id": v["rubrik"]})
        v["rubrik_rang"] = r["rang"]
    ver = [v["_id"] for v in sorted(ver, key=lambda x: (x["semester_name"], x["rubrik_rang"], x["rang"]))]
    
    with st.form("Neuer Wert", clear_on_submit=True):
        col = st.columns(col_list, vertical_alignment="center")    

        st.session_state.dict = {}
        stu_list = col[1].multiselect("Studiengänge", [x["_id"] for x in util.studiengang.find({"sichtbar": True}, sort = [("name", pymongo.ASCENDING)])], [], format_func = (lambda a: tools.repr(util.studiengang, a, False, True)), placeholder = "alle", label_visibility = "collapsed", key = "dict_new_studiengang")
        stu = list(util.studiengang.find({"_id": {"$in": stu_list}}, sort=[("name", pymongo.ASCENDING)]))
        st.session_state.dict["studiengang"] = [s["_id"] for s in stu]

        st.session_state.dict["veranstaltung"] = col[2].selectbox("Veranstaltung", ver, None, format_func = (lambda a: tools.repr(util.veranstaltung, a, False)), placeholder = "Bitte auswählen", label_visibility = "collapsed", key = "dict_new_veranstaltung")

        with col[3]:
            st.session_state.dict["wert"] = st.number_input("Wert", value = None, label_visibility = "collapsed", step=1, key = "dict_new_wert")
        st.session_state.dict["kommentar"] = col[4].text_input("Kommentar", "", label_visibility = "collapsed", key = "dict_new_kommentar")
        submit = col[5].form_submit_button('Speichern', type = 'primary')
        if submit:
            # Wenn es den Eintrag für diese Veranstaltung und diesen Studiengang schon gibt, wird der neue Eintrag abgelehnt:
            target = { "veranstaltung" : st.session_state.dict["veranstaltung"], "studiengang" : st.session_state.dict["studiengang"]}
            if any(all(item.get(k) == v for k, v in target.items()) for item in x["stat"]):
                st.toast("Eintrag für diesen Studiengang in dieser Veranstaltung bereits vorhanden. Eintrag abgelehnt!")
                time.sleep(2)
            else:
                save_new_entry(x["stat"], st.session_state.dict)
            st.rerun()

    for s in semester_list:
        if s in st.session_state.semester_auswahl and s in [v["semester"] for v in list(util.veranstaltung.find({"_id" : { "$in": [item["veranstaltung"] for item in x["stat"]]}}))]:
            write_sem = True
            for i, item in enumerate(x["stat"]):
                # falls s das Semester ist, in dem die Veranstaltung gehalten wurde:
                if s in [v["semester"] for v in [util.veranstaltung.find_one({"_id" : item["veranstaltung"]})]]:
                    if show(item):
                        if st.session_state.subedit == i:
                            with st.form("edit_entry"):
                                if write_sem:
                                    st.write("<hr style='height:1px;margin:0px;border:none;color:#333;background-color:#333;' /> ", unsafe_allow_html=True)
                                col = st.columns(col_list, vertical_alignment="top" if st.session_state.subedit != i else "bottom")
                                if write_sem:
                                    col[0].write(tools.repr(util.semester, s, False, True))
                                    write_sem = False
                                    st.session_state.dict = {"studiengang" : item["studiengang"], "veranstaltung" : item["veranstaltung"]}

                                if item["studiengang"] == []:
                                    col[1].write("alle")
                                else:
                                    col[1].write(", ".join([tools.repr(util.studiengang, id, False, True) for id in item["studiengang"]])) 
                                
                                #stu_list = col[1].multiselect("Studiengänge", [x["_id"] for x in util.studiengang.find({ "$or" : [{ "_id" : { "$in" : item["studiengang"]}}, {"sichtbar": True}]}, sort = [("name", pymongo.ASCENDING)])], [], format_func = (lambda a: tools.repr(util.studiengang, a, False, True)), placeholder = "Bitte auswählen", key = f"studiengang_{i}", label_visibility="hidden")
                                #stu = list(util.studiengang.find({"_id": {"$in": stu_list}}, sort=[("name", pymongo.ASCENDING)]))
                                #st.session_state.dict["studiengang"] = [s["_id"] for s in stu]
                                
                                col[2].write(tools.repr(util.veranstaltung, item["veranstaltung"], False))
                                #ver = [x["_id"] for x in list(util.veranstaltung.find({"semester": s}))]
                                #st.session_state.dict["veranstaltung"] = col[2].selectbox(label="Veranstaltung", options = ver, index = ver.index(item["veranstaltung"]), format_func = (lambda a: tools.repr(util.veranstaltung, a)), placeholder = "Wähle eine Veranstaltung", label_visibility = "hidden", key = "Veranstaltung edit")
                                
                                st.session_state.dict["wert"] = col[3].number_input("Wert", value = item["wert"], label_visibility="hidden", step=1.0, key = f"wert_{i}")

                                st.session_state.dict["kommentar"] = col[4].text_input("Kommentar", item["kommentar"], label_visibility="hidden", key = f"kommentar_{i}")

                                with col[5]:
                                    save = st.form_submit_button('Speichern', type = "primary")
                                    if save:
                                        target = { "veranstaltung" : st.session_state.dict["veranstaltung"], "studiengang" : st.session_state.dict["studiengang"]}
                                        # Wenn es den Eintrag für diese Veranstaltung und diesen Studiengang schon gibt, wird der neue Eintrag abgelehnt:
                                        if any(all(item.get(k) == v for k, v in target.items()) for item in stat):
                                            st.error("Eintrag für diesen Studiengang in dieser Veranstaltung bereits vorhanden. Eintrag abgelehnt!")
                                        else:
                                            st.session_state.dict["wert"] = float(st.session_state.dict["wert"])
                                            collection.update_one({"_id" : x["_id"]}, { "$set" : { f"stat.{i}" : st.session_state.dict}})
                                        st.session_state.subedit = ""
                                        st.session_state.dict = {}                            
                                        time.sleep(0.4)
                                        st.rerun()
                                with col[6]:
                                    with st.popover('Löschen', use_container_width=True):
                                        colu1, colu2, colu3 = st.columns([1,1,1])
                                        with colu1:
                                            submit = st.form_submit_button(label = "Wirklich löschen!", type = 'primary')
                                        if submit: 
                                            stat = x["stat"]
                                            del stat[i]
                                            collection.update_one({"_id" : x["_id"]}, { "$set" : { "stat" : stat}})
                                            collection.update_one({"_id" : x["_id"]}, { "$pull" : { "stat" : None}})
                                            st.session_state.subedit = ""                                
                                            st.rerun()
                                        with colu3: 
                                            st.form_submit_button(label="Abbrechen", on_click = st.success, args=("Nicht gelöscht!",))

                        else:
                            if write_sem:
                                st.write("<hr style='height:1px;margin:0px;border:none;color:#333;background-color:#333;' /> ", unsafe_allow_html=True)
                            col = st.columns(col_list, vertical_alignment="top" if st.session_state.subedit != i else "bottom")
                            if write_sem:
                                col[0].write(tools.repr(util.semester, s, False, True))
                                write_sem = False
                                st.session_state.dict = {"studiengang" : item["studiengang"], "veranstaltung" : item["veranstaltung"]}
                            if item["studiengang"] == []:
                                col[1].write("alle")
                            else:
                                col[1].write(", ".join([tools.repr(util.studiengang, id, False, True) for id in item["studiengang"]])) 
                            wert = item['wert']
                            col[2].write(tools.repr(util.veranstaltung, item["veranstaltung"], False))
                            col[3].markdown(f"<div style='text-align: right'>{wert}</div>", unsafe_allow_html=True)
                        
                            col[4].write(item["kommentar"])
                            edit = col[5].button("Bearbeiten", use_container_width=True, key = f"subedit_sem_{tools.kurzname_of_id(s)}_{i}")
                            if edit:
                                st.session_state.subedit = i
                                st.rerun()
            
    
        
else:
    st.switch_page("STAT")

st.sidebar.button("logout", on_click = tools.logout)



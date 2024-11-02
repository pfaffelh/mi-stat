import streamlit as st
import pymongo
import pandas as pd
import altair as alt

# check if session_state is initialized if not change to main page
if 'logged_in' not in st.session_state:
    st.switch_page("STAT")

from misc.config import *
import misc.util as util
import misc.tools as tools

# load css styles
from misc.css_styles import init_css
init_css()

# make all neccesary variables available to session_state
# setup_session_state()

# Es geht hier vor allem um diese Collection:
collection = util.stat_semester

if st.session_state.page != "Grafik":
    st.session_state.edit = ""
st.session_state.page = "Grafik"

# Ab hier wird die Webseite erzeugt
if st.session_state.logged_in:
    st.header("Grafiken")

    col0, col1, col2 = st.columns([2,2,2])
    col0.write("Wieviele Grafiken sollen erstellt werden?")
    number_semester = col1.selectbox("Anzahl Grafiken zu Semester-Statistiken", [0,1,2], 1)
    number_veranstaltung = col2.selectbox("Anzahl Grafiken zu Veranstaltungs-Statistiken", [0,1,2], 0)
    number = number_semester + number_veranstaltung

    col0, col1, col2 = st.columns([2,2,2])
    col0.write("Für welche Semester?")
    semesters = list(util.semester.find(sort=[("rang", pymongo.DESCENDING)]))
    semester_id_von = col1.selectbox(label="von", options = [x["_id"] for x in semesters], index = [s["_id"] for s in semesters].index(st.session_state.semester_id), format_func = (lambda a: util.semester.find_one({"_id": a})["kurzname"]), placeholder = "Wähle ein Semester", key = f"choose_semester_von")
    semester_von = util.semester.find_one({"_id": semester_id_von})
    semester_id_bis = col2.selectbox(label="bis", options = [x["_id"] for x in semesters], index = [s["_id"] for s in semesters].index(st.session_state.semester_id), format_func = (lambda a: util.semester.find_one({"_id": a})["kurzname"]), placeholder = "Wähle ein Semester", key = f"choose_semester_bis")
    semester_bis = util.semester.find_one({"_id": semester_id_bis})
    st.session_state.semester_auswahl = [s["_id"] for s in list(util.semester.find({"rang": {"$gte": semester_von["rang"], "$lte": semester_bis["rang"]}}))]

    if number:
        col = st.columns([1 for _ in range(number)])
    for i in range(number):
        with col[i]:
            if i < number_semester:
                st.subheader("Semester-Statistik")
                collection = util.stat_semester
            else:
                st.subheader("Veranstaltungs-Statistik")
                collection = util.stat_veranstaltung
            st.selectbox("Statistik", [x["_id"] for x in list(collection.find(sort = [("rang", pymongo.ASCENDING)]))], None, format_func=(lambda a: tools.repr(collection, a, False)), key = f"stat_choose_{i}" )
            st.multiselect("Studiengänge", [x["_id"] for x in util.studiengang.find({"sichtbar": True}, sort = [("name", pymongo.ASCENDING)])], [], format_func = (lambda a: tools.repr(util.studiengang, a, False, True)), placeholder = "alle", key = f"studiengang_choose_{i}")

            if i >= number_semester:
                st.text_input("Muster", "", placeholder = "Z.B. Seminar", key = f"muster_{i}")

    if number:
        col = st.columns([1 for _ in range(number)])
    df = chart = [1 for _ in range(number)]
    for i in range(number):
        if i < number_semester:
            collection = util.stat_semester
        else:
            collection = util.stat_veranstaltung
        with col[i]:
            st.divider()
            if st.session_state[f"stat_choose_{i}"] is not None:
                stat = collection.find_one({"_id" : st.session_state[f"stat_choose_{i}"]})["stat"]
                stat_choice = []
                append = False
                for j, item in enumerate(stat):
                    if collection == util.stat_veranstaltung:
                        item["semester"] = util.semester.find_one({"_id": util.veranstaltung.find_one({"_id" : item["veranstaltung"]})["semester"]})["_id"]
                        item["veranstaltung"] = tools.repr(util.veranstaltung, item["veranstaltung"], False, True)
                    if (item["semester"] in st.session_state.semester_auswahl) and (item["studiengang"] == [] or st.session_state[f"studiengang_choose_{i}"] == [] or len([x for x in item["studiengang"] if x in st.session_state[f"studiengang_choose_{i}"]]) > 0):
                        append = True
                    item["semester"] = util.semester.find_one({"_id": item["semester"]})["kurzname"]
                    item["studiengang"] = "alle" if item["studiengang"] == [] else ", ".join([tools.repr(util.studiengang, id, False, True) for id in item["studiengang"]])
                    if append:
                        stat_choice.append(item)
                df[i] = pd.DataFrame.from_records(stat_choice)
    if number:
        col = st.columns([1 for _ in range(number)])
    for i in range(number):
        with col[i]:    
            if i < number_semester:
                collection = util.stat_semester
                if st.session_state[f"stat_choose_{i}"] is not None:
                    # Erstelle die Altair-Balkengrafik mit verschiedenen Farben für jede Variable
                    chart[i] = alt.Chart(df[i]).mark_bar().encode(
                        x=alt.X('semester:N', title=''),
                        y=alt.Y('wert:Q', title='Studiengang'),
                        color='studiengang:N',  # Unterschiedliche Farben für jede Variable
                        column=alt.Column('studiengang', title="", header=alt.Header(labelAngle=270))  # Rotate column titles
                    ).properties(
                        title=f"{tools.repr(collection, st.session_state[f"stat_choose_{i}"], False)}"
                    )
            else:
                collection = util.stat_veranstaltung
                if st.session_state[f"stat_choose_{i}"] is not None:
                    # Erstelle die Altair-Balkengrafik mit verschiedenen Farben für jede Variable
                    chart[i] = alt.Chart(df[i]).mark_bar().encode(
                        x=alt.X('veranstaltung:N', title=''),
                        y=alt.Y('wert:Q', title='Studiengang'),
                        color='studiengang:N',  # Unterschiedliche Farben für jede Variable
                        column=alt.Column('studiengang', title="", header=alt.Header(labelAngle=270))  # Rotate column titles
                    ).properties(
                        title=f"{tools.repr(collection, st.session_state[f"stat_choose_{i}"], False)}"
                    )
                # Zeige die Grafik in Streamlit
            if st.session_state[f"stat_choose_{i}"] is not None:
                st.altair_chart(chart[i])
    if number:
        col = st.columns([1 for _ in range(number)])
    for i in range(number):
        with col[i]:
            st.divider()
            if st.session_state[f"stat_choose_{i}"] is not None:
                st.write("Angezeigte Daten")
                st.write(df[i])

else:
    st.switch_page("STAT")

st.sidebar.button("logout", on_click = tools.logout)



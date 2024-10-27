import streamlit as st
from misc.config import *
import pymongo

# Initialize logging
import logging
from misc.config import log_file

@st.cache_resource
def configure_logging(file_path, level=logging.INFO):
    logger = logging.getLogger()
    logger.setLevel(level)
    file_handler = logging.FileHandler(file_path)
    file_handler.setLevel(level)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - MI-STAT - %(message)s")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger

logger = configure_logging(log_file)

def setup_session_state():
    # Das ist die mongodb; 
    # vvz enthält alle Daten für das Vorlesungsverzeichnis. 
    # user ist aus dem Cluster user und wird nur bei der Authentifizierung benötigt
    try:
        cluster = pymongo.MongoClient(mongo_location)
        mongo_db_users = cluster["user"]
        st.session_state.user = mongo_db_users["user"]
        st.session_state.group = mongo_db_users["group"]

        mongo_db_vvz = cluster["vvz"]
        mongo_db_stat = cluster["stat"]
        logger.debug("Connected to MongoDB")
        st.session_state.rubrik = mongo_db_vvz["rubrik"]
        st.session_state.person = mongo_db_vvz["person"]
        st.session_state.semester = mongo_db_vvz["semester"]
        st.session_state.studiengang = mongo_db_vvz["studiengang"]
        st.session_state.veranstaltung = mongo_db_vvz["veranstaltung"]
        st.session_state.stat_veranstaltung = mongo_db_stat["veranstaltung"]
        st.session_state.stat_semester = mongo_db_stat["semester"]
        
    except: 
        logger.error("Verbindung zur Datenbank nicht möglich!")
        st.write("**Verbindung zur Datenbank nicht möglich!**  \nKontaktieren Sie den Administrator.")

    # sem ist ein gewähltes Semester
    if "current_semester_id" not in st.session_state:
        semesters = list(semester.find(sort=[("kurzname", pymongo.DESCENDING)]))
        st.session_state.current_semester_id = semesters[0]["_id"]
    if "semester_id" not in st.session_state:
        semesters = list(semester.find(sort=[("kurzname", pymongo.DESCENDING)]))
        st.session_state.semester_id = semesters[0]["_id"]
    # expanded zeigt an, welches Element ausgeklappt sein soll
    if "expanded" not in st.session_state:
        st.session_state.expanded = ""
    # Name of the user
    if "user" not in st.session_state:
        st.session_state.user = ""
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    # Element to edit
    if "edit" not in st.session_state:
        st.session_state.edit = ""
    # Determines which page we are on
    if "page" not in st.session_state:
        st.session_state.page = ""

    st.session_state.collection_name = {
        person: "Personen",
        rubrik: "Rubrik",
        semester: "Semester",
        studiengang: "Studiengänge",
        veranstaltung: "Veranstaltungen",
        stat_veranstaltung: "Veranstaltungsstatistik",
        stat_semester: "Semesterstatistik"
    }

    st.session_state.new = {
        stat_semester: {
            "name" : "", 
            "semester" : [], 
            "studiengang" : [], 
            "stat" : [],
            "kommentar" : ""
        },
        stat_veranstaltung: {
            "name" : "", 
            "studiengang" : [],
            "stat" : [],
            "kommentar" : ""
        }
    }

setup_session_state()
user = st.session_state.user
group = st.session_state.group
new = st.session_state.new
semester_id = st.session_state.semester_id

rubrik = st.session_state.rubrik
person = st.session_state.person
semester = st.session_state.semester
studiengang = st.session_state.studiengang
veranstaltung = st.session_state.veranstaltung
stat_veranstaltung = st.session_state.stat_veranstaltung
stat_semester = st.session_state.stat_semester


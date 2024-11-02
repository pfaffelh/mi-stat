import streamlit as st
import pymongo
import time

from misc.config import *
import misc.util as util
import misc.tools as tools


# Ab hier wird die Seite angezeigt
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

col0, col1, col2 = st.columns([1,1,1])

with col1:
    st.header("STAT Login")
    placeholder = st.empty()
    with placeholder.form("login"):
        kennung = st.text_input("Benutzerkennung")
        password = st.text_input("Passwort", type="password")
        submit = st.form_submit_button("Login")
        st.session_state.user = kennung

if submit:
    if tools.authenticate(kennung, password): 
        if tools.can_edit(kennung):
            # If the form is submitted and the email and password are correct,
            # clear the form/container and display a success message
            placeholder.empty()
            st.session_state.logged_in = True
            st.success("Login successful")
            util.logger.info(f"User {st.session_state.user} hat in sich erfolgreich eingeloggt.")
            # make all neccesary variables available to session_state
            util.setup_session_state()
            st.switch_page(st.Page("pages/01_Semester.py", title="Semester"))
        else:
            st.error("Nicht genügend Rechte, um STAT zu editieren.")
            util.logger.info(f"User {kennung} hatte nicht gebügend Rechte, um sich einzuloggen.")
            time.sleep(2)
            st.rerun()
    else: 
        st.error("Login nicht korrekt, oder RZ-Authentifizierung nicht möglich. (Z.B., falls nicht mit VPN verbunden.)")
        util.logger.info(f"Ein falscher Anmeldeversuch.")
        time.sleep(2)
#         st.rerun()



import streamlit as st
import pymongo
import time
import ldap
import misc.util as util
from bson import ObjectId
from misc.config import *
from datetime import datetime

def move_up(collection, x, query = {}):
    query["rang"] = {"$lt": x["rang"]}
    target = collection.find_one(query, sort = [("rang",pymongo.DESCENDING)])
    if target:
        n= target["rang"]
        collection.update_one({"_id": target["_id"]}, {"$set": {"rang": x["rang"]}})    
        collection.update_one({"_id": x["_id"]}, {"$set": {"rang": n}})    

def move_down(collection, x, query = {}):
    query["rang"] = {"$gt": x["rang"]}
    target = collection.find_one(query, sort = [("rang", pymongo.ASCENDING)])
    if target:
        n= target["rang"]
        collection.update_one({"_id": target["_id"]}, {"$set": {"rang": x["rang"]}})    
        collection.update_one({"_id": x["_id"]}, {"$set": {"rang": n}})    

def move_up_list(collection, id, field, element):
    list = collection.find_one({"_id": id})[field]
    i = list.index(element)
    if i > 0:
        x = list[i-1]
        list[i-1] = element
        list[i] = x
    collection.update_one({"_id": id}, { "$set": {field: list}})

def move_down_list(collection, id, field, element):
    list = collection.find_one({"_id": id})[field]
    i = list.index(element)
    if i+1 < len(list):
        x = list[i+1]
        list[i+1] = element
        list[i] = x
    collection.update_one({"_id": id}, { "$set": {field: list}})

def remove_from_list(collection, id, field, element):
    collection.update_one({"_id": id}, {"$pull": {field: element}})

def update_confirm(collection, x, x_updated, reset = True):
    util.logger.info(f"User {st.session_state.user} hat in {util.collection_name[collection]} Item {repr(collection, x['_id'])} geändert.")
    collection.update_one({"_id" : x["_id"]}, {"$set": x_updated })
    if reset:
        reset_vars("")
    st.toast("🎉 Erfolgreich geändert!")

def new(collection, ini = {}):
    if list(collection.find({ "rang" : { "$exists": True }})) != []:
        z = list(collection.find(sort = [("rang", pymongo.ASCENDING)]))
        rang = z[0]["rang"]-1
        util.new[collection]["rang"] = rang    
    for key, value in ini.items():
        util.new[collection][key] = value
    util.new[collection].pop("_id", None)
    x = collection.insert_one(util.new[collection])
    st.session_state.edit=x.inserted_id
    util.logger.info(f"User {st.session_state.user} hat in {util.collection_name[collection]} ein neues Item angelegt.")

def update_or_insert(collection, x, x_updated, reset = True):
    if x["_id"] == "new":
        new(collection, ini = x_updated)
    else:
        update_confirm(collection, x, x_updated, reset)

# Finde in collection.field die id, und gebe im Datensatz return_field zurück. Falls list=True,
# dann ist collection.field ein array.
def references(collection, field, list = False):    
    res = {}
    for x in util.abhaengigkeit[collection]:
        res = res | { collection: references(x["collection"], x["field"], x["list"]) } 
    if list:
        z = list(collection.find({field: {"$elemMatch": {"$eq": id}}}))
    else:
        z = list(collection.find({field: id}))
        res = {collection: [t["_id"] for t in z]}
    return res

# Finde in collection.field die id, und gebe im Datensatz return_field zurück. Falls list=True,
# dann ist collection.field ein array.
def find_dependent_items(collection, id):
    res = []
    for x in util.abhaengigkeit[collection]:
        if x["list"]:
            for y in list(x["collection"].find({x["field"].replace(".$",""): { "$elemMatch": { "$eq": id }}})):
                res.append(repr(x["collection"], y["_id"]))
        else:
            for y in list(x["collection"].find({x["field"]: id})):
                res.append(repr(x["collection"], y["_id"]))
    return res

# Finde in collection.field die id, und gebe im Datensatz return_field zurück. Falls list=True,
# dann ist collection.field ein array.
def find_dependent_veranstaltung(collection, id):
    res = []
    for x in util.abhaengigkeit[collection]:
        if x["collection"] == util.veranstaltung:
            if x["list"]:
                for y in list(x["collection"].find({x["field"].replace(".$",""): { "$elemMatch": { "$eq": id }}})):
                    res.append(y["_id"])
            else:
                for y in list(x["collection"].find({x["field"]: id})):
                    res.append(y["_id"])
    return res

# Für Semester
def kurzname_of_id(id):
    try:
        x = util.semester.find_one({"_id": id})["kurzname"]
    except:
        x = util.studiengang.find_one({"_id": id})["kurzname"]        
    return x

def id_of_kurzname(kurzname):
    x = util.semester.find_one({"kurzname": kurzname})["_id"]
    return x

# Die Authentifizierung gegen den Uni-LDAP-Server
def authenticate(username, password):
    ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
    ldap.set_option(ldap.OPT_NETWORK_TIMEOUT, 2.0)
    user_dn = "uid={},{}".format(username, base_dn)
    try:
        l = ldap.initialize(server)
        l.protocol_version = ldap.VERSION3
        l.simple_bind_s(user_dn, password)
        return True
    except ldap.INVALID_CREDENTIALS:
        return False
    except ldap.LDAPError as error:
        util.logger.warning(f"LDAP-Error: {error}")
        return False

def can_edit(username):
    u = util.user.find_one({"rz": username})
    id = util.group.find_one({"name": app_name})["_id"]
    return (True if id in u["groups"] else False)

def logout():
    st.session_state.logged_in = False
    util.logger.info(f"User {st.session_state.user} hat sich ausgeloggt.")

def reset_vars(text=""):
    st.session_state.edit = ""
    if text != "":
        st.success(text)

def display_navigation():
    st.markdown("<style>.st-emotion-cache-16txtl3 { padding: 2rem 2rem; }</style>", unsafe_allow_html=True)

    st.sidebar.write("<hr style='height:1px;margin:0px;;border:none;color:#333;background-color:#333;' /> ", unsafe_allow_html=True)
    st.sidebar.page_link("pages/01_Semester.py", label="Semester")
    st.sidebar.page_link("pages/02_Veranstaltung.py", label="Veranstaltung")
    st.sidebar.write("<hr style='height:1px;margin:0px;;border:none;color:#333;background-color:#333;' /> ", unsafe_allow_html=True)
    st.sidebar.page_link("pages/01_Semester_Grafik.py", label="Semester Grafik")
    st.sidebar.page_link("pages/02_Veranstaltung_Grafik.py", label="Veranstaltung Grafik")
    st.sidebar.write("<hr style='height:1px;margin:0px;;border:none;color:#333;background-color:#333;' /> ", unsafe_allow_html=True)

# short Version ohne abhängige Variablen
def repr(collection, id, show_collection = True, short = False):
    x = collection.find_one({"_id": id})
    if collection == util.semester:
        res = x['kurzname'] if short else x["name_de"]
    elif collection == util.rubrik:
        sem = util.semester.find_one({"_id": x["semester"]})["kurzname"]
        res = x['titel_de'] if short else f"{x['titel_de']} ({sem})"
    elif collection == util.person:
        res = f"{x['name']}, {x['name_prefix']}" if short else f"{x['name']}, {x['vorname']}"
    elif collection == util.studiengang:
        if short:
            res = f"{x['kurzname']}"
        else:
            res = f"{x['name']}"
    elif collection == util.veranstaltung:
        s = ", ".join([util.person.find_one({"_id" : id1})["name"] for id1 in x["dozent"]])
        sem = util.semester.find_one({"_id": x["semester"]})["kurzname"]
        res = x['name_de'] if short else f"{x['name_de']} ({s}, {sem})"
    elif collection == util.stat_semester:
        res = f"{x["name"]}"
    elif collection == util.stat_veranstaltung:
        res = f"{x["name"]}"
    if show_collection:
        res = f"{util.collection_name[collection]}: {res}"
    return res

def hour_of_datetime(dt):
    return "" if dt is None else str(dt.hour)

# str1 und str2 sind zwei strings, die mit "," getrennte Felder enthalten, etwa
# str1 = "HS Rundbau, Mo, 8-10"
# str2 = "HS Rundbau, Mi, 8-10"
# Ausgabe ist dann
# HS Rundbau, Mo, Mi, 8-10
def shortify(str1, str2):
    str1_list = str.split(str1, ",")
    str2_list = str.split(str2, ",")
    if str1_list[0] == str2_list[0]:
        if str1_list[2] == str2_list[2]:
            return f"{str1_list[0]}, {str1_list[1]}, {str2_list[1]} {str2_list[2]}"
        else:
            return f"{str1_list[0]}, {str1_list[1]} {str1_list[2]}, {str2_list[1]} {str2_list[2]}"
    else:
        return None

def next_semester_kurzname(kurzname):
    a = int(kurzname[:4])
    b = kurzname[4:]
    return f"{a+1}SS" if b == "WS" else f"{a}WS"

def last_semester_kurzname(kurzname):
    a = int(kurzname[:4])
    b = kurzname[4:]
    return f"{a}SS" if b == "WS" else f"{a-1}WS"

def semester_name_de(kurzname):
    a = int(kurzname[:4])
    b = kurzname[4:]
    c = f"/{a+1}" if b == "WS" else ""
    return f"{'Wintersemester' if b == 'WS' else 'Sommersemester'} {a}{c}"

def semester_name_en(kurzname):
    a = int(kurzname[:4])
    b = kurzname[4:]
    c = f"/{a+1}" if b == "WS" else ""
    return f"{'Winter term' if b == 'WS' else 'Summer term'} {a}{c}"

def new_semester_dict():
    most_current_semester = util.semester.find_one({}, sort = [("rang", pymongo.DESCENDING)])
    kurzname = next_semester_kurzname(most_current_semester["kurzname"])
    name_de = semester_name_de(kurzname)
    name_en = semester_name_en(kurzname)
    return {"kurzname": kurzname, "name_de": name_de, "name_en": name_en, "rubrik":[], "code": [], "veranstaltung": [], "hp_sichtbar": True, "rang": most_current_semester["rang"]+1}

def delete_item(collection, id):
    util.logger.info(f"User {st.session_state.user} hat in {util.collection_name[collection]} item {repr(collection, id)} gelöscht.")
    collection.delete_one({"_id": id})
    reset_vars("")
    st.success(f"🎉 Erfolgreich gelöscht")
    time.sleep(2)

def delete_temporary(except_field = ""):
    """ Delete temporary data except for the given field."""
    if not except_field == "veranstaltung_tmp":
        st.session_state.veranstaltung_tmp.clear()
        st.session_state.translation_tmp = None

def get_semester_in_years(y = 0):
    if datetime.now().month < 4:
        res = f"{datetime.now().year-1+y}WS"
    elif 3 < datetime.now().month and datetime.now().month < 11:
        res = f"{datetime.now().year+y}SS"
    else:
        res = f"{datetime.now().year+y}WS"
    return res

    
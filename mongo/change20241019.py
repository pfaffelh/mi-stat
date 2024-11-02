from pymongo import MongoClient
import pymongo
import os
import datetime

cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["vvz"]

ver = mongo_db["veranstaltung"]
sem = mongo_db["semester"]
stu = mongo_db["studiengang"]
rub = mongo_db["rubrik"]


stat_sem = mongo_db["stat_semester"]
stat_ver = mongo_db["stat_veranstaltung"]

import schema20241019
#mongo_db.command('collMod','stat_semester', validator=schema20241019.stat_semester_validator, validationLevel='off')
#mongo_db.command('collMod','stat_veranstaltung', validator=schema20241019.stat_veranstaltung_validator, validationLevel='off')

# Ab hier wird die Datenbank verändert
print("Ab hier wird verändert")

stat_sem.insert_one({"name" : "Einschreibezahlen", "rang" : 100, "einheit" : "Studierende", "stat" : [], "kommentar" : ""})

stat_ver.insert_one({"name" : "Anzahl Tutorate", "rang" : 100, "einheit" : "Tutorate", "stat" : [], "kommentar" : ""})

# Ab hier wird das Schema gecheckt
print("Check schema")
mongo_db.command('collMod','stat_semester', validator=schema20241019.stat_semester_validator, validationLevel='moderate')
mongo_db.command('collMod','stat_veranstaltung', validator=schema20241019.stat_veranstaltung_validator, validationLevel='moderate')


from pymongo import MongoClient
import pymongo
import os
import datetime

cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db_vvz = cluster["vvz"]
mongo_db_stat = cluster["stat"]

ver = mongo_db_vvz["veranstaltung"]
sem = mongo_db_vvz["semester"]
stu = mongo_db_vvz["studiengang"]
rub = mongo_db_vvz["rubrik"]


stat_sem = mongo_db_stat["semester"]
stat_ver = mongo_db_stat["veranstaltung"]

import schema20241019
mongo_db_stat.command('collMod','semester', validator=schema20241019.semester_validator, validationLevel='off')
mongo_db_stat.command('collMod','veranstaltung', validator=schema20241019.veranstaltung_validator, validationLevel='off')

# Ab hier wird die Datenbank verändert
print("Ab hier wird verändert")


stat_sem.insert_one({"name" : "Einschreibezahlen", "rang" : 100, "einheit" : "Studierende", "stat" : [], "kommentar" : ""})

stat_ver.insert_one({"name" : "Anzahl Tutorate", "rang" : 100, "einheit" : "Tutorate", "stat" : [], "kommentar" : ""})

# Ab hier wird das Schema gecheckt
print("Check schema")
mongo_db_stat.command('collMod','semester', validator=schema20241019.semester_validator, validationLevel='moderate')
mongo_db_stat.command('collMod','veranstaltung', validator=schema20241019.veranstaltung_validator, validationLevel='moderate')


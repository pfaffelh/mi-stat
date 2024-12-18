from pymongo import MongoClient

# This is the mongodb
cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["vvz"]

# collections sind:

# stat_veranstaltung
# stat_semester

# Gemeint ist hier eine Statistik zu einer Veranstaltung
stat_veranstaltung_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "title": "Eine Statistik für Veranstaltungen.",
        "required": ["name", "rang", "einheit", "stat", "kommentar"],
        "properties": {
            "name": {
                "bsonType": "string",
                "description": "Name der Statistik -- required"
            },
            "rang": {
                "bsonType": "int",
                "description": "Der Rang der Statistik in der Darstellung -- required"
            },
            "einheit": {
                "bsonType": "string",
                "description": "Die Einheit der Statistik -- required"
            },
            "stat": {
                "bsonType": "array",
                "description": "Liste der einzelnen Zahlenwerte.",
                "items": {
                    "bsonType": "object",
                    "description": "Beschreibung einer Realisierung",
                    "required": ["veranstaltung", "studiengang", "wert", "kommentar"],
                    "properties": {
                        "veranstaltung": {
                            "bsonType": "objectId",
                            "description": "Die Veranstaltung."
                        },
                        "studiengang": {
                            "bsonType": "array",
                            "description": "Kein oder ein Studiengang",
                            "items": {
                                "bsonType": "objectId",
                                "description": "Ein Studiengang.",
                            }
                        },
                        "wert": {
                            "bsonType": "double",
                            "description": "Der angenommene Wert."
                        },
                        "kommentar": {
                            "bsonType": "string",
                            "description": "Kommentar zum Wert."
                        }
                    },
                },
            },
            "kommentar": {
                "bsonType": "string",
                "description": "Kommentar zum Begriff."
            },
        },
    }
}

# Gemeint ist hier eine Statistik zu einem Semester
# Sie darf auch von einem Studiengang abhängen
stat_semester_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "title": "Eine Statistik für Semester.",
        "required": ["name", "rang", "einheit", "stat", "kommentar"],
        "properties": {
            "name": {
                "bsonType": "string",
                "description": "Name der Statistik -- required"
            },
            "rang": {
                "bsonType": "int",
                "description": "Der Rang der Statistik in der Darstellung -- required"
            },
            "einheit": {
                "bsonType": "string",
                "description": "Die Einheit der Statistik -- required"
            },
            "stat": {
                "bsonType": "array",
                "description": "Liste der einzelnen Zahlenwerte.",
                "items": {
                    "bsonType": "object",
                    "description": "Beschreibung einer Realisierung",
                    "required": ["semester", "studiengang", "wert", "kommentar"],
                    "properties": {
                        "semester": {
                            "bsonType": "objectId",
                            "description": "Das Semester."
                        },
                        "studiengang": {
                            "bsonType": "array",
                            "description": "Kein oder ein Studiengang.",
                            "items": {
                                "bsonType": "objectId",
                                "description": "Der Studiengang."
                            },
                        },
                        "wert": {
                            "bsonType": "double",
                            "description": "Der angenommene Wert."
                        },
                        "kommentar": {
                            "bsonType": "string",
                            "description": "Ein Kommentar zum Wert."
                        }                    
                    },
                },
            },
            "kommentar": {
                "bsonType": "string",
                "description": "Kommentar zum Begriff."
            },
        },
    }
}


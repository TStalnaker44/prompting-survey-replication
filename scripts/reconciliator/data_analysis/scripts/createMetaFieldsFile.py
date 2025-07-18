
import csv, json, os

def cleanFieldName(field):
    translation = {"Duration (in seconds)": "Duration",
                   "ResponseId": "ResponseID"}
    return translation.get(field, field)

def getMetaFields(filename):
    with open(filename, "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        rows = [row for row in reader]
        field_names = rows[0]
        import_ids = rows[2]
        return getSequential({ cleanFieldName(field):i for i, field in enumerate(field_names) 
                   if not json.loads(import_ids[i]).get("ImportId").startswith("QID")})
        
def getSequential(fields):
    pointer = -1
    new_fields = {}
    for field, index in fields.items():
        if index == pointer + 1:
            pointer = index
            new_fields[field] = index
        else:
            break
    return new_fields

def saveMetaFieldsFile(dataFileName, survey):
    fields = getMetaFields(dataFileName)
    path = os.path.join("surveys", survey, "metafields.json")
    with open(path, "w", encoding="utf-8") as file:
        json.dump(fields, file, indent=4)

def metaFieldFileExists(survey):
    path = os.path.join("surveys", survey, "metafields.json")
    return os.path.exists(path)
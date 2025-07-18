
import os, json, glob
from .settings import CONFIG

def checkSettings():
    if not checkSurveys():
        return 0
    if not checkQuestionFiles():
        return 0
    if not checkMetaFiles():
        return 0
    if not checkSyntaxOfQuestionFiles():
        return 0
    if not checkResponseCoding():
        return 0
    return 1

def checkResponseCoding():
    if CONFIG.RESPONSE_CODING_DONE:
        survey = CONFIG.SURVEY
        path = os.path.join("surveys", survey, "data", "response_coding.csv")
        if not os.path.exists(path):
            print(f"RESPONSE_CODING_DONE is set to True, but the 'response_coding.csv' file for '{survey}' could not be found.")
            print(f"Either set RESPONSE_CODING_DONE to False or place the appropriate file in the '{survey}/data' directory.")
            return 0
    return 1

def checkMetaFiles():
    missing = []
    survey = CONFIG.SURVEY
    path = os.path.join("surveys", survey, "metafields.json")
    if not os.path.exists(path):
        missing.append(survey)
    if missing:
        print("The following surveys are missing metafields.json:", ", ".join(missing))
        for survey in missing:
            makeMetafields(survey)
        print("Added default metafield.json files to directories.")
    return 1

def checkQuestionFiles():
    missing = []
    survey = CONFIG.SURVEY
    path = os.path.join("surveys", survey, "questions.json")
    if not os.path.exists(path):
        missing.append(survey)
    if missing:
        print("The following surveys are missing questions.json:", ", ".join(missing))
        print("For each survey, please:\n (1) Make sure that questions.json is in the right location (the top-level of your survey directory)" +\
               "\n (2) Or run createQuestionsJson.py to create one before continuing.")
        return 0
    return 1

def checkSyntaxOfQuestionFiles():
    survey = CONFIG.SURVEY
    path = os.path.join("surveys", survey, "questions.json")
    with open(path, "r", encoding="utf-8") as file:
        d = json.load(file)
    questions = []
    for gname, gdata in d.items():
        for qname, qdata in gdata.items():
            if not qdata.get("question"):
                print(f"Incorrect syntax in {survey}/questions.json")
                print(f"Missing 'question' tag on question {qname} in group '{gname}'")
                print("All questions must contain question text.")
                return 0
            if not qdata.get("type"):
                print(f"Incorrect syntax in {survey}/questions.json")
                print(f"Missing 'type' tag on question {qname} in group '{gname}'")
                return 0
            if qdata["type"] == "ranked" and (not qdata.get("options")):
                print(f"Incorrect syntax in {survey}/questions.json")
                print("Questions of type 'ranked' must include the 'options' tag")
                print("See documentation for more details.")
                return 0
            if qname in questions:
                print(f"Incorrect syntax in {survey}/questions.json")
                print(f"Two questions with the name '{qname}'")
                print("All question names must be unique.")
                return 0
            questions.append(qname)

    return 1

def checkSurveys():
    if CONFIG.SURVEY in (None, ""):
        print("No surveys provided. Please provide at least one survey to begin.")
        return 0
    bad_surveys = []
    survey = CONFIG.SURVEY
    path = os.path.join("surveys", survey)
    if not os.path.isdir(path):
        bad_surveys.append(survey)
    if bad_surveys:
        print("The following surveys do not exist:", ", ".join(bad_surveys))
        print("Please create them or remove them from SURVEYS before continuing")
        return 0
    return 1

def makeMetafields(survey):
    default = {"StartDate":0, "EndDate":1, 
                "Status":2, "IPAddress":3,
                "Progress":4, "Duration":5, 
                "Finished":6, "RecordedDate":7, 
                "ResponseID":8, "LocationLatitude":13, 
                "LocationLongitude":14,"UserLanguage":16}
    path = os.path.join("surveys", survey, "metafields.json")
    with open(path, "w", encoding="utf-8") as file:
        json.dump(default, file, indent=4)
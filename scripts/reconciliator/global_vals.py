# Store any values that are needed by multiple pages
import json, os

global cur_coder
cur_coder = None

def set_survey_session(request, survey):
    if survey == None:
        request.session["survey_internal"] = None
        request.session["survey_display"] = None
    else:
        request.session["survey_internal"] = format_internal_name(survey)
        request.session["survey_display"] = format_display_name(survey)

conversion_dictionary = {
    " ": "_",
    "\\": "&#92;",
    "[": "&#91;",
    "]": "&#93;",
    "/": "&#47;",
    ":": "&#58;",
    "*": "&#42;",
    "?": "&#63;",
    "\"": "&#34;",
    "<": "&#60;",
    ">": "&#62;",
    "|": "&#124;"
}

def format_internal_name(survey):
    for key, value in conversion_dictionary.items():
        survey = survey.replace(key, value)
    return survey

def format_display_name(survey):
    for key, value in conversion_dictionary.items():
        survey = survey.replace(value, key)
    return survey

def set_coder(coder):
    global cur_coder
    if coder != None:
        cur_coder = coder
    else:
        cur_coder = None

def get_coder():
    return cur_coder
    
# Returns true if survey has a csv file in the survey files folder, otherwise returns false 
def has_csv(survey_internal_name):
    if not survey_internal_name:
        print("Cannot find csv files for non-existing survey: " + survey_internal_name)
        return False
    
    for file in os.listdir(os.path.join("surveys", survey_internal_name, "files")):
        if file.endswith(".csv"):
            return True
    return False


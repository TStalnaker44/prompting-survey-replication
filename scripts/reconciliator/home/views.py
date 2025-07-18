from django.shortcuts import render
import global_vals as gv
import os, json

from app.models import Survey
from data_analysis.views import canGenerateJSON
import shutil


# Returns a list of survey directories in the surveys folder
def get_survey_dirs():
    return [s for s in os.listdir("surveys") if os.path.isdir(os.path.join("surveys", s))]

def index(request):
    # Create the surveys directory if it does not exist
    if not os.path.exists("surveys"):
        os.mkdir("surveys")

    # Filter out .gitignore
    surveys = [gv.format_display_name(survey) for survey in get_survey_dirs()]

    if request.method == 'POST':
        cur_survey = request.POST.get("select_survey")
        gv.set_survey_session(request, cur_survey)
        
    elif request.method == 'GET':
        cur_survey = request.session.get("survey_internal")
        if (surveys and cur_survey is None):
            cur_survey = surveys[0]
            gv.set_survey_session(request, cur_survey)
        elif not surveys:
            gv.set_survey_session(request, cur_survey)

    cur_survey = request.session["survey_display"]

    if (cur_survey is None):
        return render(request, "no_survey_home.html")
    else:
        survey_internal = request.session.get("survey_internal")
        csv_exists = gv.has_csv(survey_internal)
        fname = os.path.join("surveys", survey_internal, "files", "id-mappings.json")
        json_exists = os.path.exists(fname)
        return render(request, 'home.html', {"surveys": surveys, "cur_survey": cur_survey, 
                "csv_exists": csv_exists, "json_exists": json_exists})

def addUploadSurveyForm(request):
    return render(request, "add_upload_survey.html")

def add_upload_survey(request):
    if request.method == 'POST':

        # Remove trailing and leading spaces
        survey = request.POST.get("new_survey").strip().replace(" ", "_")

        # If the survey name is empty, render the special failure page instead
        if survey == "":
            return render(request, "failure_empty.html")

        survey_internal = gv.format_internal_name(survey)        

        names = {
            "name_internal": survey_internal,
            "name_display": survey.replace("_", " ").title()
        }

        # Code for adding new survey and directory structure
        path = os.path.join("surveys", survey_internal)

        # Save current survey in event of an upload failure
        current_survey = request.session["survey_display"]

        # Add the newly created survey to the open-coding database
        db_survey = Survey(internal_id=survey_internal)
        db_survey.save()

        if not os.path.exists(path):
            os.makedirs(path)
            os.makedirs(os.path.join(path, "files"))
            os.makedirs(os.path.join(path, "data"))
            os.makedirs(os.path.join(path, "coders"))
            with open(os.path.join(path, "survey_metadata.json"), "w", encoding="utf-8") as file:
                json.dump(names, file, indent=4)
            gv.set_survey_session(request, survey)
        else:
            return render(request, "add_upload_survey_failure.html",
                          {"survey": gv.format_display_name(survey_internal)})

        if canGenerateJSON(request):
            return render(request, 'add_upload_survey_success.html', 
            {"survey": request.session.get("survey_display")})
        else:
            # Reset the survey name
            gv.set_survey_session(request, current_survey)

            # Delete survey that was created
            path = os.path.join("surveys", survey_internal)
            if os.path.exists(path):
                shutil.rmtree(path)
            return render(request, 'add_upload_survey.html', {"error": "Error Uploading: File is not a QSF"})


def removeSurveyForm(request):
    surveys = [gv.format_display_name(s) for s in get_survey_dirs()]
    return render(request, "remove_survey.html", {"surveys": surveys})

def remove_survey(request):
    survey = request.session.get("survey_internal")

    # If the survey name is empty or None, render the special failure page instead
    if survey is None or survey == "":
        return render(request, "remove_failure.html")

    # Code for the survey path to remove
    path = os.path.join("surveys", survey.strip())

    if os.path.exists(path):
        # Delete survey and all of its files
        shutil.rmtree(path)

        # Update the current survey
        valid = [s for s in get_survey_dirs() if s != survey]

        if len(valid) == 0:
            gv.set_survey_session(None)
        else:
            gv.set_survey_session(request, valid[0])

        return index(request)
    else:
        return render(request, "remove_failure.html", {"survey": request.session.get("survey_display")})

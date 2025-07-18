import json
import os
import shutil
import global_vals as gv

from django.test import Client, TestCase

# Creates a survey directory with a metadata file
def make_survey_directory(internal_name, display_name):
    os.mkdir(f"surveys/{internal_name}")
    os.mkdir(f"surveys/{internal_name}/files")
        
    with open(f"surveys/{internal_name}/survey_metadata.json", "w+") as f:
        f.write(f"""
                {{
                    "name_internal": "{internal_name}",
                    "name_display": "{display_name}"
                }}
                """)
        
# Loads JSON
def load_json(path):
    with open(f"scripts/reconciliator/tests/{path}", "r") as file:
        return json.load(file)
        
# Subclass of TestCase that handles the survey directory
class SurveyTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Get the current directory
        self.path = os.getcwd()
        
        # Rename the surveys directory so that the current data isn't affected
        os.rename("surveys", "surveys2")
        os.mkdir("surveys")
        
    def tearDown(self):
        # Delete the new surveys directory
        if os.path.exists("surveys"):
            shutil.rmtree("surveys")
        
        # Revert the surveys directory to its original name
        os.rename("surveys2", "surveys")
        
        # Reset the current survey
        gv.set_survey(None)

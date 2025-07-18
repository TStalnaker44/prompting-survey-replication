import os
import platform
import shutil
from django.test import Client, TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
import global_vals as gv

from home.views import get_survey_dirs
from tests.testutils import SurveyTestCase, make_survey_directory

# Data for the minimal qsf file
min_qsf = open("scripts/reconciliator/tests/data/minimal_project.qsf", "r").read()

# This tests getSurveyDirs
class GetSurveyDirsTestCase(SurveyTestCase):   
    # Test get_survey_dirs with an empty directory
    def test_empty_directory(self):
        dirs = get_survey_dirs()
        
        # Confirm that the surveys directory exists
        self.assertEqual(dirs, [])
    
    # Test get_survey_dirs with a directory with several folders
    def test_full_directory(self):
        os.mkdir("surveys/a")
        os.mkdir("surveys/b")
        os.mkdir("surveys/c")
        
        dirs = get_survey_dirs()
        
        # Confirm that the surveys directory exists
        self.assertEqual(set(dirs), {"a", "b", "c"})
    
    # Test get_survey_dirs with a directory with several folders including some non-folder files
    def test_full_directory_with_files(self):
        os.mkdir("surveys/a")
        
        open("surveys/.gitignore", "a").close()
        open("surveys/b.txt", "a").close()
        
        os.mkdir("surveys/c")
        
        dirs = get_survey_dirs()
        
        # Confirm that the surveys directory exists
        self.assertEqual(set(dirs), {"a", "c"})

# This tests the behavior for the index
class IndexTestCase(SurveyTestCase):
    # Make sure the surveys folder gets created
    def test_create_surveys_folder_when_no_survey_folder(self):
        shutil.rmtree("surveys")
        
        self.client.get("/")
        
        # Confirm that the surveys directory exists
        self.assertTrue(os.path.exists(os.path.join(self.path, "surveys")), "The surveys directory was not created!")
        
    # Set the survey using POST
    def test_set_survey_from_post(self):
        make_survey_directory("my_survey", "My Survey")
        
        response = self.client.post("/", {
            "select_survey": "my_survey"
        })
        
        # Test if the global names are correct
        self.assertEqual(gv.cur_survey_display, "My Survey")
        self.assertEqual(gv.cur_survey_internal, "my_survey")
        
        # Test if the home page was rendered properly
        self.assertEqual(response.templates[0].name, "home.html")
        self.assertEqual(response.context.get("surveys"), ["My Survey"])
        self.assertEqual(response.context.get("cur_survey"), "My Survey")
        
    # Tests if the no_survey_home page is rendered if there are no surveys
    def test_no_surveys_render_no_survey_home(self):
        response = self.client.get("/")
        
        self.assertEqual(response.templates[0].name, "no_survey_home.html")
        
    # Tests if the home page is rendered with the current survey selected
    def test_render_home_page_with_selected_survey(self):
        make_survey_directory("my_survey", "My Survey")
        make_survey_directory("my_survey2", "My Survey2")
            
        gv.set_survey("my_survey2")
        
        response = self.client.get("/")
        
        self.assertEqual(response.templates[0].name, "home.html")
        self.assertEqual(set(response.context.get("surveys")), {"My Survey", "My Survey2"})
        self.assertEqual(response.context.get("cur_survey"), "My Survey2")
        
    # Tests if the home page is rendered with the first survey selected since no current survey was selected
    def test_render_home_page_with_no_current_survey_selects_first(self):
        make_survey_directory("my_survey", "My Survey")
        make_survey_directory("my_survey2", "My Survey2")
        
        response = self.client.get("/")
        
        self.assertEqual(response.templates[0].name, "home.html")
        self.assertEqual(set(response.context.get("surveys")), {"My Survey", "My Survey2"})
        # This test doesn't work on MacOS, since the survey order is different
        self.assertEqual(response.context.get("cur_survey"), "My Survey2" if platform.system() == "Darwin" else "My Survey")
        
    # Tests if it creates a new survey metadata file for surveys without one
    def test_render_home_page_creates_survey_metadata_as_needed(self):
        make_survey_directory("my_survey", "My Survey")
        os.mkdir("surveys/my_survey2")
        os.mkdir("surveys/my_survey2/files")
            
        self.client.get("/")
        
        # Check if the new file was created
        self.assertTrue(os.path.exists("surveys/my_survey2/survey_metadata.json"))
        
        metadata = open("surveys/my_survey2/survey_metadata.json", "r").read()
        
        self.assertEqual(metadata, """{
    "name_internal": "my_survey2",
    "name_display": "My Survey2"
}""")
        
# Test cases for addUploadSurveyForm
class AddUploadSurveyFormTestCase(TestCase):
    def test_render_page(self):
        self.client = Client()
        
        response = self.client.post("/addUploadSurveyForm/")
        
        self.assertEqual(response.templates[0].name, "add_upload_survey.html")
        
# This test case is for the add_upload_survey view
class AddUploadSurveyTestCase(SurveyTestCase):
    # Renders the failure page when the survey name is empty
    def test_render_failure_page_on_empty_survey(self):
        response = self.client.post("/addUploadSurvey/", {
            "new_survey": ""
        })
        
        self.assertEqual(response.templates[0].name, "failure_empty.html")
        
    # Renders the failure page when the survey name is only spaces
    def test_render_failure_page_on_survey_with_only_spaces(self):
        response = self.client.post("/addUploadSurvey/", {
            "new_survey": "    "
        })
        
        self.assertEqual(response.templates[0].name, "failure_empty.html")
        
    # Renders the failure page when the survey already exists
    def test_render_failure_page_when_survey_exists(self):
        make_survey_directory("survey", "Survey")
        make_survey_directory("survey2", "Survey2")
        
        response = self.client.post("/addUploadSurvey/", {
            "new_survey": "survey"
        })
        
        self.assertEqual(response.templates[0].name, "add_upload_survey_failure.html")
        self.assertEqual(response.context.get("survey"), "Survey")
        
    # Renders the success page for a successful upload
    def test_render_success(self):
        make_survey_directory("survey", "Survey")
        make_survey_directory("survey2", "Survey2")
        
        qsf_file = SimpleUploadedFile("file.qsf", bytes(min_qsf, "utf-8"))
        
        response = self.client.post("/addUploadSurvey/", {
            "new_survey": "survey3",
            "fileUpload": qsf_file
        })
        
        self.assertEqual(response.templates[0].name, "add_upload_survey_success.html")
        self.assertEqual(response.context.get("survey"), "Survey3")
        
    # Successful upload updates current survey
    def test_render_success_upload_current_survey(self):
        make_survey_directory("survey", "Survey")
        make_survey_directory("survey2", "Survey2")
        
        qsf_file = SimpleUploadedFile("file.qsf", bytes(min_qsf, "utf-8"))
        
        response = self.client.post("/addUploadSurvey/", {
            "new_survey": "survey3",
            "fileUpload": qsf_file
        })
        
        self.assertEqual(gv.cur_survey_display, "Survey3")
        self.assertEqual(gv.cur_survey_internal, "survey3")
        
    # Creates the necessary directories and files for a successful upload
    def test_render_success_create_files(self):
        make_survey_directory("survey", "Survey")
        make_survey_directory("survey2", "Survey2")
        
        qsf_file = SimpleUploadedFile("file.qsf", bytes(min_qsf, "utf-8"))
        
        response = self.client.post("/addUploadSurvey/", {
            "new_survey": "survey3",
            "fileUpload": qsf_file
        })
        
        # Check existence of files
        self.assertTrue(os.path.exists("surveys/survey3"))
        self.assertTrue(os.path.exists("surveys/survey3/files"))
        self.assertTrue(os.path.exists("surveys/survey3/data"))
        self.assertTrue(os.path.exists("surveys/survey3/figs"))
        self.assertTrue(os.path.exists("surveys/survey3/survey_metadata.json"))
        
        # Check contents of survey_metadata.json
        metadata = open("surveys/survey3/survey_metadata.json", "r").read()
        
        self.assertEqual(metadata, """{
    "name_internal": "survey3",
    "name_display": "Survey3"
}""") 
        
    # Renders the failed upload page for a failed upload
    def test_render_failed(self):
        make_survey_directory("survey", "Survey")
        make_survey_directory("survey2", "Survey2")
        
        qsf_file = SimpleUploadedFile("file.txt", bytes(min_qsf, "utf-8"))
        
        response = self.client.post("/addUploadSurvey/", {
            "new_survey": "survey3",
            "fileUpload": qsf_file
        })
        
        self.assertEqual(response.templates[0].name, "add_upload_survey.html")
        self.assertEqual(response.context.get("error"), "Error Uploading: File is not a QSF")
        
    # Does not update the global values for a failed upload
    def test_render_failed_dont_update_global_vals(self):
        make_survey_directory("survey", "Survey")
        make_survey_directory("survey2", "Survey2")
        
        gv.set_survey("survey2")
        
        qsf_file = SimpleUploadedFile("file.txt", bytes(min_qsf, "utf-8"))
        
        response = self.client.post("/addUploadSurvey/", {
            "new_survey": "survey3",
            "fileUpload": qsf_file
        })
        
        self.assertEqual(gv.cur_survey_display, "Survey2")
        self.assertEqual(gv.cur_survey_internal, "survey2")
        
    # Does not update the global values for a failed upload even if there are no surveys
    def test_render_failed_no_surveys_dont_update_global_vals(self):
        qsf_file = SimpleUploadedFile("file.txt", bytes(min_qsf, "utf-8"))
        
        response = self.client.post("/addUploadSurvey/", {
            "new_survey": "survey3",
            "fileUpload": qsf_file
        })
        
        self.assertEqual(gv.cur_survey_display, None)
        self.assertEqual(gv.cur_survey_internal, None)
        
    # Does not create a new directory for a failed upload
    def test_render_failed_dont_create_directory(self):
        make_survey_directory("survey", "Survey")
        make_survey_directory("survey2", "Survey2")
        
        gv.set_survey("survey2")
        
        qsf_file = SimpleUploadedFile("file.txt", bytes(min_qsf, "utf-8"))
        
        response = self.client.post("/addUploadSurvey/", {
            "new_survey": "survey3",
            "fileUpload": qsf_file
        })
        
        self.assertFalse(os.path.exists("surveys/survey3"))
        
class RemoveSurveyFormTestCase(SurveyTestCase):
    def test_remove_survey_form_renders_with_surveys(self):
        make_survey_directory("survey", "Survey")
        make_survey_directory("survey2", "Survey2")
        
        response = self.client.get("/removeSurveyForm/")
        
        self.assertEqual(set(response.context.get("surveys")), {"Survey", "Survey2"})   
        
    def test_remove_survey_form_preserves_survey(self):
        make_survey_directory("survey", "Survey")
        make_survey_directory("survey2", "Survey2")
        
        gv.set_survey("survey2")
        
        response = self.client.get("/removeSurveyForm/")
        
        self.assertEqual(gv.cur_survey_internal, "survey2")
        
class RemoveSurveyTestCase(TestCase):
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
        
    def test_return_remove_failure_if_none(self):
        make_survey_directory("survey", "Survey")
        make_survey_directory("survey2", "Survey2")
        
        gv.set_survey(None)
        
        response = self.client.get("/removeSurvey/")
        
        self.assertEqual(response.templates[0].name, "remove_failure.html")
        
    def test_return_remove_failure_nopath(self):
        gv.set_survey("survey")
        
        response = self.client.get("/removeSurvey/")
        
        self.assertEqual(response.templates[0].name, "remove_failure.html")
        
    def test_return_remove_success_home(self):
        make_survey_directory("survey", "Survey")
        make_survey_directory("survey2", "Survey2")
        
        gv.set_survey("survey")
        
        response = self.client.get("/removeSurvey/")
        
        self.assertEqual(response.templates[0].name, "home.html")
        
        self.assertFalse(os.path.exists("surveys/survey"))
        self.assertTrue(os.path.exists("surveys/survey2"))
        
    def test_return_remove_update_current_with_two_delete_first(self):
        make_survey_directory("survey", "Survey")
        make_survey_directory("survey2", "Survey2")
        
        gv.set_survey("survey")
        
        response = self.client.get("/removeSurvey/")
        
        self.client.get("/")
        
        self.assertEqual(gv.cur_survey_internal, "survey2")
        
    def test_return_remove_update_current_with_two_delete_last(self):
        make_survey_directory("survey", "Survey")
        make_survey_directory("survey2", "Survey2")
        
        gv.set_survey("survey2")
        
        response = self.client.get("/removeSurvey/")
        
        self.client.get("/")
        
        self.assertEqual(gv.cur_survey_internal, "survey")
        
    def test_return_remove_update_current_with_many_delete_mid(self):
        make_survey_directory("survey", "Survey")
        make_survey_directory("survey2", "Survey2")
        make_survey_directory("survey3", "Survey3")
        make_survey_directory("survey4", "Survey4")
        
        gv.set_survey("survey3")
        
        response = self.client.get("/removeSurvey/")
        
        self.client.get("/")
        
        # The folder order is different on macOS
        self.assertEqual(gv.cur_survey_internal, "survey4" if platform.system() == "Darwin" else "survey")
        
    def test_return_remove_only_one_update_current(self):
        make_survey_directory("survey", "Survey")
        
        gv.set_survey("survey")
        
        response = self.client.get("/removeSurvey/")
        
        self.client.get("/")
        
        self.assertEqual(gv.cur_survey_internal, None)
import io
import os
import shutil
import sys
from data_analysis.scripts.settings import CONFIG
from data_analysis.scripts.check_settings import checkSettings
from tests.testutils import SurveyTestCase

def get_input_path(path):
    return f"scripts/reconciliator/tests/data/check_settings/{path}"

def read_output(path):
    return open(f"scripts/reconciliator/tests/data/check_settings/{path}", "r").read()

# Tests the check_settings method
class CheckSettingsTestCase(SurveyTestCase):
    def setUp(self):
        super().setUp()
        
        # Disable print for now
        suppress_text = io.StringIO()
        sys.stdout = suppress_text
        
        # Set up a survey folder
        os.mkdir("surveys/survey")
        os.mkdir("surveys/survey/files")
        
        # Set up configs
        CONFIG.set_survey("survey")
        
    def tearDown(self):
        super().tearDown()
        
        # Reset configs
        CONFIG.set_survey("")
        CONFIG.set_response_coding_done(False)
        CONFIG.set_file_types(["PNG"])
        
        # Re-enable print
        sys.stdout = sys.__stdout__
        
    def test_check_survey_none(self):
        CONFIG.set_survey(None)
        
        self.assertEqual(checkSettings(), 0)
        
    def test_check_survey_empty_name(self):
        CONFIG.set_survey("")
        
        self.assertEqual(checkSettings(), 0)
        
    def test_check_survey_survey_folder_missing(self):
        shutil.rmtree("surveys/survey")
        
        self.assertEqual(checkSettings(), 0)
        
    def test_data_file_missing(self):
        self.assertEqual(checkSettings(), 0)
        
    def test_data_file_wrong_format(self):
        open("surveys/survey/files/data.csv", "w+").close()
        
        self.assertEqual(checkSettings(), 0)
        
    def test_sanitized_file_missing(self):
        open("surveys/survey/files/data_11.csv", "w+").close()
        self.assertEqual(checkSettings(), 0)
        
    def test_sanitized_file_wrong_format(self):
        open("surveys/survey/files/data_11.csv", "w+").close()
        open("surveys/survey/files/1_sanitized.json", "w+").close()        
        self.assertEqual(checkSettings(), 0)
        
    def test_plot_no_data_folder(self):
        open("surveys/survey/files/data_11.csv", "w+").close()
        
        CONFIG.set_pre_process(False)
        
        self.assertEqual(checkSettings(), 0)
        
    def test_questions_file_not_exists(self):
        open("surveys/survey/files/data_11.csv", "w+").close()
        
        self.assertEqual(checkSettings(), 0)
        
    def test_make_missing_metafields(self):
        open("surveys/survey/files/data_11.csv", "w+").close()
        shutil.copy(get_input_path("questions1.json"), "surveys/survey/questions.json")
        
        checkSettings()
        
        self.assertTrue(os.path.exists("surveys/survey/metafields.json"))
        
        metafields = open("surveys/survey/metafields.json", "r").read()
        
        self.assertEqual(metafields, read_output("output1.txt"))
        
    def test_missing_question_field(self):
        open("surveys/survey/files/data_11.csv", "w+").close()
        shutil.copy(get_input_path("questions2.json"), "surveys/survey/questions.json")

        self.assertEqual(checkSettings(), 0)
        
    def test_missing_type_field(self):
        open("surveys/survey/files/data_11.csv", "w+").close()
        shutil.copy(get_input_path("questions3.json"), "surveys/survey/questions.json")
            
        self.assertEqual(checkSettings(), 0)
        
    def test_ranked_missing_options(self):
        open("surveys/survey/files/data_11.csv", "w+").close()
        shutil.copy(get_input_path("questions4.json"), "surveys/survey/questions.json")
            
        self.assertEqual(checkSettings(), 0)
        
    def test_duplicate_questions(self):
        open("surveys/survey/files/data_11.csv", "w+").close()
        shutil.copy(get_input_path("questions5.json"), "surveys/survey/questions.json")
            
        self.assertEqual(checkSettings(), 0)
        
    def test_missing_partitions(self):
        open("surveys/survey/files/data_11.csv", "w+").close()
        shutil.copy(get_input_path("questions6.json"), "surveys/survey/questions.json")
            
        self.assertEqual(checkSettings(), 0)
        
    def test_missing_partition_name(self):
        open("surveys/survey/files/data_11.csv", "w+").close()
        shutil.copy(get_input_path("questions7.json"), "surveys/survey/questions.json")
            
        self.assertEqual(checkSettings(), 0)
        
    def test_missing_response_coding_csv(self):
        open("surveys/survey/files/data_11.csv", "w+").close()
        shutil.copy(get_input_path("questions1.json"), "surveys/survey/questions.json")
        
        CONFIG.set_response_coding_done(True)
        
        self.assertEqual(checkSettings(), 0)
        
    def test_success(self):
        open("surveys/survey/files/data_11.csv", "w+").close()
        shutil.copy(get_input_path("questions1.json"), "surveys/survey/questions.json")
        
        self.assertEqual(checkSettings(), 1)
                
    def test_success_plot(self):
        CONFIG.set_pre_process(False)
        
        open("surveys/survey/files/data_11.csv", "w+").close()
        shutil.copy(get_input_path("questions1.json"), "surveys/survey/questions.json")
        os.mkdir("surveys/survey/data")
        
        self.assertEqual(checkSettings(), 1)
        
    def test_success_response_coding(self):
        CONFIG.set_response_coding_done(True)
        
        open("surveys/survey/files/data_11.csv", "w+").close()
        shutil.copy(get_input_path("questions1.json"), "surveys/survey/questions.json")
        os.mkdir("surveys/survey/data")
        open("surveys/survey/data/response_coding.csv", "w+").close()
        
        self.assertEqual(checkSettings(), 1)
        
        
        
        
        
        
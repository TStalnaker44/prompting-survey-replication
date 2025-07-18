import os
import shutil

from data_analysis.scripts.qualtrics_reader import makeQJSON, readQSF, saveJSON
from tests.testutils import SurveyTestCase

prefix = "scripts/reconciliator/tests/data/qualtrics_reader"

# Reads the value of the questions file generated
def read_questions():
    return open("surveys/survey/questions.json", "r").read()

# Copies the file into the questions qsf
def copy_questions(json_path):
    shutil.copy(f"{prefix}/data/{json_path}", "surveys/survey/files/questions.qsf")
    
# Reads the output text file
def get_expected_output(text_path):
    return open(f"{prefix}/output/{text_path}", "r").read()

# Test cases for readQSF
class readQSFTestCase(SurveyTestCase):
    def test_no_qsf_file_found_returns_none(self):
        os.mkdir("surveys/survey")
        os.mkdir("surveys/survey/files")
        
        json = readQSF("surveys/survey")
        
        self.assertIsNone(json)
        
    def test_load_one_qsf_file(self):
        os.mkdir("surveys/survey")
        os.mkdir("surveys/survey/files")
        
        # It just uses a placeholder JSON
        open("surveys/survey/files/questions.qsf", "w+").write('{"SurveyElements": ["3", "5"]}')
        
        json = readQSF("surveys/survey")
        
        self.assertEqual(json, ["3", "5"])
        
    def test_load_one_qsf_file_out_of_two(self):
        os.mkdir("surveys/survey")
        os.mkdir("surveys/survey/files")
        
        # It just uses a placeholder JSON
        open("surveys/survey/files/questions.qsf", "w+").write('{"SurveyElements": ["7", "6"]}')
        open("surveys/survey/files/questions2.qsf", "w+").write('{"SurveyElements": ["3", "5"]}')
        
        json = readQSF("surveys/survey")
        
        self.assertEqual(json, ["7", "6"])

# Test cases for saveJSON
class SaveJSONTestCase(SurveyTestCase):
    def test_save_json(self):
        os.mkdir("surveys/survey")
        
        open("surveys/survey/questions.json", "w+").close()
        
        # Just use some sample data
        saveJSON("surveys/survey", {
            "data": "1",
            "meta": "2"
        })
        
        # Check if the data is correct
        text = read_questions()
        
        self.assertEqual(text, '{\n    "data": "1",\n    "meta": "2"\n}')
        
# Test cases for makeQJSON
class MakeQJSONTestCase(SurveyTestCase):
    def setUp(self):
        super().setUp()
        
        os.mkdir("surveys/survey")
        os.mkdir("surveys/survey/files")
    
    def test_no_qsf_file_found_dont_upload_questions(self):
        makeQJSON("surveys/survey")
        
        self.assertFalse(os.path.exists("surveys/survey/questions.json"))
        
    def test_qsf_with_no_blocks(self):
        copy_questions("qsf1.json")
        
        makeQJSON("surveys/survey")
        
        self.assertEqual(read_questions(), "{}")
        
    def test_qsf_with_one_block(self):
        copy_questions("qsf2.json")
        
        makeQJSON("surveys/survey")
        
        self.assertEqual(read_questions(), get_expected_output("output2.txt"))
        
    def test_qsf_many_blocks(self):
        copy_questions("qsf3.json")
        
        makeQJSON("surveys/survey")
        
        self.assertEqual(read_questions(), get_expected_output("output3.txt"))
        
    def test_qsf_different_question_types(self):
        copy_questions("qsf4.json")
        
        makeQJSON("surveys/survey")
        
        self.assertEqual(read_questions(), get_expected_output("output4.txt"))
        
    def test_qsf_with_branch(self):
        copy_questions("qsf5.json")
        
        makeQJSON("surveys/survey")
        
        self.assertEqual(read_questions(), get_expected_output("output5.txt"))
        
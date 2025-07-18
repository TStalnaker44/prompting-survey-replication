import os
import shutil
from django.http import HttpRequest
from django.test import Client, TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import AnonymousUser

import global_vals as gv
from data_analysis.views import canGenerateJSON, string_to_bool
from tests.testutils import SurveyTestCase, make_survey_directory

# Data for the minimal qsf file
min_qsf = open("scripts/reconciliator/tests/data/minimal_project.qsf", "r").read()

# Test cases for string_to_bool
class StringToBoolTestCase(TestCase):
    def test_str_to_bool_true(self):
        self.assertTrue(string_to_bool("TrUe"))
        
    def test_str_to_bool_false(self):
        self.assertFalse(string_to_bool("false"))
        
# Test cases for configure_analysis
class ConfigureAnalysisTestCase(SurveyTestCase):    
    def test_configure_analysis_render(self):
        make_survey_directory("survey", "Survey")
        make_survey_directory("survey2", "Survey2")
        
        gv.set_survey("survey2")
        
        response = self.client.get("/configure_analysis/")
        
        self.assertEqual(response.context.get("cur_survey"), "Survey2")
        
# Test cases for uploadQualtricsFile
class UploadQualtricsFileTestCase(SurveyTestCase):
    def test_upload_qualtrics_file_render(self):
        make_survey_directory("survey", "Survey")
        make_survey_directory("survey2", "Survey2")
        
        gv.set_survey("survey2")
        
        response = self.client.get("/uploadQualtricsFile/")
        
        self.assertEqual(response.context.get("cur_survey"), "Survey2")
  
# Test cases for uploadDataFile
class UploadDataFileTestCase(SurveyTestCase): 
    def test_upload_data_file_render(self):
        make_survey_directory("survey", "Survey")
        make_survey_directory("survey2", "Survey2")
        
        gv.set_survey("survey2")
        
        response = self.client.get("/uploadDataFile/")
        
        self.assertEqual(response.context.get("cur_survey"), "Survey2")
  
# Test cases for reviewQuestions
class ReviewQuestionsTestCase(SurveyTestCase):     
    def test_upload_review_questions_render(self):
        make_survey_directory("survey", "Survey")
        make_survey_directory("survey2", "Survey2")
        
        gv.set_survey("survey2")
        
        response = self.client.get("/reviewQuestions/")
        
        self.assertEqual(response.context.get("cur_survey"), "Survey2")
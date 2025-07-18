import os
import shutil
from django.test import TestCase
import global_vals as gv

# Tests for set_survey
class SetSurveyTestCase(TestCase):
    def setUp(self):
        # Rename the surveys directory so that the current data isn't affected
        os.rename("surveys", "surveys2")
        os.mkdir("surveys")
        
    def tearDown(self):
        # Delete the new surveys directory
        if os.path.exists("surveys"):
            shutil.rmtree("surveys")
        
        # Revert the surveys directory to its original name
        os.rename("surveys2", "surveys")
        
    def test_set_survey_none_sets_current_survey_none(self):
        gv.cur_survey_display = "ok"
        gv.cur_survey_internal = "ok"
        
        gv.set_survey(None)
        
        self.assertIsNone(gv.cur_survey_display)
        self.assertIsNone(gv.cur_survey_internal)
        
    # If the survey folder has no metadata, just set the current survey to None, since it isn't valid
    def test_set_survey_with_no_metadata_sets_current_to_none(self):
        os.mkdir("surveys/survey")
        
        gv.set_survey("survey")
        
        self.assertIsNone(gv.cur_survey_display)
        self.assertIsNone(gv.cur_survey_internal)
        
    # Set the current survey to the values in the metadata
    def test_set_survey_with_working_metadata(self):
        # Set up the metadata item
        os.mkdir("surveys/survey")
        
        with open("surveys/survey/survey_metadata.json", "w+") as f:
            f.write("""
                    {
                        "name_internal": "my_survey",
                        "name_display": "My Survey"
                    }
                    """)
            
        gv.set_survey("survey")
        
        self.assertEqual(gv.cur_survey_display, "My Survey")
        self.assertEqual(gv.cur_survey_internal, "my_survey")
        
# Tests for format_internal_name
class FormatInternalNameTestCase(TestCase):
    def test_format_internal_name_standard(self):
        name = "mysurvey"
        
        self.assertEqual(gv.format_internal_name(name), "mysurvey")
        
    def test_format_internal_name_converts_to_lowercase(self):
        name = "MyNewSurvey"
        
        self.assertEqual(gv.format_internal_name(name), "mynewsurvey")
        
    def test_format_internal_name_special_chars(self):
        name = "a survey\\With []/:with*special?\"characters\"<>| ok"
        
        self.assertEqual(gv.format_internal_name(name), "a_survey&#92;with_&#91;&#93;&#47;&#58;with&#42;special&#63;&#34;characters&#34;&#60;&#62;&#124;_ok")
        
# Tests for format_display_name
class FormatDisplayNameTestCase(TestCase):
    def test_format_display_name_standard(self):
        name = "mysurvey"
        
        self.assertEqual(gv.format_display_name(name), "Mysurvey")
        
    def test_format_display_name_several_words(self):
        name = "my_long_survey_name"
        
        self.assertEqual(gv.format_display_name(name), "My Long Survey Name")
        
    def test_format_display_name_special_chars(self):
        name = "a_survey&#92;with_&#91;&#93;&#47;&#58;with&#42;special&#63;&#34;characters&#34;&#60;&#62;&#124;_ok"
        
        self.assertEqual(gv.format_display_name(name), "A Survey\\With []/:With*Special?\"Characters\"<>| Ok")
import os
import shutil
from data_analysis.scripts.settings import CONFIG
from data_analysis.scripts.csv2json import CSVConverter # type: ignore
from tests.testutils import SurveyTestCase


class SimpleSurveyTestCase(SurveyTestCase):
    def setUp(self):
        super().setUp()
        
        CONFIG.set_survey("1question")
        
        # Create the files directory, questions.json, and a data file
        shutil.copytree("scripts/reconciliator/tests/data/csv2json/1question", "surveys/1question")
        
    def test_convert_csv(self):
        converter = CSVConverter(os.path.join("surveys", "1question"))
        
        converter.convertCSV()
        
        self.assertEqual(open("surveys/1question/files/1question_completers_11-19-24.json", "r").read(), open("scripts/reconciliator/tests/data/csv2json/1question/files/csv2json_output.json", "r").read())
        
class SpecialQuestionsTestCase(SurveyTestCase):
    def setUp(self):
        super().setUp()
        
        CONFIG.set_survey("special")
        
        # Create the files directory, questions.json, and a data file
        shutil.copytree("scripts/reconciliator/tests/data/csv2json/special", "surveys/special")
        
    def test_convert_csv(self):
        converter = CSVConverter(os.path.join("surveys", "special"))
        
        converter.convertCSV()
        
        self.assertEqual(open("surveys/special/files/special_completers_11-25-24.json", "r").read(), open("scripts/reconciliator/tests/data/csv2json/special/results/files/special_completers_11-25-24.json", "r").read())
    
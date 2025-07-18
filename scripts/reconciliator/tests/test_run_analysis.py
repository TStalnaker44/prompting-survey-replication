import os
import shutil
from data_analysis.scripts.settings import CONFIG
from data_analysis.scripts.csv2json import CSVConverter # type: ignore
from data_analysis.scripts.run_analysis import main
from tests.testutils import SurveyTestCase


class SimpleSurveyTestCase(SurveyTestCase):
    def setUp(self):
        super().setUp()
        
        CONFIG.set_survey("1question")
        
        # Create the files directory, questions.json, and a data file
        shutil.copytree("scripts/reconciliator/tests/data/csv2json/1question", "surveys/1question")
        
    def test_convert_csv(self):
        main()
        
        # Test if the file is correct
        self.assertEqual(open("surveys/1question/data/all/single.csv", "r").read(), open("scripts/reconciliator/tests/data/csv2json/1question/results/data/all/single.csv", "r").read())


class SpecialQuestionsTestCase(SurveyTestCase):
    def setUp(self):
        super().setUp()
        
        CONFIG.set_survey("special")
        
        # Create the files directory, questions.json, and a data file
        shutil.copytree("scripts/reconciliator/tests/data/csv2json/special", "surveys/special")
        
    def test_convert_csv(self):
        main()
        
        paths = ["single.csv", "multi_select/Q4.csv", "rank/Q5.csv", "rank/Q6.csv", "rank/Q7.csv"]
        
        for path in paths:
            self.assertEqual(open(f"surveys/special/data/all/{path}", "r").read(), open(f"scripts/reconciliator/tests/data/csv2json/special/results/data/all/{path}", "r").read())


class SpecialQuestions2TestCase(SurveyTestCase):
    def setUp(self):
        super().setUp()
        
        CONFIG.set_survey("special2")
        
        # Create the files directory, questions.json, and a data file
        shutil.copytree("scripts/reconciliator/tests/data/csv2json/special2", "surveys/special2")
        
    def test_convert_csv(self):
        main()
        
        paths = ["single.csv", "multi_select/Q4.csv", "rank/Q5.csv", "rank/Q6.csv", "rank/Q7.csv"]
        
        for path in paths:
            self.assertEqual(open(f"surveys/special2/data/all/{path}", "r").read(), open(f"scripts/reconciliator/tests/data/csv2json/special2/results/data/all/{path}", "r").read())
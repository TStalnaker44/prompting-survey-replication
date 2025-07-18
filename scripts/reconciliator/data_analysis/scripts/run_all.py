from .csv2json import CSVConverter
from .sanitize import sanitize
from .settings import CONFIG
from .populate_database import populateDatabase

import os, shutil

from .results_json import ResultsJson

def main():
    survey = CONFIG.SURVEY

    survey_path = os.path.join("surveys", survey)
    print("Processing %s survey..." % (survey,))

    # Generate JSON Files from CSV
    CSVConverter(survey_path).convertCSV()

    # Sanitize JSON
    print("Sanitizing files...")
    sanitize(survey_path)

    # Populate the database
    print("Populating the database with sanitized data...")
    print(survey_path.split(os.path.sep)[-1])
    populateDatabase(survey_path.split(os.path.sep)[-1])

    # Make the data directory if it doesn't exist
    data_path = os.path.join(survey_path, "data")
    if not os.path.isdir(data_path):
        os.mkdir(data_path)

    # if CONFIG.RESPONSE_CODING_DONE:
        ## Moving response_coding file
        # shutil.copy(os.path.join("surveys", survey, "data", "response_coding.csv"),
        #             os.path.join("surveys", survey, "data", "all", "response_coding.csv"))

    ## Generate results.json
    ResultsJson().makeResultsJson()

    print("All data processed!")

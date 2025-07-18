
import openpyxl, json, os
from .utils import getQuestions
from .resp_config import REC_CONFIG

dictionary_file = 'dictionary.xlsx'
output_file = 'glossary.json'

def main():

    questions = getQuestions()
    
    # Load the Excel file
    in_path = os.path.join(REC_CONFIG.PATH, "response_coding", 'code_files', dictionary_file)
    workbook = openpyxl.load_workbook(in_path)

    # Select the sheet you want to work with
    sheet = workbook['Selection Options']

    def getDefinition(comment):
        if comment is None:
            return ("", "")
        else:
            comment = comment.text.split('\n\t-')
            return (comment[0], comment[-1])
        
    terms = {}

    # Identify the index positions of relevant columns
    first_row = [cell.value for cell in sheet[1]]
    column_indices = {value:i+1 for i, value in enumerate(first_row) if value in questions}

    # Iterate over relevant columns
    for question, column in column_indices.items():
        terms[question] = {}
        col_values = next(sheet.iter_cols(min_col=column, max_col=column, min_row=3))
        for cell in col_values:
            term = cell.value
            definition, author = getDefinition(cell.comment)
            if term != None and (not term.startswith("--")):
                terms[question][term] = definition

    out_path = os.path.join(REC_CONFIG.PATH, "response_coding", "generated_files", output_file)
    with open(out_path, "w", encoding="utf-8") as file:
        json.dump(terms, file, indent=4)

if __name__ == "__main__":
    main()

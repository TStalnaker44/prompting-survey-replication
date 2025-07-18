import requests, csv, openpyxl, shutil, os

class CodeBook():
    _INSTANCE = None
    _SURVEY = None

    @classmethod
    def instance(cls, survey):
        if cls._INSTANCE is None or survey != cls._SURVEY:
            cls._INSTANCE = cls._CodeBook(survey)
            cls._SURVEY = survey
        return cls._INSTANCE

    class _CodeBook():

        def __init__(self, survey):
            self.survey = survey
            self.updateCodes()

        def updateCodes(self):
            self.codes = self.getCodes()
            self.addDefinitions()

        def filterCodes(self, codes):
            new_codes = []
            for code, definition in codes.items():
                if code != "" and not code.startswith("--"):
                    if definition == "":
                        definition = "No definition available. Try downloading latest code book."
                    new_codes.append((code, definition))
            new_codes.sort(key=lambda x: x[0])
            return new_codes

        def get(self, qid):
            return self.filterCodes(self.codes[qid])

        def initialize(self):
            """
            Since the codebook is a singleton an instance is created at 
            start up (before a survey has been selected), resulting in 
            an error.  Therefore, we shouldn't initialize the codes until
            the first use of the codebook. To avoid recursion, order of 
            lines matters.
            """
            self.initialized = True
            self.updateCodes()
        
        def getQuetions(self):
            return list(self.codes.keys())

        def checkForCodeBook(self):
            path = os.path.join("surveys", self.survey, "files", "codebook.csv")
            return os.path.exists(path)
        
        def search(self, term, qid):
            term = term.lower()
            hits = {}
            codes = self.codes[qid]
            for code, definition in codes.items():
                if term in code.lower() or term in definition.lower():
                    definition = definition.replace("&#39;", "'")
                    hits[code] = definition
            return hits

        def convertXLSXtoCSV(self):
            path = os.path.join("surveys", self.survey, "files", "open-coding-workbook.xlsx")
            workbook = openpyxl.load_workbook(path)
            sheet = workbook['Selection Options']
            csv_path = os.path.join("surveys", self.survey, "files", "codebook.csv")
            with open(csv_path, "w", encoding="utf-8", newline="") as file:
                writer = csv.writer(file)
                for row in sheet.iter_rows(values_only=True):
                    writer.writerow(row)

        def getCodes(self):
            path = os.path.join("surveys", self.survey, "files", "codebook.csv")
            if not os.path.exists(path):
                print(f"Warning: {path} not found.")
                return {}

            with open(path, "r", encoding="utf-8") as file:
                reader = csv.reader(file)
                codes = {}
                for i, row in enumerate(reader):
                    if i == 0:
                        questions = row
                        for column in row:
                            if column != "": codes[column] = {}
                    else:
                        for j, column in enumerate(row):
                            if column != "":
                                codes[questions[j]][column] = ""
                return codes

        def addDefinitions(self):
            path = os.path.join("surveys", self.survey, "files", "open-coding-workbook.xlsx")

            if not os.path.exists(path):
                print(f"{path} does not exist")
                return self.codes

            workbook = openpyxl.load_workbook(path)
            sheet = workbook['Selection Options']

            def getDefinition(comment):
                if comment is None:
                    return ("", "")
                else:
                    comment = comment.text.split('\n\t-')
                    return (comment[0], comment[-1])

            questions = self.getQuetions()
            # Iterate over columns
            for i, column in enumerate(sheet.iter_cols(min_col=1, max_col=len(questions), min_row=3)):
                for cell in column:
                    term = cell.value
                    definition, author = getDefinition(cell.comment)
                    if term != None:
                        definition = definition.replace("'", "&#39;")
                        self.codes[questions[i]][term] = definition
            return self.codes

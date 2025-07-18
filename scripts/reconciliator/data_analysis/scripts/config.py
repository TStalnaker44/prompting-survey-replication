
import json, re, os

class Config():

    def __init__(self, survey):
        self.ranked_answers = {}
        self.loadData(survey)
        self.setTypes()
        self.setQTypes()
        self.shared = ["ResponseID"]

    def loadData(self, survey):
        path = os.path.join(survey, "questions.json")
        with open(path, "r") as file:
            self.data = json.load(file)

    def loadQuestions(self, survey):
        path = os.path.join(survey, "questions.json")
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)

    def setTypes(self):
        self.types = {}
        for label, questions in self.data.items():
            if len(questions.keys()) != 0:
                first_qid = list(questions.keys())[0]
                short_label = re.sub(r'[^A-Za-z]', '', first_qid)
                self.types[short_label] = label
        
    def setQTypes(self):
        self.ranked, self.multi, self.single = [], [], []
        self.likert = []
        self.convertToRange = []
        for label, questions in self.data.items():
            for qid, qdata in questions.items():
                qtype = qdata["type"]
                if (not qdata.get("contains_pii")) and (not qdata.get("ignore")):
                    if qtype in ("single-select", "single-select-with-other", "likert", "single-text"):
                        self.single.append((label, qid))
                    elif qtype in ("short-answer", "email"): pass
                    elif qtype == "multi-select-with-text-entry":
                        self.multi.append(qid)
                    elif qtype == "likert":
                        self.likert.append(qid)
                    elif qtype in ("ranked", "ranked-with-other"):
                        self.ranked.append(qid)
                        self.ranked_answers[qid] = qdata["options"]

                    # If the answers should be converted to a range
                    if qdata.get("convert_to_range"):
                        self.convertToRange.append(qid)
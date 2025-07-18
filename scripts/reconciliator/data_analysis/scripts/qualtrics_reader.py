
import json, os, glob, re, html

TYPE_MAPPING = {"TE":"short-answer",
                "MC":"multi-select",
                "RO":"ranked",
                "CS":"constant-sum",
                "Matrix":"matrix",
                "Slider":"slider"}
SELECTOR_MAPPING = {"SL":"single-text", # Single Line
                    "SAVR":"single-select",
                    "SAHR":"likert"}

def makeQJSON(directory):
    d = readQSF(directory)
    if d:
        groups = getQuestionGroups(d)
        flow = getFlow(d, groups)
        output = makeJSON(flow, groups, d)
        output = filterDefinitionBlocks(output)
        saveJSON(directory, output)

def getQuestionGroups(d):
    blocks = d[0]["Payload"]
    groups = {}
    if type(blocks) == type({}):
        blocks = blocks.values()
    for b in blocks:
        # Questions from trash should not be included
        if not groupEmpty(b) and b["Type"] != "Trash":
            group_name = b["Description"]
            group_id = b["ID"]
            questions = [e["QuestionID"] for e in b["BlockElements"] if e["Type"] == "Question"]
            groups[group_name] = {"id":group_id, "questions":questions}
    return groups

def groupEmpty(group):
    return not group.get("BlockElements", False)

def filterDefinitionBlocks(groups):
    new = {}
    for g in groups:
        temp = {}
        for qname, qinfo in groups[g].items():
            if qinfo["type"] != "DB":
                temp[qname] = qinfo
        new[g] = temp
    return new
                
def getQuestionInfo(qid, d):
    for element in d:
        if element["PrimaryAttribute"] == qid:
            payload = element["Payload"]
            qtext = cleanQText(payload["QuestionText"])
            qname = payload["DataExportTag"]
            qtype = determineQType(payload)
            break
    qinfo = {"question":qtext, "type":qtype, "qual_name":payload["DataExportTag"]}
    if qtype in ("ranked", "ranked-with-other", "multi-select",
                 "single-select", "single-select-with-other", "constant-sum", "constant-sum-with-other",
                 "matrix", "matrix-with-other", "likert"):
        addOptions(qinfo, payload)
    elif qtype in ("multi-select-with-text-entry",):
        addOptionsAndTextEntries(qinfo, payload)
    if qtype in ("matrix", "matrix-with-other"):
        addAnswers(qinfo, payload)
    return qname, qinfo

def cleanQText(text):
    # Handle spaces separately
    text = text.replace("&nbsp;", " ")
    text = text.replace("<br>", " ")
    # Remove HTML tags
    tag_re = re.compile(r'<[^>]+>')
    text = tag_re.sub('', text)
    # Unescape HTML entities (e.g., &amp; -> &)
    text = html.unescape(text)
    return " ".join(text.split())

def addOptions(qinfo, payload):
    options = payload["Choices"]
    qinfo["options"] = [o["Display"] for o in options.values()]

def addOptionsAndTextEntries(qinfo, payload):
    options = payload["Choices"]
    qinfo["options"] = [o["Display"] for o in options.values()]
    qinfo["text-entry-fields"] = [o["Display"] for o in options.values() if o.get("TextEntry")]

def addAnswers(qinfo, payload):
    answers = payload["Answers"]
    qinfo["answers"] = [a["Display"] for a in answers.values()]

def determineQType(payload):
    qtype = payload["QuestionType"]
    qtype = TYPE_MAPPING.get(qtype, qtype)
    if payload["Selector"] in SELECTOR_MAPPING: # Single Line
        qtype = SELECTOR_MAPPING[payload["Selector"]]
    if qtype in ("multi-select", "ranked", "single-select", "constant-sum", "matrix"):
        choices = payload["Choices"]
        if any([choice.get("TextEntry") for choice in choices.values()]):
            if qtype == "multi-select":
                qtype += "-with-text-entry"
            else:
                qtype += "-with-other" # <- TODO: replace this with text entry
    return qtype

def getGroupByID(id, groups):
    for g in groups:
        if groups[g]["id"] == id:
            return g
        
# This gets all of the groups, using the flow element
def getFlow(d, groups):
    elements = d[1]["Payload"]
    lyst = []
    getFlowHelper(elements, groups, lyst)
    return lyst

def getFlowHelper(e, groups, lyst):
    flow = e["Flow"]
    for f in flow:
        if f["Type"] in ("Standard", "Block"):
            g = getGroupByID(f["ID"], groups)
            if g:
                lyst.append(g)
        elif f["Type"] == "Branch":
            getFlowHelper(f, groups, lyst)

def makeJSON(flow, groups, d):
    output = {}
    for block in flow:
        questions_json = {}
        for q in groups[block]["questions"]:
            qname, qinfo = getQuestionInfo(q, d)
            questions_json[qname] = qinfo
        output[block] = questions_json
    return output

# readQSF returns the SurveyElements part of the .qsf file. It returns None if the file did not exist.
def readQSF(directory):
    # For some reason glob.glob cannot find qsf file of surveys with special characters.  
    qsfs = glob.glob(os.path.join(directory, "files", "*.qsf"))
    if len(qsfs) < 1:
        print("No QSF files found.  Please place a QSF file in your survey directory.")
        return None
    else:
        with open(qsfs[0], "r", encoding="utf-8") as file:
            return json.load(file)["SurveyElements"]
        
def saveJSON(directory, d):
    path = os.path.join(directory, "questions.json")
    with open(path, "w", encoding="utf-8") as file:
        json.dump(d, file, indent=4)

if __name__ == "__main__":
    makeQJSON("")
import os, magic
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse
from .scripts.utils import CodeBook
from django.http import JsonResponse
from global_vals import set_coder, get_coder
from .scripts.generateResponseCodingTemplate import TemplateGenerator

# Create your views here.
def chooseCodes(request):

    survey_internal = request.session.get("survey_internal")

    codebook = CodeBook.instance(survey_internal)
    
    if request.method == "GET":
        codebook_exists = codebook.checkForCodeBook()   
        if codebook_exists:
            qid = request.GET.get("qid") or codebook.getQuetions()[0]
            codes = codebook.get(qid)
            questions = codebook.getQuetions()
            return render(request, 'choose_codes.html', {"codes":codes,
                                                        "questions":questions,
                                                        "qid":qid})
        else:
            return render(request, 'upload_code_file.html',
                          {"cur_survey": survey_internal})

    if request.method == 'POST':
        file = request.FILES['fileUpload']
        path = os.path.join("surveys", survey_internal, "files", "open-coding-workbook.xlsx")
        with open(path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        codebook.convertXLSXtoCSV()
        codebook.updateCodes()
        qid = request.POST.get("qid", codebook.getQuetions()[0])
        return redirect(reverse('chooseCodes') + "?qid=" + qid)

def searchCodes(request, question_id, term):
        survey = request.session.get("survey_internal")
        hits = CodeBook.instance(survey).search(term, question_id)
        return render(request, "search_results.html", {"hits":hits})

def selectCoder(request):
    path = os.path.join("surveys", request.session.get("survey_internal"), "coders")
    if request.method == 'POST':
        cur_coder = request.POST.get("select_coder")
        set_coder(cur_coder)
        return redirect("open_coding")
    
    elif request.method == 'GET':
        if len(os.listdir(path)) == 0:
            createCoderDir()

    coders = [c for c in os.listdir(path)]
    if get_coder() is None and coders:
        set_coder(coders[0])
    return render(request, "select_coder.html", {"coders": coders})

def addCoder(request):
    if request.method == "POST":
        createCoderDir()
        path = os.path.join("surveys", request.session.get("survey_internal"), "coders")
        coders = [c for c in os.listdir(path)]
        return render(request, "select_coder.html", {"coders": coders})
        
def createCoderDir():
    path = os.path.join("surveys", request.session.get("survey_internal"), "coders")
    coderId = len(os.listdir(path))
    coderPath = "coder"+ str(coderId + 1)
    os.makedirs(os.path.join(path, coderPath))
    set_coder(coderPath)

def createCodingTemplate(request):
    survey = request.session.get("survey_internal")
    coder_count = 1 # In theory you can have more than one sheet, but not sure it's worth adding a page to collect that info
    tg = TemplateGenerator(survey, coder_count).generateTemplate()
    return render(request, 'create_coding_template.html')

def downloadTemplate(request):
    path = os.path.join("surveys", request.session.get("survey_internal"), "response_coding", "coding_template.xlsx")
    with open(path, "rb") as file:
        contents = file.read()
    response = HttpResponse(contents, content_type='application/octet-stream')
    response['Content-Disposition'] = f'attatchment; filename="coding_template.xlsx"'
    return response

def addResultsCleanup(request):
    survey = request.session.get("survey_internal")
    return render(request, 'result_cleanup_upload.html', {"survey":survey})

def createCleanupFile(request):
    if request.method == 'POST':
        file = request.FILES['fileUpload']
        file_str = str(file)

        # Check that the file type is CSV 
        # TODO: Factor this logic out as it likely gets used more than once
        mime = magic.Magic(mime=True)
        mime_type = mime.from_buffer(file.read(1024))
        file.seek(0)  # Reset file pointer
        csv_mime_types = ['text/csv', 'application/csv', 'application/vnd.ms-excel']
        try:
            if not (mime_type in csv_mime_types or (mime_type == 'text/plain' and file_str[-4:] == '.csv')):
                raise ValidationError('File is not a CSV.')
        except ValidationError as e:
            messages.error(request, str(e))
            return render(request, 'data_upload.html',
                          {"cur_survey": request.session.get("survey_display"), 
                          "error": "Error Uploading: File is not a CSV"})

        # Save the uploaded file to the proper location
        survey_name = request.session.get("survey_internal")
        path = os.path.join("surveys", survey_name, "response_coding", "code_files", "response_clean_up.csv")
        with open(path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        return render(request, 'result_cleanup_upload_success.html')
class Analysis_Config():
    _INSTANCE = None

    @classmethod
    def instance(cls):
        if cls._INSTANCE is None:
            cls._INSTANCE = cls._Config()
        return cls._INSTANCE

    class _Config():
        def __init__(self):
            self.SURVEY = ""
            self.RESPONSE_CODING_DONE = False
            self.FILE_TYPES = ["png"]  # , "pdf"]
            self.QUESTION_TYPES = ["single-select",
                                   "single-select-with-other",
                                   "multi-select",
                                   "multi-select-with-text-entry",
                                   "ranked",
                                   "ranked-with-other",
                                   "likert",
                                   "matrix",
                                   "short-answer",
                                   "single-text",
                                   "email"]

        def set_survey(self, survey):
            self.SURVEY = survey

        def set_response_coding_done(self, response_coding_done):
            self.RESPONSE_CODING_DONE = response_coding_done

        def set_file_types(self, file_types):
            self.FILE_TYPES = file_types


CONFIG = Analysis_Config.instance()

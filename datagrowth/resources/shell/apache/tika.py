import json

from datagrowth.resources.shell import ShellResource


class TextBucket(object):

    def __init__(self, size=2):
        self.bucket = []
        self.size = size

    def shift(self, value):
        bucket = [value] + self.bucket
        self.bucket = bucket[:self.size]

    def pop(self):
        bucket_size = len(self.bucket)
        if not bucket_size:
            return None
        value = self.bucket[0]
        if bucket_size == 1:
            self.bucket = []
        else:
            self.bucket = self.bucket[1:]
        return value

    def is_full(self):
        return len(self.bucket) >= self.size

    def empty(self):
        self.bucket = []


class TikaResource(ShellResource):

    CMD_TEMPLATE = [
        "java",
        "-jar",
        "tika-app-1.19.1.jar",
        "-J",
        "-t",
        "{}"
    ]
    CONTENT_TYPE = "application/json"
    DIRECTORY_SETTING = "DATAGROWTH_BIN_DIR"

    @property
    def content(self):
        content_type, raw = super().content
        if not raw:
            return content_type, raw
        data = json.loads(raw)[0]  # TODO: allow multiple document input
        variables = self.variables()
        data["resourcePath"] = variables["input"][0]
        return content_type, data

    class Meta:
        abstract = True

    @staticmethod
    def extract_texts(title, text):

        if not title or not text:
            return [], [], []

        bucket = TextBucket()
        titles = []
        paragraphs = []
        junk = []
        passed_title = False
        passed_paragraphs = False
        junk_only = False
        for raw_line in text.split("\n"):

            text_line = raw_line.strip()
            if not text_line:
                continue

            if junk_only:
                junk.append(text_line)
                continue

            if text_line in title:
                passed_title = True
                titles.append(text_line)
                continue

            words = text_line.split(" ")
            is_paragraph = len(words) > 10

            if is_paragraph and passed_title:
                passed_paragraphs = True
                paragraphs.append(text_line)
                paragraph_title = bucket.pop()
                if paragraph_title is not None:
                    titles.append(paragraph_title)
                bucket.empty()
            elif is_paragraph and not passed_title:
                junk.append(text_line)

            elif not is_paragraph and not passed_title:
                junk.append(text_line)
            elif not is_paragraph and passed_title:
                if bucket.is_full() and passed_paragraphs:
                    junk_only = True
                else:
                    bucket.shift(text_line)

        return titles, paragraphs, junk

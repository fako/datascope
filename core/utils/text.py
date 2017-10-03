import os
import re

from spacy.tokens import Span

from core.exceptions import DSSystemConfigError


class ArgumentTexts(object):

    def __init__(self, parser, doc):
        self.parser = parser
        self.doc = doc

    def create_span_from_match(self, match, label):
        token_end = -1
        start_token_index = None
        end_token_index = None
        start_char_index = match.start()
        end_char_index = match.end()
        for token in self.doc:
            token_end += len(token.text_with_ws)
            if start_token_index is None and start_char_index < token_end:
                start_token_index = token.i
                continue
            elif end_token_index is None and end_char_index < token_end:
                end_token_index = token.i
                break
        else:
            raise Exception("Could not create a span from match: " + match.group())
        return Span(self.doc, start_token_index, end_token_index, self.doc.vocab.strings[label])

    def get_argument_spans(self):
        for argument_label, argument_match in self.parser.get_arguing_matches(self.doc):
            yield self.create_span_from_match(argument_match, argument_label)


class ArguingLexiconParser(object):

    MACROS_PATH = "system/data/arguing_lexicon/macros"
    PATTERNS_PATH = "system/data/arguing_lexicon/patterns"

    MACRO_PATTERN = re.compile("(@[A-Z0-9]+)")

    MACROS = {}
    PATTERNS = {}

    def system_check(self):
        if not os.path.exists(self.MACROS_PATH):
            raise DSSystemConfigError("Trying to load Arguing Lexicon without macros file")
        if not os.path.exists(self.PATTERNS_PATH):
            raise DSSystemConfigError("Trying to load Arguing Lexicon without patterns file")

    def load_macros(self):
        for entry in os.listdir(self.MACROS_PATH):
            if not entry.endswith(".tff"):
                continue
            with open(self.MACROS_PATH + "/" + entry) as macro_file:
                for macro_line in macro_file.readlines():
                    # Skip empty lines, class definitions and comments
                    if not macro_line.strip():
                        continue
                    if macro_line.startswith("#"):
                        continue
                    # Add macros
                    macro_label, macro_definition = self.preprocess_pattern(macro_line).split("=")
                    macro = [mcr.strip() for mcr in macro_definition.strip().strip("{}").split(",")]
                    self.MACROS[macro_label] = macro

    def preprocess_pattern(self, pattern):
        stripped_pattern = pattern.replace("\\'", "'").strip()
        return "{}\\b".format(stripped_pattern)  # the \b makes sure that a match ends with a non-word token

    def compile_pattern(self, pattern):
        macro_match = self.MACRO_PATTERN.search(pattern)
        if macro_match is None:
            yield re.compile(self.preprocess_pattern(pattern), flags=re.IGNORECASE)
        else:
            macro = macro_match.group(0)
            macro_replacement = "|".join(self.MACROS[macro])
            replaced_pattern = pattern.replace(macro, macro_replacement)
            for preprocessed_pattern in self.compile_pattern(replaced_pattern):
                yield preprocessed_pattern

    def load_patterns(self):
        for entry in os.listdir(self.PATTERNS_PATH):
            if not entry.endswith(".tff"):
                continue
            with open(self.PATTERNS_PATH + "/" + entry) as patterns_file:
                pattern_class = None
                for pattern_line in patterns_file.readlines():
                    # Skip empty lines and comments
                    if not pattern_line.strip():
                        continue
                    if pattern_line.startswith("#") and pattern_class:
                        continue
                    # Read pattern class
                    elif pattern_line.startswith("#"):
                        trash, pattern_class = pattern_line.replace('"', "").split("=")
                        pattern_class = pattern_class.strip()
                        self.PATTERNS[pattern_class] = []
                        continue
                    # Add patterns
                    for preprocessed_patterns in self.compile_pattern(pattern_line):
                        self.PATTERNS[pattern_class].append(preprocessed_patterns)

    def get_arguing_matches(self, doc):
        for arguing_label, arguing_patterns in self.PATTERNS.items():
            for arguing_pattern in arguing_patterns:
                match = arguing_pattern.search(doc.text)
                if match is not None:
                    yield arguing_label, match

    def __init__(self):
        super().__init__()
        self.system_check()
        self.load_macros()
        self.load_patterns()

    def __call__(self, doc):
        doc.user_data["arguments"] = ArgumentTexts(self, doc)

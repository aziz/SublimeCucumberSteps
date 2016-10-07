import sublime_plugin
import sublime
import re
import codecs
from os import path, walk
from . import case_parse

BEHAT_KEYWORDS = ['Given', 'When', 'Then', 'And', 'But']
TEST_FOLDER = 'tests/acceptance'
DEBUG = True
IGNORED_FILES = ['.DS_Store']

class CucumberStepFinder():
    def __init__(self, line, root):
        self.matches = []
        self.step = self.remove_keywords(line)
        # TODO: return if line does not start with a keyword
        self.fn_name = self.prepare_fn_name(self.step)
        self.search_path = self.get_search_path(root)
        self.matches = self.find_implementation(self.fn_name, self.search_path)

        if DEBUG:
            print("FN_NAME: " + self.fn_name)
            print("SEARCH_PATH: " + self.search_path)
            print(self.matches)

    def remove_keywords(self, line):
        step = line
        for keyword in BEHAT_KEYWORDS:
            if line.startswith(keyword):
                step = line.replace(keyword, '', 1)
        return step.strip()

    def prepare_fn_name(self, step):
        # TODO: handle <> and : and tables
        step = re.sub(r'"[^"]+"', '', step)
        return ' ' + self.to_camel_case(step) + '('

    def to_camel_case(self, text):
        words, case, sep = case_parse.parseVariable(text, False, [])
        words[0] = words[0].lower()
        return ''.join(words)

    def get_search_path(self, root):
        return path.join(root, TEST_FOLDER)

    def find_implementation(self, text, search_path):
        matches = []
        for root, dirs, files in walk(search_path):
            for f in files:
                ignored = False
                for ignore_file in IGNORED_FILES:
                    if f == ignore_file:
                        ignored = True
                if ignored:
                    continue
                index = 0
                file_path = path.join(root, f)
                for line in codecs.open(file_path, 'r', 'utf-8'):
                    index = index + 1
                    if re.search(re.escape(text), line):
                        matches.append([file_path, str(index), f, line])
        return matches


class BehatFindImplementationCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        # TODO: return if not valid file
        window = self.view.window()
        self.root_folder = window.extract_variables()['folder']
        self.line = self.line_content()
        self.matches = CucumberStepFinder(self.line, self.root_folder).matches

        if len(self.matches) == 1:
            m = self.matches[0]
            window.open_file(m[0] + ':' + m[1], sublime.ENCODED_POSITION)

        if len(self.matches) > 1:
            items = ([m[2] + ':' + m[1], m[3]] for m in self.matches)
            window.show_quick_panel(list(items), self.on_file_selection)

        if len(self.matches) == 0:
            window.status_message('=> Step not implemented!')

    def on_file_selection(self, row):
        pass

    def line_content(self):
        view = self.view
        cursor = view.sel()[0]
        line_range = view.line(cursor)
        return view.substr(line_range).strip()

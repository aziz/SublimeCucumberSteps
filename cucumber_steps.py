# -*- coding: utf-8 -*-
import sublime_plugin
import sublime
import re
import codecs
from os import path, walk
from . import case_parse

TEST_FOLDER = 'tests/acceptance/bootstrap/'
IGNORED_FILES = ['.DS_Store']

class CucumberStepFinder():
    def __init__(self, line, root):
        self.matches = []
        self.settings = sublime.load_settings('cucumber_steps.sublime-settings')
        self.step = self.remove_keywords(line)
        # TODO: return if line does not start with a keyword
        self.fn_name = self.prepare_fn_name(self.step)
        self.regex_name = self.prepare_regex_name(self.step)
        self.search_path = self.get_search_path(root)

        self.matches = self.find_implementation(self.regex_name, self.search_path)

        if not self.matches:
            self.regex_name_removed_all_caps = re.sub(r'\b[A-Z]{2,}\b', '(.+?)', self.regex_name)
            self.matches = self.find_implementation(self.regex_name_removed_all_caps, self.search_path)

        if not self.matches:
            self.matches = self.find_implementation(self.fn_name, self.search_path)

        if self.settings.get('debug'):
            print("FN_NAME: " + self.fn_name)
            print("REGEX: " + self.regex_name)
            print("SEARCH_PATH: " + self.search_path)
            print(self.matches)

    def remove_keywords(self, line):
        step = line
        for keyword in self.settings.get('cucumber_keywords', []):
            if line.startswith(keyword):
                step = line.replace(keyword, '', 1)
        return step.strip()

    def prepare_regex_name(self, step):
        step = re.sub(r'"[^"]+"', '(.+?)', step)
        step = re.sub(r'\d+', '(.+?)', step)
        step = re.sub(r'<[^>]+>', '(.+?)', step)
        return step

    def prepare_fn_name(self, step):
        # TODO: handle <> and : and tables
        step = re.sub(r'"[^"]+"', '', step)
        return ' ' + self.to_camel_case(step)

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
                    if re.search(text, line):
                        matches.append([file_path, str(index), f, line])
        return matches


class CucumberFindImplementationCommand(sublime_plugin.TextCommand):
    def __init__(self, view):
        self.items = []
        self.view = view

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
            items = list([m[2] + ':' + m[1], m[3]] for m in self.matches)
            window.show_quick_panel(items, self.on_file_selection)

        if len(self.matches) == 0:
            window.status_message('=> Step not implemented!')

    def on_file_selection(self, row):
        m = self.matches[row]
        self.view.window().open_file(m[0] + ':' + m[1], sublime.ENCODED_POSITION)

    def line_content(self):
        view = self.view
        cursor = view.sel()[0]
        line_range = view.line(cursor)
        return view.substr(line_range).strip()

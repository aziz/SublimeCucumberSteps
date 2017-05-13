# -*- coding: utf-8 -*-
import sublime_plugin
import sublime
import subprocess

class BehatSearchCommand(sublime_plugin.WindowCommand):
    def __init__(self, window):
        self.items = []
        self.window = window
        self.__find_step_definitions()

    def run(self):
        self.__find_step_definitions()
        self.window.show_quick_panel(self.items, self.__on_file_selection)

    def __find_step_definitions(self):
        if len(self.items) > 0:
            return
        project_settings = self.window.project_data().get('behat', None)
        if project_settings:
            cmd = project_settings['behat_command'] + ' -dl --no-ansi'
            stdoutdata = subprocess.check_output(cmd, shell=True)
            lines = stdoutdata.decode("utf-8").split("\n")
            self.items = list(map(self.__parse, lines))


    def __parse(self, line):
        step = line[7:-2]
        if step.startswith('^'):
            step = step[1:]
        if step.endswith('$'):
            step = step[:-1]
        return step

    def __on_file_selection(self, row):
        self.window.active_view().run_command('behat_search_insert_step', {'step': self.items[row]})

    def is_enabled(self):
        return bool(self.window.project_data().get('behat', None))


class BehatSearchInsertStepCommand(sublime_plugin.TextCommand):
    def run(self, edit, **args):
        point = self.view.sel()[0].a
        self.view.insert(edit, point, args['step'])

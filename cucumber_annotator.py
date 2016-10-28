# -*- coding: utf-8 -*-
import sublime_plugin
import sublime
from . import cucumber_steps as Steps


class CucumberStepAnnotator(sublime_plugin.ViewEventListener):
    @classmethod
    def applies_to_primary_view_only(cls):
        return True

    @classmethod
    def is_applicable(cls, settings):
        syntax = settings.get('syntax')
        if not syntax:
            return
        plugin_settings = sublime.load_settings('cucumber_steps.sublime-settings')
        supported_syntaxes = plugin_settings.get('supported_syntaxes')
        for s in supported_syntaxes:
            if syntax.endswith(s):
                return True
        return False

    def __init__(self, view):
        self.current_line = (-1, -1)
        self.view = view
        self.settings = sublime.load_settings('cucumber_steps.sublime-settings')

    def is_valid_step(self, step):
        for keyword in self.settings.get('cucumber_keywords', []):
            if step.startswith(keyword):
                return True
        return False

    def on_navigate(self, url):
        if url.startswith('quickpanel://'):
            items = list([m[2] + ':' + m[1], m[3]] for m in self.matches)
            self.view.window().show_quick_panel(items, self.on_file_selection)
        else:
            self.view.window().open_file(url, sublime.ENCODED_POSITION)

    def on_file_selection(self, row):
        m = self.matches[row]
        self.view.window().open_file(m[0] + ':' + m[1], sublime.ENCODED_POSITION)

    def on_selection_modified_async(self):
        view = self.view
        if view.is_dirty():
            view.erase_phantoms("cucumber_steps")
            return
        window = view.window()
        cursor = view.sel()[0]
        line_range = view.line(cursor)
        if view.line(line_range.b) == self.current_line:
            return
        line_content = view.substr(line_range).strip()
        root_folder = window.extract_variables()['folder']
        css = sublime.load_resource("Packages/CucumberSteps/html/ui.css")
        html = sublime.load_resource("Packages/CucumberSteps/html/ui.html")

        if self.is_valid_step(line_content):
            matches = Steps.CucumberStepFinder(line_content, root_folder).matches
            region = sublime.Region(line_range.b, line_range.b)
            self.current_line = view.line(line_range.b)
            view.erase_phantoms("cucumber_steps")
            if len(matches) == 1:
                m = matches[0]
                content = '<span class="label label-success"><a href="' + m[0] + ':' + m[1] + '">➜</a></span>'
                view.add_phantom("cucumber_steps", region, html.format(css=css, content=content), sublime.LAYOUT_INLINE, self.on_navigate)
            elif len(matches) > 1:
                self.matches = matches
                href="quickpanel://"
                content = '<span class="label label-success"><a href="' + href + '">➜</a></span>'
                view.add_phantom("cucumber_steps", region, html.format(css=css, content=content), sublime.LAYOUT_INLINE, self.on_navigate)
            else:
                content = '<span class="label label-error">✘ definition not found</span>'
                view.add_phantom("cucumber_steps", region, html.format(css=css, content=content), sublime.LAYOUT_INLINE)
        else:
            view.erase_phantoms("cucumber_steps")

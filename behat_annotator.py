import sublime_plugin
import sublime
from . import behat_step


class BehatStepAnnotator(sublime_plugin.ViewEventListener):

    @classmethod
    def applies_to_primary_view_only(cls):
        return True

    @classmethod
    def is_applicable(cls, settings):
        syntax = settings.get('syntax')
        # TODO: list of valid systaxes
        if syntax.endswith('Behat-Features.tmLanguage'):
            return True
        return False

    def is_valid_step(self, step):
        for keyword in behat_step.BEHAT_KEYWORDS:
            if step.startswith(keyword):
                return True
        return False

    def on_navigate(self, url):
        self.view.window().open_file(url, sublime.ENCODED_POSITION)

    def on_selection_modified_async(self):
        view = self.view
        window = view.window()
        cursor = view.sel()[0]
        line_range = view.line(cursor)
        line_content = view.substr(line_range).strip()
        root_folder = window.extract_variables()['folder']
        css = sublime.load_resource("Packages/CucumberSteps/html/ui.css")
        html = sublime.load_resource("Packages/CucumberSteps/html/ui.html")

        if self.is_valid_step(line_content):
            matches = behat_step.CucumberStepFinder(line_content, root_folder).matches
            region = sublime.Region(line_range.b, line_range.b)
            view.erase_phantoms("behat")
            if len(matches) == 1:
                m = matches[0]
                content = '<span class="label label-success"><a href="' + m[0] + ':' + m[1] + '">➜ Go to implementation</a></span>'
                view.add_phantom("behat", region, html.format(css=css, content=content), sublime.LAYOUT_INLINE, self.on_navigate)
            else:
                content = '<span class="label label-error">✘ implementation not found</span>'
                view.add_phantom("behat", region, html.format(css=css, content=content), sublime.LAYOUT_INLINE)
        else:
            view.erase_phantoms("behat")

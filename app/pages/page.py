from ..widgets import Widget

class Page(Widget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def switch(self, page):
        self.parent().switch(page)
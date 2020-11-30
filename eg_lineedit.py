import renpy
import string

PRINT = set(string.printable)

class LineEdit(renpy.Displayable):
    cursor = '_'

    def __init__(self, **kwargs):
        super(LineEdit, self).__init__(**kwargs)

        self.text = renpy.Text()
        self.buffer = ''

    @property
    def buffer(self):
        return self._buffer

    @buffer.set
    def buffer(self, v):
        self._buffer = v
        self.text.set_text(v + self.cursor)

    def render(self, w, h, s, a):
        return self.text.render(w, h, s, a)

    def event(self, ev, x, y, s):
        print(ev)

    def visit(self):
        return [self.text]

from PySide6 import QtWidgets


class ToggleSplitterHandle(QtWidgets.QSplitterHandle):

    def mouseDoubleClickEvent(self, e):
        self.parent().toggle_collapse()

class Resize_Splitter(QtWidgets.QSplitter):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Store the previos size of the left hand panel.
        self._previous_state = None

    def createHandle(self):
        return ToggleSplitterHandle(self.orientation(), self)

    def toggle_collapse(self):
        sizes = self.sizes()
        if sizes[0] == 0 and self._previous_state:
            sizes = self._previous_state
        else:
            # Store the size so we can return to it.
            self._previous_state = sizes[:] # store copy so change below doesn't affect stored.
            sizes[0] = 0

        self.setSizes(sizes)

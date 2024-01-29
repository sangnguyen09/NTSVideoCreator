from PySide6.QtCore import Signal
from PySide6.QtWidgets import QSlider


class SliderFloat(QSlider):

    # create our our signal that we can connect to if necessary
    doubleValueChanged = Signal(float)

    def __init__(self, decimals=1, *args, **kargs):
        super(SliderFloat, self).__init__(*args, **kargs)
        self._multi = 10 ** decimals

        self.valueChanged.connect(self.emitDoubleValueChanged)

    def emitDoubleValueChanged(self):
        value = float(super(SliderFloat, self).value()) / self._multi
        self.doubleValueChanged.emit(value)

    def value(self):
        return float(super(SliderFloat, self).value()) / self._multi

    def setMinimum(self, value):
        return super(SliderFloat, self).setMinimum(value * self._multi)

    def setMaximum(self, value):
        return super(SliderFloat, self).setMaximum(value * self._multi)

    def setSingleStep(self, value):
        return super(SliderFloat, self).setSingleStep(value * self._multi)

    def singleStep(self):
        return float(super(SliderFloat, self).singleStep()) / self._multi

    def setValue(self, value):
        super(SliderFloat, self).setValue(int(value * self._multi))
from __future__ import division
from past.utils import old_div
import logging
from vtkAtamai import WindowLevelInteractionMode

logger = logging.getLogger(__name__)


class WindowLevelInteractionMode2(WindowLevelInteractionMode.WindowLevelInteractionMode):

    def __init__(self):
        WindowLevelInteractionMode.WindowLevelInteractionMode.__init__(self)
        self._ListenerMethods = []

    def AddListenerMethod(self, method):
        self._ListenerMethods.append(method)

    def RemoveListenerMethod(self, method):
        self._ListenerMethods.remove(method)

    def DoMotion(self, event):
        if not self._LookupTable:
            return

        table = self._LookupTable

        mlo, mhi = self._DataRange
        lo, hi = table.GetTableRange()

        level = old_div((lo + hi), 2.0)
        window = hi - lo

        level = level + (event.x - self._LastX) * (mhi - mlo) / 500.0
        window = window + (event.y - self._LastY) * (mhi - mlo) / 250.0

        if window <= 0:
            window = 1e-3

        if window > mhi - mlo:
            window = mhi - mlo

        if level > mhi:
            level = mhi

        if level < mlo:
            level = mlo

        lo = level - old_div(window, 2.0)
        hi = level + old_div(window, 2.0)

        if table.IsA('vtkWindowLevelLookupTable'):
            table.SetWindow(window)
            table.SetLevel(level)
        else:
            logger.warning('Using a vtkLookupTable!!')
            table.SetTableRange(lo, hi)
        table.Modified()

        self._LastX = event.x
        self._LastY = event.y

        for method in self._ListenerMethods:
            method(window, level)

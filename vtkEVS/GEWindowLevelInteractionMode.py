import logging
from vtkAtamai import WindowLevelInteractionMode


class GEWindowLevelInteractionMode(WindowLevelInteractionMode.WindowLevelInteractionMode):

    def __init__(self):
        WindowLevelInteractionMode.WindowLevelInteractionMode.__init__(self)
        self._UseMinMax = 0

    def DoButtonPress(self, event):
        self._LastX = event.x
        self._LastY = event.y
        self._StartX = event.x
        self._StartY = event.y

        event.pane.DoStartMotion(event)

    def DoButtonRelease(self, event):
        event.pane.DoEndMotion(event)

    def DoMotion(self, event):
        if not self._LookupTable:
            logging.info(
                "GEWindowLevelInteractionMode: LookupTable must be set!")
            return
        if not self._DataRange:
            logging.info(
                "GEWindowLevelInteractionMode: DataRange must be set!")
            return

        table = self._LookupTable
        min, max = self._DataRange
        # min,max = (0,1024)
        lo, hi = table.GetTableRange()
        level = (lo + hi) / 2.0
        window = hi - lo

        dx = event.x - self._LastX
        dy = event.y - self._LastY
        if dy == 0:
            action = 'horizontal'
        else:
            ratio = abs(float(dx) / dy)
            if ratio >= 1.0:
                action = 'horizontal'
            else:
                action = 'vertical'

        # note:
        # up and down (Y) for Level, or Min
        # left and right (X) for Window or Max

        if self._UseMinMax:
            if action == 'horizontal':
                lo = lo + (event.x - self._LastX) * (max - min) / 300.0
                if lo < min:
                    lo = min
                elif lo > hi:
                    lo = hi
            elif action == 'vertical':
                hi = hi + (event.y - self._LastY) * (max - min) / 300.0
                if hi > max:
                    hi = max
                if hi < lo:
                    hi = lo

            window = hi - lo
            level = (hi + lo) / 2.0

        else:
            if action == 'horizontal':
                window = window + (event.x - self._LastX) * (max - min) / 300.0
            elif action == 'vertical':
                level = level + (event.y - self._LastY) * (max - min) / 300.0

            # need to set limits to window and level
            if window <= 0:
                window = 0.0

            if window > (max - min):
                window = max - min

            if level < min:
                level = min

            if level > max:
                level = max

            lo = level - window / 2.0
            hi = level + window / 2.0

        if table.IsA('vtkWindowLevelLookupTable'):
            table.SetLevel(level)
            table.SetWindow(window)
        else:
            table.SetTableRange(lo, hi)

        table.Modified()

        self._LastX = event.x
        self._LastY = event.y

    def SetUseMinMax(self, bool):
        self._UseMinMax = bool

from __future__ import division
from past.utils import old_div
from vtkAtamai.WindowLevelLabel import WindowLevelLabel as oldWindowLevelLabel
from vtkAtamai.Label import Label
import vtk

#
# Enhanced WindowLevelLabel Widget
#   - Adds Get/Set Opacity functions
#   - Adds Command/Observer pattern hooks
#   - Adds highlight capability

if 'FreeType' in vtk.vtkTextMapper().GetClassName():
    _FS = 18
else:
    _FS = 14


class WindowLevelLabel(oldWindowLevelLabel):

    def __init__(
        self, parent=None, x=0, y=0, width=100, height=27, fontsize=_FS,
            **kw):

        kw["height"] = height
        kw["width"] = width
        kw["x"] = x
        kw["y"] = y
        kw["fontsize"] = fontsize
        kw["font"] = "arial"
        kw["text"] = "W/L"

        Label.__init__(*(self, parent), **kw)

        self._Table = None
        self._DataRange = None
        self._Window = None
        self._Level = None
        self._Shift = 0.0
        self._Scale = 1.0
        self._Pressed = 0
        self._Mapper = None

        self._minmax = False
        self._eventObject = vtk.vtkObject()

        self._actionColor = (1, 0, 0)
        self._defaultColor = kw["foreground"]
        self._highlightColor = (1, 1, 0)

        # add to the configuration dictionary
        self._Config['font'] = 'arial'

        self.BindEvent("<ButtonPress>", self.DoPress)
        self.BindEvent("<ButtonRelease>", self.DoRelease)
        self.BindEvent("<Enter>", self.DoEnter)
        self.BindEvent("<Leave>", self.DoLeave)

        self._SetColor(self._defaultColor)

    def AddObserver(self, event, command):
        self._eventObject.AddObserver(event, command)

    def SetToMinMax(self):
        self._minmax = True
        self._Table.Modified()

    def SetToWindowLevel(self):
        self._minmax = False
        self._Table.Modified()

    def GetTextMapper(self):
        if self._Mapper:
            return self._Mapper
        else:
            for a in self._Actors:
                if a.GetMapper():
                    if a.GetMapper().IsA('vtkTextMapper'):
                        self._Mapper = a.GetMapper()
                        break
            return self._Mapper

    def DoPress(self, event):
        "call back method for Button 1 click"
        self._SetColor(self._actionColor)
        self._Pressed = int(event.num)

    def DoRelease(self, event):
        if (self.IsInWidget(event)):
            self._SetColor(self._highlightColor)
            s = ['LeftButtonPressEvent', 'MiddleButtonPressEvent',
                 'RightButtonPressEvent'][int(event.num) - 1]
            self._eventObject.InvokeEvent(s)
        else:
            self._SetColor(self._defaultColor)
        self._Pressed = 0
        self.Modified()

    def _SetColor(self, color):
        p = self.GetTextMapper().GetTextProperty()
        p.SetColor(color)

    def DoEnter(self, event):
        "call back method for mouse enter"
        self._SetColor(self._highlightColor)
        self.Modified()

    def DoLeave(self, event):
        "callback for mouse leaving"
        self._SetColor(self._defaultColor)
        self.Modified()

    def GetOpacity(self):
        for a in self._Actors:
            if a.GetMapper():
                if not a.GetMapper().IsA('vtkTextMapper'):
                    return a.GetProperty().GetOpacity()

    def SetOpacity(self, o):
        for a in self._Actors:
            if a.GetMapper():
                if not a.GetMapper().IsA('vtkTextMapper'):
                    a.GetProperty().SetOpacity(o)

    def SetLookupTable(self, table):
        oldWindowLevelLabel.SetLookupTable(self, table)
        self._Table.AddObserver('ModifiedEvent', self.cb)

    def SetDataRange(self, range):
        self._DataRange = range
        # reset mode to default
        self._SetColor(self._defaultColor)

    def GetDataRange(self):
        return self._DataRange

    def cb(self, e, o):
        self._Listen(None)

    def _Listen(self, transform):
        min, max = self._Table.GetTableRange()

        self._Window = max - min
        self._Level = old_div((max + min), 2.0)

        # create a formatted string, and set the label
        if self._minmax:
            text = "Min % 6.2f\nMax  % 6.2f" % (min * self._Scale,
                                                max * self._Scale + self._Shift)
        else:
            text = "W % 6.2f\nL  % 6.2f" % (self._Window * self._Scale,
                                            self._Level * self._Scale + self._Shift)
        self.Configure(text=text)

    def _CreateLabel(self):
        oldWindowLevelLabel._CreateLabel(self)
        # over-ride justification of text here
        for a in self._Actors:
            if a.GetMapper():
                if a.GetMapper().IsA('vtkTextMapper'):
                    a.GetMapper().GetTextProperty().SetJustificationToLeft()
                    a.GetMapper().GetTextProperty().BoldOff()

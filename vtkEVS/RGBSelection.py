from __future__ import division
from __future__ import print_function
from past.utils import old_div
import wx


class RGBComponentPicker(wx.Panel):

    """Draws a single bar with two arrows -- may be red, green or blue scale.
       Has hooks for running a callback whenever colour bar is updated."""

    def __init__(self, parent, channel='r'):

        self._pos = 128
        self._clicked = False
        self._cb = None
        self._channel = channel
        self._colours = {'r': (255, 0, 0), 'g': (
            0, 255, 0), 'b': (0, 0, 255)}
        wx.Panel.__init__(self, parent, -1)
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self._width = w = 150
        self._height = h = 16

        self.SetInitialSize((w, h))

        gstops = wx.GraphicsGradientStops()
        gstops.SetStartColour(wx.Colour(0, 0, 0))
        gstops.SetEndColour(wx.Colour(*self._colours[self._channel]))
        gs = wx.GraphicsGradientStop(wx.Colour(0, 0, 0), 0.0)
        gstops.Add(gs)
        gs = wx.GraphicsGradientStop(wx.Colour(
            *self._colours[self._channel]), 1.0)
        gstops.Add(gs)

        ctx = wx.GraphicsContext.CreateMeasuringContext()
        self.gradient_brush = ctx.CreateLinearGradientBrush(
            0, 0, w - 1, 0, gstops)
        self.transparent_brush = ctx.CreateBrush(wx.TRANSPARENT_BRUSH)

        self.Bind(wx.EVT_LEFT_DOWN, self.buttonDown)
        self.Bind(wx.EVT_LEFT_UP, self.buttonUp)
        self.Bind(wx.EVT_MOTION, self.mouseMove)

    def getValue(self):
        return self._pos

    def setValue(self, val):
        self._pos = val

    def OnPaint(self, evt):
        dc = wx.PaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        gc.SetBrush(self.gradient_brush)
        w, h = gc.GetSize()

        # draw gradient box
        gc.DrawRectangle(1, 1, w - 2, h - 2)

        # draw two arrows -- first find x-pos of both arrows
        x = int((old_div(self._pos, 255.0)) * (w - 2))
        s = 5
        y0 = 0
        y1 = y0 + h
        gc.SetPen(wx.Pen('black', 1))
        gc.SetBrush(wx.BLACK_BRUSH)
        gc.DrawLines((wx.Point2D(x - s, y0), wx.Point2D(
            x + s, y0), wx.Point2D(x, y0 + s)))
        gc.SetPen(wx.Pen('white', 1))
        gc.SetBrush(wx.WHITE_BRUSH)
        gc.DrawLines((wx.Point2D(x - s, y1 - 1), wx.Point2D(
            x + s, y1 - 1), wx.Point2D(x, y1 - 1 - s)))

        # draw box around it
        gc.SetPen(wx.Pen('black', 1))
        gc.SetBrush(self.transparent_brush)
        gc.DrawRectangle(0, 0, w - 1, h - 1)

    def setCallback(self, cb):
        """setCallback - sets callback for mouse interaction."""
        self._cb = cb

    def buttonDown(self, evt):
        self._clicked = True
        self.CaptureMouse()
        self.mouseMove(evt)

    def mouseMove(self, evt):

        if self._clicked:
            val = int((evt.x - 1) / float(self._width - 2) * 255.0)
            val = max(0, min(val, 255))
            self.setValue(val)
            self.Refresh()
            if self._cb:
                self._cb(self._channel, self._pos, self._clicked)

    def buttonUp(self, evt):
        if self._clicked:
            self.ReleaseMouse()
        self._clicked = False
        self.mouseMove(evt)

    def setValueAndTriggerCallback(self, v):
        self.setValue(v)
        self.Refresh()
        if self._cb:
            self._cb(self._channel, self._pos, False)

    def setChannel(self, v):
        """Sets the colour channel to modify -
        must be one of 'r', 'g' or 'b' """
        self._channel = v


class RGBColour(wx.Panel):

    def __init__(self, parent, **kw):
        self._comp = {'r': 128, 'g': 128, 'b': 128}
        self._cb = None
        wx.Panel.__init__(self, parent, **kw)
        self.SetInitialSize((52, 52))
        self.SetDoubleBuffered(True)
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def getValue(self):
        return self._comp['r'], self._comp['g'], self._comp['b']

    def setCallback(self, cb):
        self._cb = cb

    def component_callback(self, c, v, done):
        self._comp[c] = v
        if self._cb:
            self._cb(self._comp['r'], self._comp['g'], self._comp['b'], done)

        self.Refresh()

    def OnPaint(self, evt):

        dc = wx.PaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        w, h = gc.GetSize()

        transparent_brush = gc.CreateBrush(wx.TRANSPARENT_BRUSH)

        colour = wx.Colour(self._comp['r'], self._comp['g'], self._comp['b'])

        print(self._comp)

        fill_brush = wx.Brush(colour, wx.SOLID)

        # draw filled box
        gc.SetPen(wx.Pen(colour, 1))
        gc.SetBrush(fill_brush)
        gc.DrawRectangle(0, 0, w - 1, h - 1)

        return

        # draw outline
        gc.SetPen(wx.Pen('black', 1))
        gc.SetBrush(transparent_brush)
        gc.DrawRectangle(0, 0, w - 1, h - 1)


class RGBSelection(wx.Panel):

    def __init__(self, parent, *args, **kw):

        wx.Panel.__init__(self, parent)

        sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(sizer1)
        sizer2 = wx.BoxSizer(wx.VERTICAL)
        sizer1.Add(sizer2, 0, wx.ALL, 2)

        self.components = []
        self._colour = RGBColour(self)

        for v, row in ('r', 0), ('g', 1), ('b', 2):
            self.components.append(RGBComponentPicker(self, channel=v))
            sizer2.Add(self.components[-1], 0, wx.ALL, 1)
            self.components[-1].setCallback(self._colour.component_callback)

        sizer1.Add(self._colour, 0, wx.TOP | wx.BOTTOM, 3)

    def setValue(self, r, g, b):
        if (r != self.components[0].getValue()):
            self.components[0].setValueAndTriggerCallback(r)
        if (g != self.components[1].getValue()):
            self.components[1].setValueAndTriggerCallback(g)
        if (b != self.components[2].getValue()):
            self.components[2].setValueAndTriggerCallback(b)

    def getValue(self):
        return self._colour.getValue()

    def setCallback(self, cb):
        self._colour.setCallback(cb)


#########################################################################
if __name__ == '__main__':

    def cb(r, g, b, done):
        print('value changed:', r, g, b)

    app = wx.App()
    top = wx.Frame(None, title="Test", size=(300, 200))

    sizer1 = wx.BoxSizer(wx.HORIZONTAL)
    top.SetSizer(sizer1)

    rgb = RGBSelection(top)
    rgb.SetSize((300, 100))
    rgb.setValue(0, 128, 255)
    sizer1.Add(rgb, 1, wx.EXPAND, 2)

    top.Show()
    app.MainLoop()

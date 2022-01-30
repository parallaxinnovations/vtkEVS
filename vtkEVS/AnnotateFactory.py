from __future__ import division
# =========================================================================
#
# Copyright (c) 2000-2002 Enhanced Vision Systems
# Copyright (c) 2002-2008 GE Healthcare
# Copyright (c) 2011-2022 Parallax Innovations Inc.
#
# Use, modification and redistribution of the software, in source or
# binary forms, are permitted provided that the following terms and
# conditions are met:
#
# 1) Redistribution of the source code, in verbatim or modified
#   form, must retain the above copyright notice, this license,
#   the following disclaimer, and any notices that refer to this
#   license and/or the following disclaimer.
#
# 2) Redistribution in binary form must include the above copyright
#    notice, a copy of this license and the following disclaimer
#   in the documentation or with other materials provided with the
#   distribution.
#
# 3) Modified copies of the source code must be clearly marked as such,
#   and must not be misrepresented as verbatim copies of the source code.
#
# EXCEPT WHEN OTHERWISE STATED IN WRITING BY THE COPYRIGHT HOLDERS AND/OR
# OTHER PARTIES, THE COPYRIGHT HOLDERS AND/OR OTHER PARTIES PROVIDE THE
# SOFTWARE "AS IS" WITHOUT EXPRESSED OR IMPLIED WARRANTY INCLUDING, BUT
# NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE.  IN NO EVENT UNLESS AGREED TO IN WRITING WILL
# ANY COPYRIGHT HOLDER OR OTHER PARTY WHO MAY MODIFY AND/OR REDISTRIBUTE
# THE SOFTWARE UNDER THE TERMS OF THIS LICENSE BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
# TO, LOSS OF DATA OR DATA BECOMING INACCURATE OR LOSS OF PROFIT OR
# BUSINESS INTERRUPTION) ARISING IN ANY WAY OUT OF THE USE OR INABILITY TO
# USE THE SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.
#
# =========================================================================

#
# This file represents a derivative work by Parallax Innovations Inc.
#

from past.utils import old_div
from vtkAtamai import ActorFactory
import vtk
from zope import component


class AnnotateFactory(ActorFactory.ActorFactory):

    """Displays text at the specified location in the window.

    Derived From:
      ActorFactory

    Parameters:
      renderer - The renderer

    """

    def __init__(self):
        ActorFactory.ActorFactory.__init__(self)
        # used to be 14 but VTK44 doesn't render arial 14 properly
        fontSize = 12

        self._TextMapper = vtk.vtkTextMapper()
        self._TextMapper.SetInput(" ")

        self._TextProperty = self._TextMapper.GetTextProperty()
        self._TextProperty.SetFontSize(fontSize)
        self._TextProperty.SetFontFamilyToArial()
        self._TextProperty.BoldOff()
        self._TextProperty.ItalicOff()
        self._TextProperty.ShadowOff()
        self._TextProperty.SetColor(0.933, 0.505, 0)
        #self._TextProperty.SetColor(1, 1, 1)

        self._Input = None

        self._TextActor = vtk.vtkActor2D()
        self._TextActor.SetMapper(self._TextMapper)

        self._Position = "NW"
        self._Text = ""

        self._RectanglePoints = vtk.vtkPoints()
        self._RectanglePoints.SetNumberOfPoints(4)
        self._RectanglePoints.InsertPoint(0, 0, 0, 0)
        self._RectanglePoints.InsertPoint(1, 0, 0, 0)
        self._RectanglePoints.InsertPoint(2, 0, 0, 0)
        self._RectanglePoints.InsertPoint(3, 0, 0, 0)

        self._Rectangle = vtk.vtkPolygon()
        self._Rectangle.GetPointIds().SetNumberOfIds(4)
        self._Rectangle.GetPointIds().SetId(0, 0)
        self._Rectangle.GetPointIds().SetId(1, 1)
        self._Rectangle.GetPointIds().SetId(2, 2)
        self._Rectangle.GetPointIds().SetId(3, 3)

        self._RectangleGrid = vtk.vtkPolyData()
        self._RectangleGrid.Allocate(1, 1)
        self._RectangleGrid.InsertNextCell(
            self._Rectangle.GetCellType(), self._Rectangle.GetPointIds())
        self._RectangleGrid.SetPoints(self._RectanglePoints)

        self._RectangleOpacity = 0.65

        self._RectangleProperty = vtk.vtkProperty2D()
        self._RectangleProperty.SetColor(0, 0, 0)
        self._RectangleProperty.SetOpacity(self._RectangleOpacity)

        self._ActorRectangle = vtk.vtkActor2D()
        self._ActorRectangle.PickableOff()
        self._ActorRectangle.SetProperty(self._RectangleProperty)
        self._MapperRectangle = vtk.vtkPolyDataMapper2D()

        # VTK-6
        if vtk.vtkVersion().GetVTKMajorVersion() > 5:
            self._MapperRectangle.SetInputData(self._RectangleGrid)
        else:
            self._MapperRectangle.SetInput(self._RectangleGrid)

        self._ActorRectangle.SetMapper(self._MapperRectangle)

    def AddToRenderer(self, renderer):
        """Adds actor to a given renderer

        Args:
            renderer: a VTK renderer
        """
        ActorFactory.ActorFactory.AddToRenderer(self, renderer)
        renderer.AddObserver('StartEvent', self.OnRenderEvent)

    def AddObserver(self, event, callback):
        return self._TextActor.AddObserver(event, callback)

    def SetText(self, text=" "):
        """Specify the text to be displayed by this actor

        Args:
            text (str): The text to display

        """
        self.Modified()
        self._Text = text
        self._TextMapper.SetInput(self._Text)
        self._TextMapper.Modified()

    def OnRenderEvent(self, renderer, evt):

        w = self._TextMapper.GetWidth(renderer)
        h = self._TextMapper.GetHeight(renderer)
        p = self._TextActor.GetPosition()

        if self._Text.strip() == "":
            self._RectanglePoints.InsertPoint(0, 0, 0, 0)
            self._RectanglePoints.InsertPoint(1, 0, 0, 0)
            self._RectanglePoints.InsertPoint(2, 0, 0, 0)
            self._RectanglePoints.InsertPoint(3, 0, 0, 0)
            return

        coord = vtk.vtkCoordinate()
        coord.SetCoordinateSystemToNormalizedViewport()
        coord.SetValue(p[0], p[1])
        p = coord.GetComputedViewportValue(renderer)
        x = p[0]
        y = p[1]

        if len(self._Position) > 1:

            if self._Position[1] == "E":
                x += 5
            elif self._Position[1] == "W":
                x -= 5

        if self._Position[0] == "N":
            y += 5
        elif self._Position[0] == "S":
            y -= 5

        # pad
        w += 10
        h += 10

        if self._Position == "SE":
            self._RectanglePoints.InsertPoint(0, x - w, y, 0)
            self._RectanglePoints.InsertPoint(1, x - w, y + h, 0)
            self._RectanglePoints.InsertPoint(2, x, y + h, 0)
            self._RectanglePoints.InsertPoint(3, x, y, 0)
        elif self._Position == "NW":
            self._RectanglePoints.InsertPoint(0, x, y, 0)
            self._RectanglePoints.InsertPoint(1, x, y - h, 0)
            self._RectanglePoints.InsertPoint(2, x + w, y - h, 0)
            self._RectanglePoints.InsertPoint(3, x + w, y, 0)
        else:
            # default?
            self._RectanglePoints.InsertPoint(0, x - old_div(w, 2), y + h, 0)
            self._RectanglePoints.InsertPoint(1, x - old_div(w, 2), y, 0)
            self._RectanglePoints.InsertPoint(2, x + old_div(w, 2), y, 0)
            self._RectanglePoints.InsertPoint(3, x + old_div(w, 2), y + h, 0)

    def SetColor(self, r, g, b):
        """Set the colour of the actor

        Args:
            r, g, b: Normalized red, green and blue values (0..1)

        """
        self._TextMapper.GetTextProperty().SetColor(r, g, b)

    def GetColor(self):
        """Get the current colour of the actor

        Returns:
            (tuple): The normalized RGB tuple
        """
        return self._TextMapper.GetTextProperty().GetColor()

    def SetFontSize(self, fontsize):
        """Set the font size of this actor

        Args:
            fontsize (int): Font size in points

        """
        if fontsize < 12:
            # fontsize smaller than 12 doesn't look good
            fontsize = 12
        self._TextMapper.GetTextProperty().SetFontSize(fontsize)

    def GetFontSize(self):
        """Get current font size

        Returns:
            int: The font size in points

        """
        return self._TextMapper.GetTextProperty().GetFontSize()

    def BoldOn(self):
        """Display text with bold attributes"""
        self._TextMapper.GetTextProperty().BoldOn()

    def BoldOff(self):
        """Don't display text with bold attributes"""
        self._TextMapper.GetTextProperty().BoldOff()

    def ShadowOn(self):
        """Display text with whitish shadow attributes"""
        self._TextMapper.GetTextProperty().ShadowOn()

    def ShadowOff(self):
        """Don't display text with whitish shadow attributes"""
        self._TextMapper.GetTextProperty().ShadowOff()

    def GetShadow(self):
        """Get current shadow attribute settings

        Returns:
            int: Shadow state.  1 means shadow is enabled.

        """
        return self._TextMapper.GetTextProperty().GetShadow()

    def ToggleBold(self):
        """Toggle bold display state from off to on or on to off"""
        if self._TextMapper.GetTextProperty().GetBold():
            self.BoldOff()
        else:
            self.BoldOn()

    def ToggleShadow(self):
        """Toggle shadow display state from off to on or on to off"""
        if self._TextMapper.GetTextProperty().GetShadow():
            self.ShadowOff()
        else:
            self.ShadowOn()

    def ToggleRectangleOpacity(self):
        pass

    def GetRectangleOpacity(self):
        #      return self._RectangleOpacity
        return False

    # The SetPosition() method allows you to specify where you would like the
    # text to be displayed in the window.  The position parameter can take on the
    # values "N", "NE", "E", "SE", "S", "SW", "W", and "NW".
    def SetPosition(self, position, justify=None):
        self._Position = position
        self._TextActor.GetPositionCoordinate(
        ).SetCoordinateSystemToNormalizedViewport()

        if position == 'N' or position == 'S':
            ypos = position
            xpos = 'C'
        elif position == 'E' or position == 'W':
            xpos = position
            ypos = 'C'
        elif len(position) == 2:
            ypos = position[0]
            xpos = position[1]
        else:
            xpos = 'C'
            ypos = 'C'

        offset = 0.02
        if ypos == 'N':
            self._TextMapper.GetTextProperty().SetVerticalJustificationToTop()
            y = 1 - offset
        elif ypos == 'S':
            self._TextMapper.GetTextProperty(
            ).SetVerticalJustificationToBottom()
            y = offset
        else:
            self._TextMapper.GetTextProperty(
            ).SetVerticalJustificationToCentered()
            y = 0.50

        if xpos == 'E':
            self._TextMapper.GetTextProperty().SetJustificationToRight()
            x = 1 - offset
        elif xpos == 'W':
            self._TextMapper.GetTextProperty().SetJustificationToLeft()
            x = offset
        else:
            self._TextMapper.GetTextProperty().SetJustificationToCentered()
            x = 0.50

        self._TextActor.GetPositionCoordinate().SetValue(x, y)

    def _MakeActors(self):
        return [self._ActorRectangle, self._TextActor]

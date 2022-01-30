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
#    form, must retain the above copyright notice, this license,
#    the following disclaimer, and any notices that refer to this
#    license and/or the following disclaimer.
#
# 2) Redistribution in binary form must include the above copyright
#    notice, a copy of this license and the following disclaimer
#    in the documentation or with other materials provided with the
#    distribution.
#
# 3) Modified copies of the source code must be clearly marked as such,
#    and must not be misrepresented as verbatim copies of the source code.
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

"""
EVSRenderPane2D - a 'RenderPane2D' with some additional functionality.

  EVSRenderPane2D adds a number of key bindings to the default 'RenderPane2D' class.  It also
  implements some basic functionality, such as the ability to zoom the display on a single panel.

See Also:

  RenderPane2D

"""

import logging
import os
import vtk
import wx
from vtkAtamai import RenderPane2D, RenderPane


class EVSRenderPane2D(RenderPane2D.RenderPane2D):

    def __init__(self, master, **kw):

        self._master = master
        self._index = 0
        self._pane_name = kw['name']

        if 'index' in kw:
            self._index = kw['index']
            del(kw['index'])
        else:
            logging.error("EVSRenderPane2D requires an image index!")

        RenderPane2D.RenderPane2D.__init__(self, master, **kw)
        self.SetBorderWidth(2)

        # event object
        self._eventObject = vtk.vtkObject()

        # OrthoPlaneFactory -- we need to set the orthocenter
        self.__orthoPlanes = None

        self._tracked_sliceplane_index = 0

        # the Button 1 action binding
        self._B1Action = 'pan'

        # create some default cursors
        self._cursors = {'winlev': wx.StockCursor(wx.CURSOR_ARROW),
                         'rotate': wx.StockCursor(wx.CURSOR_ARROW),
                         'zoom': wx.StockCursor(wx.CURSOR_MAGNIFIER),
                         'pan': wx.StockCursor(wx.CURSOR_HAND),
                         'slice': wx.StockCursor(wx.CURSOR_ARROW),
                         'spin': wx.StockCursor(wx.CURSOR_ARROW),
                         }
        # override some of the default with cursor if we find them on disk
        for action in ('pan', 'winlev', 'zoom', 'slice', 'spin'):
            filename = os.path.join('Cursors', '%s.gif' % action)
            if os.path.exists(filename):
                try:
                    image = wx.Image(filename)
                    image.SetOptionInt(wx.IMAGE_OPTION_CUR_HOTSPOT_X, 1)
                    image.SetOptionInt(wx.IMAGE_OPTION_CUR_HOTSPOT_Y, 1)
                    self._cursors[action] = wx.CursorFromImage(image)
                except:
                    logging.exception("EVSRenderPane2D")

    def GetName(self):
        return self._pane_name

    def GetImageIndex(self):
        return self._index

    def GetTrackedSliceIndex(self):
        return self._tracked_sliceplane_index

    def SetTrackedSlicePlaneIndex(self, idx):
        self._tracked_sliceplane_index = idx

    def tearDown(self):
        RenderPane2D.RenderPane2D.tearDown(self)

        for actor in self.GetActorFactories():
            actor.RemoveFromRenderer(self._Renderer)
        self._ActorFactories = []

        self.RemoveAllEventHandlers()
        self._eventObject.RemoveAllObservers()
        self._Renderer.RemoveAllObservers()

        del(self._eventObject)
        del(self._master)
        del(self.__orthoPlanes)
        del(self._Renderer)

    def GetObjectState(self):
        return None

    def SetObjectState(self, obj):
        pass

    def AddObserver(self, event, command):
        self._eventObject.AddObserver(event, command)

    def BindDefaultInteraction(self):
        RenderPane2D.RenderPane2D.BindDefaultInteraction(self)
        self.BindPanToButton(1)
        self.BindResetToButton(2, "Shift")

        self.BindEvent("<Left>", self.DecrementPush)
        self.BindEvent("<Down>", self.DecrementPush)
        self.BindEvent("<Right>", self.IncrementPush)
        self.BindEvent("<Up>", self.IncrementPush)
        self.BindEvent("<Next>", self.PriorDecrementPush)
        self.BindEvent("<Prior>", self.NextIncrementPush)
        self.BindEvent("<Home>", self.HomeDecrementPush)
        self.BindEvent("<End>", self.EndIncrementPush)
        self.BindEvent("<KeyPress-t>", self.SavePlaneAsImage)
        self.BindEvent("<Motion>", self.OnMouseMove)

        self.BindSetOrthoCenterToButton(1, modifier='Control')

    def BindSetOrthoCenterToButton(self, button=1, modifier=None):
        self.BindModeToButton((self.SetOrthoCenter,
                               None,
                               self.SetOrthoCenter),
                              button, modifier)

    def SetOrthoCenter(self, event):
        if self.__orthoPlanes:
            pos = self.GetCursorPosition(event)
            if pos:
                self.__orthoPlanes.SetOrthoCenter(pos)

    def GetCursorPositionOnOrthoPlanes(self, evt):
        """Return cursor position on OrthoPlanes."""

        self.DoPickActor(evt)
        infoList = self._PickInformationList
        if len(infoList) > 0:
            for info in infoList:
                if info.factory.IsA('OrthoPlanesFactory') or \
                        info.factory.IsA('SlicePlaneFactory'):
                    return info.position
        return None

    def GetCursorPosition(self, event):
        """Return cursor position on RenderPane."""

        self.DoSmartPick(event)
        infoList = self._PickInformationList
        if len(infoList) > 0:
            for info in infoList:
                if info.factory == self._Plane:
                    return info.position
        return None

    def DoStartMotion(self, event):

        if event.num == 1:
            if event.state == 1:  # Shift key
                curs = self._cursors['pan']
            else:
                curs = self._cursors[self._B1Action]
        elif event.num == 2:
            curs = self._cursors['slice']
        elif event.num == 3:
            curs = self._cursors['zoom']

        self._master.SetCursor(curs)
        RenderPane.RenderPane.DoStartMotion(self, event)

    def DoEndMotion(self, event):
        curs = wx.StockCursor(wx.CURSOR_ARROW)
        self._master.SetCursor(curs)
        RenderPane.RenderPane.DoEndMotion(self, event)

    def DoStartAction(self, event):

        RenderPane2D.RenderPane2D.DoStartAction(self, event)
        self._master.SetCursor(self._cursors['slice'])

    def DoEndAction(self, event):

        RenderPane2D.RenderPane2D.DoEndAction(self, event)
        self._master.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))

    def DoPickActor(self, event):

        RenderPane2D.RenderPane2D.DoPickActor(self, event)

        if self._CurrentActorFactory is not None:
            if event.num > 0:
                self._master.SetCursor(self._cursors['slice'])

    def DoReleaseActor(self, event):

        RenderPane2D.RenderPane2D.DoPickActor(self, event)
        if event.num > 0:
            self._master.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))

    def SetPlaneIntersection(self, planeintersection):
        self._PlaneIntersection = planeintersection

    def EnableMotionMonitoring(self):
        self.BindEvent("<Motion>", self.OnMouseMove)

    def DisableMotionMonitoring(self):
        self.BindEvent("<Motion>", None)

    def SetPlaneIntersections(self, planeintersections):
        self._PlaneIntersections = planeintersections

    def DecrementPush(self, event, factor=1):
        input = self._Plane.GetInput()
        # input.UpdateInformation()  # TODO: fix VTK-6
        spacing = input.GetSpacing()

        Normal = self._Plane.GetNormal()
        UseSpacing = self._Plane.GetUseSpacing()
        self._Plane.SetUseSpacing(True)

        if ((Normal[0] == 0) and (Normal[1] == 0)):
            distance = -spacing[2] * factor
        elif ((Normal[0] == 0) and (Normal[2] == 0)):
            distance = spacing[1] * factor
        else:
            distance = -spacing[0] * factor
        self._Plane.Push(distance)

        self._Plane.SetUseSpacing(UseSpacing)
        self._Plane.Render(self._Renderer)

    def IncrementPush(self, event, factor=1):
        input = self._Plane.GetInput()
        # input.UpdateInformation()  # TODO: fix VTK-6
        spacing = input.GetSpacing()

        Normal = self._Plane.GetNormal()
        UseSpacing = self._Plane.GetUseSpacing()
        self._Plane.SetUseSpacing(True)

        if ((Normal[0] == 0) and (Normal[1] == 0)):
            distance = spacing[2] * factor
        elif ((Normal[0] == 0) and (Normal[2] == 0)):
            distance = -spacing[1] * factor
        else:
            distance = spacing[0] * factor
        self._Plane.Push(distance)

        self._Plane.SetUseSpacing(UseSpacing)
        self._Plane.Render(self._Renderer)

    def PriorDecrementPush(self, event):
        self.DecrementPush(event, 10)

    def NextIncrementPush(self, event):
        self.IncrementPush(event, 10)

    def HomeDecrementPush(self, event):
        input = self._Plane.GetInput()
        # input.UpdateInformation()  # TODO: fix VTK-6
        Normal = self._Plane.GetNormal()
        extent = input.GetExtent()
        if ((Normal[0] == 0) and (Normal[1] == 0)):
            self.DecrementPush(event, extent[5])
        elif ((Normal[0] == 0) and (Normal[2] == 0)):
            self.DecrementPush(event, extent[3])
        else:
            self.DecrementPush(event, extent[1])

    def EndIncrementPush(self, event):
        input = self._Plane.GetInput()
        # input.UpdateInformation()  # TODO: fix VTK-6
        Normal = self._Plane.GetNormal()
        extent = input.GetExtent()
        if ((Normal[0] == 0) and (Normal[1] == 0)):
            self.IncrementPush(event, extent[5])
        elif ((Normal[0] == 0) and (Normal[2] == 0)):
            self.IncrementPush(event, extent[3])
        else:
            self.IncrementPush(event, extent[1])

    # Save the scene in the selected view port
    def SavePlaneAsImage(self, event):
        print "to be implement in application"

    def SetPaneName(self, PaneName):
        self.PaneName = PaneName

    def OnMouseMove(self, event):

        position = self.GetCursorPosition(event)
        self._eventObject.position = position
        self._eventObject.InvokeEvent('MouseMoveEvent')

    def SetOrthoPlanes(self, orthoPlanes):
        self.__orthoPlanes = orthoPlanes

    def GetOrthoPlanes(self):
        """an alternative to call self.GetMicroView().OthoPlane
        be careful with the reference count.
        """
        return self.__orthoPlanes

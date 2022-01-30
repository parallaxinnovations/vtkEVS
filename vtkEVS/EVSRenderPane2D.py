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
from __future__ import print_function

import logging
import os
import vtk
import wx
from vtkAtamai import RenderPane2D, RenderPane
from PI.visualization.common.events import ShowContextSensitiveMenuCommand

# we have references here to MicroView from vtkEVS - this should probably be reworked by sending a generic message instead
from PI.visualization.MicroView.interfaces import IMicroViewMainFrame
from PI.visualization.MicroView import LayoutMenuManager

from zope import component, event

logger = logging.getLogger(__name__)


class EVSRenderPane2D(RenderPane2D.RenderPane2D):

    def __init__(self, parent, **kw):

        self._parent = parent
        self._index = 0
        self._pane_name = kw['name']

        if 'index' in kw:
            self._index = kw['index']
            del(kw['index'])
        else:
            logger.error("EVSRenderPane2D requires an image index!")

        super(EVSRenderPane2D, self).__init__(parent, **kw)
        self.SetBorderWidth(2)

        # event object
        self._eventObject = vtk.vtkObject()

        # OrthoPlaneFactory -- we need to set the orthocenter
        self.__orthoPlanes = None

        self._tracked_sliceplane_index = 0

        # the Button 1 action binding
        self._B1Action = 'pan'

        # create some default cursors
        if 'phoenix' in wx.version():
            _func = wx.Cursor
        else:
            _func = wx.StockCursor

        # keep track of whether mouse moved during right click events
        self._right_click_x = None
        self._right_click_y = None

        self._cursors = {'winlev': _func(wx.CURSOR_ARROW),
                         'rotate': _func(wx.CURSOR_ARROW),
                         'zoom': _func(wx.CURSOR_MAGNIFIER),
                         'pan': _func(wx.CURSOR_HAND),
                         'slice': _func(wx.CURSOR_ARROW),
                         'spin': _func(wx.CURSOR_ARROW),
                         }
        # override some of the default with cursor if we find them on disk
        for action in ('pan', 'winlev', 'zoom', 'slice', 'spin'):
            filename = os.path.join('Cursors', '%s.gif' % action)
            if os.path.exists(filename):
                try:
                    image = wx.Image(filename)
                    if 'phoenix' in wx.version():
                        image.SetOption(wx.IMAGE_OPTION_CUR_HOTSPOT_X, 1)
                        image.SetOption(wx.IMAGE_OPTION_CUR_HOTSPOT_Y, 1)
                        self._cursors[action] = wx.Cursor(image)
                    else:
                        image.SetOptionInt(wx.IMAGE_OPTION_CUR_HOTSPOT_X, 1)
                        image.SetOptionInt(wx.IMAGE_OPTION_CUR_HOTSPOT_Y, 1)
                        self._cursors[action] = wx.CursorFromImage(image)
                except:
                    logger.exception("EVSRenderPane2D")

        # ---------------------------------------------------------------------
        # Set up some zope event handlers
        # ---------------------------------------------------------------------
        component.provideHandler(self.ShowContextSensitiveMenu)

    def GetName(self):
        return self._pane_name

    def GetImageIndex(self):
        return self._index

    def GetTrackedSliceIndex(self):
        return self._tracked_sliceplane_index

    def SetTrackedSlicePlaneIndex(self, idx):
        self._tracked_sliceplane_index = idx

    def tearDown(self):
        try:
            super(EVSRenderPane2D, self).tearDown()

            for actor in self.GetActorFactories():
                actor.RemoveFromRenderer(self._Renderer)
            self._ActorFactories = []

            self.RemoveAllEventHandlers()
            self._eventObject.RemoveAllObservers()
        except Exception as e:
            logger.exception(e)

        # unregister our zope handlers
        gsm = component.getGlobalSiteManager()
        gsm.unregisterHandler(self.ShowContextSensitiveMenu)

        del self._eventObject
        del self._parent
        del self.__orthoPlanes

    def GetObjectState(self):
        return None

    def SetObjectState(self, obj):
        pass

    def AddObserver(self, evt, command):
        self._eventObject.AddObserver(evt, command)

    def BindDefaultInteraction(self):
        super(EVSRenderPane2D, self).BindDefaultInteraction()
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

    def SetOrthoCenter(self, evt):
        if self.__orthoPlanes:
            pos = self.GetCursorPosition(evt)
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

    def GetCursorPosition(self, evt):
        """Return cursor position on RenderPane."""

        self.DoSmartPick(evt)
        infoList = self._PickInformationList
        if len(infoList) > 0:
            for info in infoList:
                if info.factory == self._Plane:
                    return info.position
        return None

    def DoStartMotion(self, evt):

        if evt.num == 1:
            if evt.state == 1:  # Shift key
                curs = self._cursors['pan']
            else:
                curs = self._cursors[self._B1Action]
        elif evt.num == 2:
            curs = self._cursors['slice']
        elif evt.num == 3:

            # keep track of current mouse position - we want to differentiate
            # between zooming and context sensitive menu
            self._right_click_x = evt.x
            self._right_click_y = evt.y

            curs = self._cursors['zoom']

        if evt.num in (1, 2):
            self._parent.SetCursor(curs)

        RenderPane.RenderPane.DoStartMotion(self, evt)

    @component.adapter(ShowContextSensitiveMenuCommand)
    def ShowContextSensitiveMenu(self, evt):

        # ignore messages that don't originate in our window
        if evt.GetWindow() != self:
            return

        popup_menu = wx.Menu()

        wx_version = wx.version()

        # duplicate Window->Layout here
        mvframe = component.getUtility(IMicroViewMainFrame)
        lm = LayoutMenuManager.LayoutMenuManager(mvframe, mvframe.SetLayout)
        lm.UpdateMenus()
        if 'phoenix' in wx.version():
            popup_menu.Append(wx.ID_ANY, '&Layout', lm.GetMenu())
        else:
            popup_menu.AppendMenu(wx.ID_ANY, '&Layout', lm.GetMenu())
        self._parent.PopupMenu(popup_menu)
        popup_menu.Destroy()

    def DoEndMotion(self, evt):

        # keep track of current mouse position - we want to differentiate
        # between zooming and context sensitive menu
        if self._right_click_x is not None:
            if (evt.x == self._right_click_x) and (evt.y == self._right_click_y):
                # a right click menu should be displayed
                event.notify(ShowContextSensitiveMenuCommand(self))

        self._right_click_x = None
        self._right_click_y = None

        if 'phoenix' in wx.version():
            curs = wx.Cursor(wx.CURSOR_ARROW)
        else:
            curs = wx.StockCursor(wx.CURSOR_ARROW)

        self._parent.SetCursor(curs)
        RenderPane.RenderPane.DoEndMotion(self, evt)

    def DoStartAction(self, evt):

        super(EVSRenderPane2D, self).DoStartAction(evt)
        self._parent.SetCursor(self._cursors['slice'])

    def DoEndAction(self, evt):

        super(EVSRenderPane2D, self).DoEndAction(evt)
        self._parent.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))

    def DoPickActor(self, evt):

        super(EVSRenderPane2D, self).DoPickActor(evt)

        if self._CurrentActorFactory is not None:
            if evt.num > 0:
                self._parent.SetCursor(self._cursors['slice'])

    def DoReleaseActor(self, evt):

        super(EVSRenderPane2D, self).DoPickActor(evt)
        if evt.num > 0:
            if 'phoenix' in wx.version():
                cur = wx.Cursor(wx.CURSOR_ARROW)
            else:
                cur = wx.StockCursor(wx.CURSOR_ARROW)
            self._parent.SetCursor(cur)

    def SetPlaneIntersection(self, planeintersection):
        self._PlaneIntersection = planeintersection

    def DoCameraZoom(self, evt):
        """Mouse motion handler for zooming the scene."""

        if (self._right_click_x != None):
            # we should change cursor here
            self._parent.SetCursor(self._cursors['zoom'])
            self._right_click_x = None
            self._right_click_y = None

        super(EVSRenderPane2D, self).DoCameraZoom(evt)

    def EnableMotionMonitoring(self):
        self.BindEvent("<Motion>", self.OnMouseMove)

    def DisableMotionMonitoring(self):
        self.BindEvent("<Motion>", None)

    def SetPlaneIntersections(self, planeintersections):
        self._PlaneIntersections = planeintersections

    def DecrementPush(self, evt, factor=1):

        alg = self._Plane.GetInputConnection()
        producer = alg.GetProducer()
        producer.UpdateInformation()
        image_data = producer.GetOutputDataObject(0)

        spacing = image_data.GetSpacing()

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

    def IncrementPush(self, evt, factor=1):

        alg = self._Plane.GetInputConnection()
        producer = alg.GetProducer()
        producer.UpdateInformation()
        image_data = producer.GetOutputDataObject(0)

        spacing = image_data.GetSpacing()

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

    def PriorDecrementPush(self, evt):
        self.DecrementPush(evt, 10)

    def NextIncrementPush(self, evt):
        self.IncrementPush(evt, 10)

    def HomeDecrementPush(self, evt):

        alg = self._Plane.GetInputConnection()
        producer = alg.GetProducer()
        producer.UpdateInformation()
        image_data = producer.GetOutputDataObject(0)

        Normal = self._Plane.GetNormal()
        extent = image_data.GetExtent()
        if ((Normal[0] == 0) and (Normal[1] == 0)):
            self.DecrementPush(evt, extent[5])
        elif ((Normal[0] == 0) and (Normal[2] == 0)):
            self.DecrementPush(evt, extent[3])
        else:
            self.DecrementPush(evt, extent[1])

    def EndIncrementPush(self, evt):

        alg = self._Plane.GetInputConnection()
        producer = alg.GetProducer()
        producer.UpdateInformation()
        image_data = producer.GetOutputDataObject(0)

        Normal = self._Plane.GetNormal()
        extent = image_data.GetExtent()
        if ((Normal[0] == 0) and (Normal[1] == 0)):
            self.IncrementPush(evt, extent[5])
        elif ((Normal[0] == 0) and (Normal[2] == 0)):
            self.IncrementPush(evt, extent[3])
        else:
            self.IncrementPush(evt, extent[1])

    # Save the scene in the selected view port
    def SavePlaneAsImage(self, evt):
        print("to be implement in application")

    def SetPaneName(self, PaneName):
        self.PaneName = PaneName

    def OnMouseMove(self, evt):

        position = self.GetCursorPosition(evt)
        self._eventObject.position = position
        self._eventObject.evt = evt
        self._eventObject.InvokeEvent('MouseMoveEvent')

    def SetOrthoPlanes(self, orthoPlanes):
        self.__orthoPlanes = orthoPlanes

    def GetOrthoPlanes(self):
        """an alternative to call self.GetMicroView().OthoPlane
        be careful with the reference count.
        """
        return self.__orthoPlanes

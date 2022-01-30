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

import logging
import vtk

from zope import interface

from vtkAtamai import OrthoPlanesFactory, PaneFrame
import EVSSlicePlaneFactory
import OrthoPlanesIntersectionsFactory
from vtkEVS.interfaces import IEVSOrthoPlanesFactory


class EVSOrthoPlanesFactory(OrthoPlanesFactory.OrthoPlanesFactory):

    """Extends the basic functionality of the Atamai OrthoPlanesFactory class."""

    interface.implements(IEVSOrthoPlanesFactory)

    def __init__(self):

        OrthoPlanesFactory.OrthoPlanesFactory.__init__(self)

        self._PickPlane = None
        self._AxialOnOff = 1
        self._CoronalOnOff = 1
        self._SagittalOnOff = 1
        self.__DisableOblique = False
        self._PlanesOutlineOnOff = 1

        self.BindEvent("<Motion>", self.PickPlane)

        # override OrthoPlaneFactory's action colors
        self._PushColor = [1.0, 1.0, 0.0]
        self._RotateColor = [1.0, 0.0, 1.0]
        self._SpinColor = [0.0, 1.0, 1.0]

        # override OrthoPlaneFactory to use different colors
        # for 3 sliceplanes
        red1 = [1.0, 0.0, 0.0]
        green1 = [0.0, 1.0, 0.0]
        blue1 = [0.0, 0.0, 1.0]

        # listen to modified events from our planes
        for plane in self._Planes:
            plane.AddObserver('ModifiedEvent', self.onPlaneModified)

        self._DefaultOutlineColors = (blue1, green1, red1)
        self.SetDefaultOutlineColors()

    def tearDown(self):
        for plane in self._Planes:
            plane.RemoveAllObservers()
        OrthoPlanesFactory.OrthoPlanesFactory.tearDown(self)

    def onPlaneModified(self, evt, obj):
        # if a plane changed, we've changed too
        self.Modified()

    def MakeSlicePlaneFactory(self):
        return EVSSlicePlaneFactory.EVSSlicePlaneFactory()

    def MakePlaneIntersectionsFactory(self):
        return OrthoPlanesIntersectionsFactory.OrthoPlanesIntersectionsFactory()

    def OrthoPlanesReset(self):
        if self.__DisableOblique is True:
            return
        else:
            OrthoPlanesFactory.OrthoPlanesFactory.OrthoPlanesReset(self)

    def GetObjectState(self):
        class EVSOrthoPlanesFactoryData(object):
            pass
        obj = EVSOrthoPlanesFactoryData()
        # plane intersection
        obj.intersection = self.GetOrthoCenter()
        m = self.GetTransform().GetMatrix()
        # plane orientation
        obj.transform = []
        for i in range(4):
            for j in range(4):
                obj.transform.append(m.GetElement(i, j))
        # outline?
        obj.outline = self._PlanesOutlineOnOff
        # which planes to display?
        obj.planesOnOff = [
            self._AxialOnOff, self._CoronalOnOff, self._SagittalOnOff]

        return obj

    def SetObjectState(self, obj):
        m = vtk.vtkMatrix4x4()
        n = 0
        for i in range(4):
            for j in range(4):
                m.SetElement(i, j, obj.transform[n])
                n += 1
        self.GetTransform().SetMatrix(m)
        self.SetOrthoCenter(obj.intersection)
        self.TogglePlanesOutline(obj.outline)

    def Serialize(self):
        try:
            obj = self.GetObjectState()
            return xml_pickle.dumps(obj)
        except:
            return ""

    def DeSerialize(self, s):
        try:
            obj = xml_pickle.loads(s)
            self.SetObjectState(obj)
        except:
            pass

    def HandleEvent(self, event=None):
        """Handles events

        Filters out FocusOut events.  Make sure that this Orthoplane disables
        plane selection, if a focusout gets called

        """
        if event.type == '10':
            self.DoEndAction(event)
        else:
            OrthoPlanesFactory.OrthoPlanesFactory.HandleEvent(self, event)

    def SetDefaultOutlineColors(self):
        for i in range(3):
            self._Planes[i].SetDefaultOutlineColor(
                self._DefaultOutlineColors[i])

    def SetOutlineOpacity(self, opacity):
        for plane in self._Planes:
            try:
                outline = plane.GetChild('Outline')
                outline._Property.SetOpacity(opacity)
            except:
                logging.exception("EVSOrthoPlanesFactory")

    def GetIntersections(self):
        return self._Intersections

    def GetAxialOnOff(self):
        """Returns the visibility of the axial plane image."""
        return self._AxialOnOff

    def GetCoronalOnOff(self):
        """Returns the visibility of the coronal plane image."""
        return self._CoronalOnOff

    def GetSagittalOnOff(self):
        """Returns the visibility of the sagittal plane image."""
        return self._SagittalOnOff

    def ToggleAxialPlane(self, renderer, toggle=None):
        """Toggle the visibility of the axial plane image.

        Args:
            renderer: The renderer to which change is to be applied
            toggle (bool): Optionally set state directly rather than toggle

        """

        plane = self.GetAxialPlane()

        if toggle is None:
            self._AxialOnOff = (self._AxialOnOff + 1) % 2
        else:
            self._AxialOnOff = toggle

        plane.SetVisibility(self._AxialOnOff, 0, renderer)
        self.Modified()

    def ToggleCoronalPlane(self, renderer, toggle=None):
        """Toggle the visibility of the coronal plane image.

        Args:
            renderer: The renderer to which change is to be applied
            toggle (bool): Optionally set state directly rather than toggle

        """

        plane = self.GetCoronalPlane()

        if toggle is None:
            self._CoronalOnOff = (self._CoronalOnOff + 1) % 2
        else:
            self._CoronalOnOff = toggle

        plane.SetVisibility(self._CoronalOnOff, 0, renderer)
        # self.Render()

    def ToggleSagittalPlane(self, renderer, toggle=None):
        """Toggle the visibility of the sagittal plane image.

        Args:
            renderer: The renderer to which change is to be applied
            toggle (bool): Optionally set state directly rather than toggle

        """

        plane = self.GetSagittalPlane()

        if toggle is None:
            self._SagittalOnOff = (self._SagittalOnOff + 1) % 2
        else:
            self._SagittalOnOff = toggle

        plane.SetVisibility(self._SagittalOnOff, 0, renderer)
        # self.Render()

    def AllVisible(self, renderer):
        """Enable plane visibility for all planes

        Args:
            renderer: The renderer to which change is to be applied

        """
        for plane in [self.GetSagittalPlane(), self.GetCoronalPlane(), self.GetAxialPlane()]:
            plane.SetVisibility(1, 0, renderer)
        # self.Render()
        self._SagittalOnOff = self._AxialOnOff = self._CoronalOnOff = 1

    def SetPlaneIntersections(self, planeintersections):
        pass
##     self._PlaneIntersections = planeintersections
# for i in range(3):
# self._Planes[i].SetPlaneIntersections(planeintersections)

    def SetRotateAndSpinOnOff(self, onoff):
        self.__DisableOblique = onoff

    def GetRotateAndSpin(self):
        return self.__DisableOblique

    def DisableRotateAndSpin(self):
        self.__DisableOblique = True

    def EnableRotateAndSpin(self):
        self.__DisableOblique = False

    def DoResetPlanes(self, event=None):
        if self.__DisableOblique:
            return
        self._Transform.Identity()
        self.Modified()
        # invoke an event to notify any observers that we've finished
        # interacting.
        self._MTime.InvokeEvent('EndAction')

    def DoEndAction(self, event):
        """Override to set different colours for plane outlines"""

        OrthoPlanesFactory.OrthoPlanesFactory.DoEndAction(self, event)

        # invoke an event to notify any observers that we've finished
        # interacting.
        self._MTime.InvokeEvent('EndAction')

    def DoEndAction2(self, event):
        """Override to set different colours for plane outlines

        Args:
            event: end action object

        """

        OrthoPlanesFactory.OrthoPlanesFactory.DoEndAction2(self, event)
        self.SetDefaultOutlineColors()

    def DoSpin(self, event):
        if self._Plane is None:
            return
        if self.__DisableOblique:
            return

        # call our parent
        OrthoPlanesFactory.OrthoPlanesFactory.DoSpin(self, event)

# for planeintersection in self._PlaneIntersections:
##         planeintersection.DoSpin(self.GetOrthoCenter(), self._Transform.TransformNormal(self._Plane.GetNormal()), self._dw)
# planeintersection.UpdatePlaneIntersections()

    def DoRotation(self, event):
        if self._Plane is None:
            return

        if self.__DisableOblique:
            return

        # call our parent
        OrthoPlanesFactory.OrthoPlanesFactory.DoRotation(self, event)

# HQ: not work with new vtkAtamai RenderPane, fix please !
# for planeintersection in self._PlaneIntersections:
##       planeintersection.DoRotation(self.GetOrthoCenter(), self._Transform.TransformVector(self.__RotateAxis), self._dw)
# planeintersection.UpdatePlaneIntersections()

    def PickPlane(self, event):
        for plane in self._Planes:
            if event.actor in plane.GetActors(event.renderer):
                self._PickPlane = plane
                break
        # let parent class handle rest of event
        OrthoPlanesFactory.OrthoPlanesFactory.DoAction(self, event)

    def GetPickedPlane(self):
        return self._PickPlane

    def GetPlane(self, idx):
        return self._Planes[idx]

    def SetPickedPlaneByNumber(self, planenumber):
        self._PickPlane = self._Planes[planenumber]

    def TogglePlanesOutline(self, toggle=None):
        """Toggle or set planes outline

        Args:
            toggle (bool):  if defined, set outline visibility to this value, otherwise toggle state

        """
        if toggle is None:
            self._PlanesOutlineOnOff = 1 - self._PlanesOutlineOnOff
        else:
            self._PlanesOutlineOnOff = toggle

        if self._PlanesOutlineOnOff:
            for plane in self._Planes:
                plane.OutlineOn()
        else:
            for plane in self._Planes:
                plane.OutlineOff()

        self.Modified()
        # PaneFrame.RenderAll()

    def GetPlanesOutlineOnOff(self):
        return self._PlanesOutlineOnOff

    def SetOrthoCenter(self, *center):
        """Override OrthoPlanesFactory for oblique planes

        Args:
            center: 3D position of center

        """
        if len(center) == 1:
            center = center[0]

        for plane in self._Planes:
            origin = plane.GetOrigin()
            origin = self._Transform.TransformPoint(origin)
            normal = plane.GetTransformedNormal()

            d = ((center[0] - origin[0]) * normal[0] +
                 (center[1] - origin[1]) * normal[1] +
                 (center[2] - origin[2]) * normal[2])

            plane.Push(d)

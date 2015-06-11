# =========================================================================
#
# Copyright (c) 2000-2002 Enhanced Vision Systems
# Copyright (c) 2002-2008 GE Healthcare
# Copyright (c) 2011-2015 Parallax Innovations Inc.
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

"""
OrthoPlanesIntersectionsFactory - draw colored lines at the
  OrthoPlanes intersections, and cones (triangles) at the
  end of lines if the pane is 2D.

Derived From:

  ActorFactory

Initialization:

  OrthoPlanesIntersectionsFactory()

Public Methods:

  SetPlanes(*planes*) -- set a set of orthoganal SlicePlaneFactories

  SetVisibility(*yesno*, *renderer*=None) -- Set visibility of all
    actors on *renderer*. If *renderer* is not specified,
    all actors made by this factory will be affected. Use set visibility
    method only when the factory has been connected to a renderer.

  SetLineVisibility(*yesno*, *renderer*=None) -- Set the visibility of
    line actors on *renderer*.

  SetEndVisibility(*yesno*, *renderer*=None, *axisIndex*=None) --
    Set the visibility of cone actors of the axis with index of *axisIndex* on
    *renderer*.

  SetColor(*i*, **args*) -- Set color of *i*. *args* could be (r,g,b) or r,g,b.
"""

import math
import vtk
from vtkAtamai import ActorFactory


class OrthoPlanesIntersectionsFactory(ActorFactory.ActorFactory):

    def __str__(self):

        import cStringIO

        s = cStringIO.StringIO()
        # TODO: implement me
        return s.getvalue()

    def __init__(self):
        ActorFactory.ActorFactory.__init__(self)

        colors = ((1, 0, 0), (0, 1, 0), (0, 0, 1))
        self._Properties = []
        for i in range(3):
            property = vtk.vtkProperty()
            property.SetColor(colors[i])
            property.SetAmbient(1.0)
            property.SetOpacity(0.3)
            self._Properties.append(property)

        self._ConeProperties = []
        for i in range(3):
            property = vtk.vtkProperty()
            property.SetColor(colors[i])
            property.SetAmbient(1.0)
            # property.SetOpacity(0.3)
            self._ConeProperties.append(property)

        self._Planes = []
        self._Cutters = []
        self._LineActorsIndex = []
        self._ConeActorsIndex = []

        self._ConeSize = 24.0
        self._Cones = []
        for i in range(6):
            cone = vtk.vtkConeSource()
            cone.SetResolution(2)
            cone.SetHeight(self._ConeSize)
            cone.SetRadius(self._ConeSize)
            self._Cones.append(cone)

    def SetPlanes(self, planes):

        self._Planes = planes

        for i in range(3):
            for j in range(i + 1, 3):
                cutter = vtk.vtkCutter()
                # VTK-6
                if vtk.vtkVersion().GetVTKMajorVersion() > 5:
                    cutter.SetInputData(planes[i].GetPolyData())
                else:
                    cutter.SetInput(planes[i].GetPolyData())
                cutter.SetCutFunction(planes[j].GetPlaneEquation())
                self._Cutters.append(cutter)

    def SetVisibility(self, yesno, renderer=None):
        if renderer is None:
            renderers = self._Renderers
        else:
            renderers = [renderer, ]

        for ren in renderers:
            for actor in self._ActorDict[ren]:
                actor.SetVisibility(yesno)

        self.Modified()

    def SetLineVisibility(self, yesno, renderer=None):

        if renderer is None:
            renderers = self._Renderers
        else:
            renderers = [renderer, ]

        for ren in renderers:
            for i in self._LineActorsIndex:
                self._ActorDict[ren][i].SetVisibility(yesno)

        self.Modified()

    def SetEndVisibility(self, yesno, renderer=None, axisIndex=None):

        if renderer is None:
            renderers = self._Renderers
        else:
            renderers = [renderer, ]

        if axisIndex is None:
            actorsIndex = self._ConeActorsIndex
        else:
            actorsIndex = (3 + 2 * axisIndex, 3 + 2 * axisIndex + 1)

        for ren in renderers:
            for i in actorsIndex:
                self._ActorDict[ren][i].SetVisibility(yesno)

        self.Modified()

    def GetProperties(self):
        return self._Properties

#    def SetColor(self, i, *args):
#
#        # TODO: check this
#        return
#
#        apply(self._Properties[i].SetColor, args)

    def HasChangedSince(self, sinceMTime):

        if ActorFactory.ActorFactory.HasChangedSince(self, sinceMTime):
            return 1
        for plane in self._Planes:
            if plane.HasChangedSince(sinceMTime):
                return 1
        for property in self._Properties:
            if property.GetMTime() > sinceMTime:
                return 1
        return 0

    def AddToRenderer(self, renderer):
        ActorFactory.ActorFactory.AddToRenderer(self, renderer)
        renderer.AddObserver('StartEvent', self.OnRenderEvent)

    def OnRenderEvent(self, ren, event):

        # Abort early if renderer is zero pixels in size
        _sz = ren.GetSize()
        if _sz[0] == 0 or _sz[1] == 0:
            return

        camera = ren.GetActiveCamera()
        v = camera.GetViewPlaneNormal()

        if camera.GetParallelProjection():
            worldsize = camera.GetParallelScale()
            windowWidth, windowHeight = ren.GetSize()
            if windowWidth > 0:
                pitch = worldsize / max(windowWidth, windowHeight)
            else:
                pitch = 1.0
            d1 = worldsize / 100
            d2 = worldsize / 95.

        else:
            d1 = camera.GetDistance() * \
                math.sin(camera.GetViewAngle() / 360.0 * math.pi) / 100
            d2 = d1 * 1.05

        v1 = self._Transform.GetInverse().TransformVector(
            v[0] * d1, v[1] * d1, v[2] * d1)
        v2 = self._Transform.GetInverse().TransformVector(
            v[0] * d2, v[1] * d2, v[2] * d2)

        for i in range(3):
            if camera.GetParallelProjection():
                # only update the cone actors for 2D render panes
                self._Cutters[i].Update()
                x1, x2, y1, y2, z1, z2 = self._Cutters[
                    i].GetOutput().GetBounds()
                self._Planes[0].GetOutput()

                point1 = (x1 + v2[0], y1 + v2[1], z1 + v2[2])
                point2 = (x2 + v2[0], y2 + v2[1], z2 + v2[2])

                point1 = self._Clamp(ren, point1)
                point2 = self._Clamp(ren, point2)

                delta0, delta1, delta2 = (point2[0] - point1[0],
                                          point2[1] - point1[1],
                                          point2[2] - point1[2])
                self._Cones[2 * i].SetDirection(delta0, delta1, delta2)

                if delta1 == 0 and delta2 == 0:
                    delta1 = 0.000000001
                self._Cones[2 * i + 1].SetDirection(-delta0, -delta1, -delta2)

                self._ActorDict[ren][3 + 2 * i].SetScale(pitch)
                self._ActorDict[ren][4 + 2 * i].SetScale(pitch)
                # cone actors
                self._ActorDict[ren][3 + 2 * i].SetPosition(point1)
                self._ActorDict[ren][4 + 2 * i].SetPosition(point2)
            # line actors
            self._ActorDict[ren][i].SetPosition(v1[0], v1[1], v1[2])

    def _Clamp(self, ren, point):
        """Clamps at the boundary of the renderer so that the
        cones would not move beyond.
        """
        x, y, z = self._Transform.TransformPoint(point)
        ren.SetWorldPoint(x, y, z, 1.0)
        ren.WorldToView()
        p = list(ren.GetViewPoint())
        # aspect = ren.GetAspect()
        aspect = (1.0, 1.0)  # adjusted 2014-12-16
        size = ren.GetSize()
        for i in (0, 1):
            margin = aspect[i] - (self._ConeSize / 2.0) / size[i]
            if p[i] < -margin:
                p[i] = -margin
            elif p[i] > margin:
                p[i] = margin

        ren.SetViewPoint(p)
        ren.ViewToWorld()
        x, y, z, w = ren.GetWorldPoint()
        return self._Transform.GetInverse().TransformPoint(x, y, z)

    def _MakeActors(self):

        actors = []

        # lines
        for i in range(3):
            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputConnection(self._Cutters[i].GetOutputPort())
            actor = self._NewActor()
            actor.SetProperty(self._Properties[i])
            actor.SetMapper(mapper)
            actor.PickableOff()
            actors.append(actor)
        # use index to track actors in different renderers
        self._LineActorsIndex = (0, 1, 2)

        # cones
        for i in range(6):
            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputConnection(self._Cones[i].GetOutputPort())
            actor = self._NewActor()
            actor.SetProperty(self._ConeProperties[i / 2])
            actor.SetMapper(mapper)
            actor.PickableOff()
            actors.append(actor)
        self._ConeActorsIndex = (3, 4, 5, 6, 7, 8)

        return actors


"""
RectROIFactory - A 2D ROI selection tool. This class has fewer functionalities
than ROIFactory, but it has an improved user interface.

This class doesn't appear to be used anywhere.

Derived From:

    ActorFactory

Also See:

    ROIFactory

Public Methods:

    HERE! fix me

"""

import vtk
from vtkAtamai import ActorFactory
import math
from vtk.util.colors import tomato, banana


class RectROIFactory(ActorFactory.ActorFactory):

    def __init__(self):
        ActorFactory.ActorFactory.__init__(self)

        self.SetName("RectROI")

        # colors
        self._ActiveColor = (0, 1, 0)
        self._HandleColor = tomato
        self._LineColor = banana

        # Mode 0: Click and Drag to set ROI;
        #      1: Control-Click and drag to set ROI
        self._Mode = 1

        # 4 corner squares
        self._Corners = []
        for i in range(4):
            corner = RectangleSource()
            self._Corners.append(corner)

        self._CornerProperty = vtk.vtkProperty()
        self._CornerProperty.SetOpacity(0)
        self._CornerProperty.SetColor(self._HandleColor)

        # center cross
        self._Center = CrossSource()
        self._CenterProperty = vtk.vtkProperty()
        self._CenterProperty.SetColor(self._HandleColor)
        self._CenterProperty.SetOpacity(0)

        # rectangle ROI
        self._ROI = RectangleSource()
        self._ROIProperty = vtk.vtkProperty()
        self._ROIProperty.SetColor(self._LineColor)
        self._ROIProperty.SetOpacity(0)

        # hack for VCT project: we need to pick the active viewport
        self._viewportManager = None

        # listener method
        self._listenerMethods = []

        # x or y translate only for fixed size ROI, used by VCT scanner
        self._XOnly = False
        self._YOnly = False

        self._clearROI = False

    def GetROIBounds(self):
        return self._ROI.GetBounds()

    def GetROICenter(self):
        return self._ROI.GetCenter()

    def GetROISize(self):
        return self._ROI.GetSize()

    def SetPaneAndMode(self, pane, mode=1):
        """ An override function for creating ROIs from files """
        self._Pane = pane
        self._Mode = mode

        if mode == 0:
            self.SetModeToDragAndSet()
        elif mode == 1:
            self.SetModeToControlDragAndSet()
        elif mode == 2:
            self.SetModeToFixedSizeROI()

    def SetModeToDragAndSet(self):
        self._Mode = 0
        # self._Pane.BindDefaultInteraction() # reset earlier bindings
        self._Pane.BindEvent("<ButtonPress-1>", self._StartDragAndSet)
        self._Pane.BindEvent("<B1-Motion>", None)
        self._Pane.BindEvent("<ButtonRelease-1>", self._EndModifyROI)

    def SetModeToControlDragAndSet(self):
        self._Mode = 1
        # self._Pane.BindDefaultInteraction() # reset earlier bindings
        # disabled for 'aw' style click
        self._Pane.BindEvent("<ButtonPress-1>", self._StartModifyROI)
        self._Pane.BindEvent("<Control-ButtonPress-1>", self._StartDragAndSet)
        self._Pane.BindEvent("<B1-Motion>", None)
        self._Pane.BindEvent("<ButtonRelease-1>", self._EndModifyROI)

    def SetModeToFixedSizeROI(self):
        self._Mode = 2
        self._Pane.BindEvent("<ButtonPress-1>", self._StartModifyFixedSizeROI)
        self._Pane.BindEvent(
            "<Control-ButtonPress-1>", self._StartModifyFixedSizeROI)
        self._Pane.BindEvent("<B1-Motion>", None)
        self._Pane.BindEvent("<ButtonRelease-1>", self._EndModifyROI)

    def SetViewportManager(self, viewportManager):
        self._viewportManager = viewportManager

    def AddListenerMethod(self, method):
        self._listenerMethods.append(method)

    def ResetROISizeAndLocation(self):
        """set a proper initial location and size of the ROI"""

        self.SetModeToControlDragAndSet()

        image = self._GetPaneInput()
        if image is None:
            return
        image.UpdateInformation()
        e = image.GetWholeExtent()
        spacing = image.GetSpacing()
        origin = image.GetOrigin()
        del image
        xc = (e[1] + e[0]) * 0.5 * spacing[0] + origin[0]
        yc = (e[3] + e[2]) * 0.5 * spacing[1] + origin[1]
        xs = (e[1] - e[0]) * 0.4 * spacing[0]
        ys = (e[3] - e[2]) * 0.4 * spacing[1]
        z = 0.001   # use a different 'layer' from the image plane

        # print "image bounds: ", b

        self._ROI.SetBounds((xc - xs, xc + xs, yc - ys, yc + ys, z, z))

        self._Center.SetCenter((xc, yc, z))
        # self._Center.SetSize(0.05*xs)

        self._Corners[0].SetCenter((xc - xs, yc - ys, z))
        self._Corners[1].SetCenter((xc + xs, yc - ys, z))
        self._Corners[2].SetCenter((xc - xs, yc + ys, z))
        self._Corners[3].SetCenter((xc + xs, yc + ys, z))
        # self._SetCornerSizes(0.05*xs)

        self._ROIProperty.SetOpacity(1)
        self._CenterProperty.SetOpacity(1)
        self._CornerProperty.SetOpacity(1)

        self.Modified()

    def SetFixedSize(self, xsize=None, ysize=None):
        """set fixed size ROI"""

        if xsize == None and ysize is None:
            # we need at least one parameter set
            return

        self.SetModeToFixedSizeROI()

        # get image extent
        image = self._GetPaneInput()
        if image is None:
            return
        image.UpdateInformation()
        # b = image.GetBounds()
        e = image.GetWholeExtent()
        print "extent: ", e
        spacing = image.GetSpacing()
        origin = image.GetOrigin()
        del image

        handleSize = 0.02 * (e[1] - e[0]) * spacing[0]

        self.SetModeToFixedSizeROI()

        if xsize is None:
            # xsize full extent, only allow y translate
            xsize = (e[1] - e[0]) * spacing[0]
            self._XOnly = False
            self._YOnly = True

        elif ysize is None:
            # ysize full extent, only allow x translate
            ysize = (e[3] - e[2]) * spacing[1]
            self._XOnly = True
            self._YOnly = False

        else:
            # fixed size, but allow both x and y translate
            self._XOnly = False
            self._YOnly = False

        print "xsize, ysize: ", xsize, ysize
        xc = (e[1] - e[0]) * 0.5 * spacing[0] + origin[0]
        yc = (e[3] - e[2]) * 0.5 * spacing[1] + origin[1]
        xs = xsize * 0.5
        ys = ysize * 0.5

        z = 0.001   # use a different 'layer' from the image plane

        # print "image bounds: ", b

        self._ROI.SetBounds((xc - xs, xc + xs, yc - ys, yc + ys, z, z))

        self._Center.SetCenter((xc, yc, z))
        self._Center.SetSize(handleSize)

# self._Corners[0].SetCenter((xc-xsize,yc-ysize,z))
# self._Corners[1].SetCenter((xc+xsize,yc-ysize,z))
# self._Corners[2].SetCenter((xc-xsize,yc+ysize,z))
# self._Corners[3].SetCenter((xc+xsize,yc+ysize,z))
# self._SetCornerSizes(0)

        self._ROIProperty.SetOpacity(1)
        self._CenterProperty.SetOpacity(1)
        self._CornerProperty.SetOpacity(0)

        self.Modified()

    def _GetPaneInput(self):
        # for compatibility with both ImagePane and RenderPane2D
        if hasattr(self._Pane, 'GetInput'):
            return self._Pane.GetInput()
        else:
            return self._Pane._Plane.GetInput()

    def _GetPaneSlice(self):
        # for compatibility with both ImagePane and RenderPane2D
        if hasattr(self._Pane, 'GetSlice'):
            return self._Pane.GetSlice()
        else:
            return self._Pane._Plane.GetSliceIndex()

    def _GetCursorPosition(self, event):
        # find world-coord from mouse position
        self._Renderers[0].SetDisplayPoint(event.x, event.y, 0.49)
        self._Renderers[0].DisplayToWorld()
        x0, y0, z0, w = self._Renderers[0].GetWorldPoint()
        return self._Transform.GetInverse().TransformPoint(x0 / w, y0 / w, z0 / w)

    def _StartModifyROI(self, event):
        self.diffx = 0.0
        self.diffy = 0.0

        self.transx = 0.0
        self.transy = 0.0

        actor = None
        picklist = self._Pane.DoSmartPick(event)
        if picklist is not None:
            for item in picklist:
                if item.factory == self:
                    actor = item.actor
                    break

        if actor:
            actor.GetProperty().SetColor(self._ActiveColor)
            self.pickedActor = self._ActorDict[event.renderer].index(actor)
            if self.pickedActor == 4:
                # center picked, translate
                self._lastx = 0
                self._lasty = 0
                self._Pane.BindEvent("<B1-Motion>", self._TranslateROI)
            else:
                # resize
                self._ResetROIOrigin(event)
                self._Pane.BindEvent("<B1-Motion>", self._DoExpandROI)
        else:
            self._clearROI = True
            self.curposOffset = (0.0, 0.0)
            self._lastCenter = (0, 0, 0)
            self._ROIProperty.SetOpacity(0)
            self._CornerProperty.SetOpacity(0)
            self._CenterProperty.SetOpacity(0)
            curpos = self._GetCursorPosition(event)
            self.pos = curpos
            for corner in self._Corners:
                corner.SetCenter(curpos)
            self._Center.SetCenter(self.pos)
            self._Pane.BindEvent("<B1-Motion>", self._DoExpandROI)
            # self._Pane.BindEvent("<B1-Motion>", None)

    def _EndModifyROI(self, event):
        self._CornerProperty.SetColor(self._HandleColor)
        self._CenterProperty.SetColor(self._HandleColor)

        # hack to set present RenderPane the active pane
        # and its 'sibblings' inactive
        try:
            for i in range(self._viewportManager.nViewports):
                if self._Pane == self._viewportManager.GetRenderPane(i):
                    self._viewportManager.SetActiveViewport(i)
        except:
            pass

        if self._clearROI:
            for method in self._listenerMethods:
                method(self.pos, (0, 0, 0))

    def _StartDragAndSet(self, event):

        self._Pane = event.pane
        curpos = self._GetCursorPosition(event)
        self.curposOffset = (0.0, 0.0)

        actor = None
        picklist = self._Pane.DoSmartPick(event)
        if picklist is not None:
            for item in picklist:
                if item.factory == self:
                    actor = item.actor
                    break

        self.diffx = 0.0
        self.diffy = 0.0

        self.transx = 0.0
        self.transy = 0.0

        if actor:
            actor.GetProperty().SetColor(self._ActiveColor)
            self.pickedActor = self._ActorDict[event.renderer].index(actor)
            self._CornerProperty.SetOpacity(1)
            self._CenterProperty.SetOpacity(1)

            if self.pickedActor == 4:
                # center picked, translate
                self._lastx = 0
                self._lasty = 0
                self._Pane.BindEvent("<B1-Motion>", self._TranslateROI)
            else:
                # resize
                self._ResetROIOrigin(event)
                self._Pane.BindEvent("<B1-Motion>", self._DoExpandROI)

        else:
            self._lastCenter = (0, 0, 0)
            self._ROIProperty.SetOpacity(0)
            self._CornerProperty.SetOpacity(0)
            self._CenterProperty.SetOpacity(0)
            self._clearROI = True
            self.pos = curpos
            for corner in self._Corners:
                corner.SetCenter(curpos)
            self._Center.SetCenter(self.pos)

            self._Pane.BindEvent("<B1-Motion>", self._DoExpandROI)

    def _ResetROIOrigin(self, event):
        curpos = self._GetCursorPosition(event)

        i = self.pickedActor
        self.pos = self._Corners[3 - i].GetCenter()
        corner = self._Corners[i].GetCenter()

        self.diffx = corner[0] - curpos[0]
        self.diffy = corner[1] - curpos[1]

    def _TranslateROI(self, event):
        self._clearROI = False
        curpos = self._GetCursorPosition(event)
        if (self._lastx == 0 and self._lasty == 0):
            self._lastx = curpos[0]
            self._lasty = curpos[1]

        self.transx = (curpos[0] - self._lastx)
        self.transy = (curpos[1] - self._lasty)

        # Move the ROI
        self._ROI.Translate(self.transx, self.transy, 0)

        # move the corners
        for corner in self._Corners:
            corner.Translate(self.transx, self.transy, 0)

        # move the center
        self._Center.Translate(self.transx, self.transy, 0)

        self._ROIProperty.SetOpacity(1)
        self._CornerProperty.SetOpacity(1)
        self._CenterProperty.SetOpacity(1)

        self._lastx = curpos[0]
        self._lasty = curpos[1]

        for method in self._listenerMethods:
            method(self.GetROICenter(), self.GetROISize())

    def _StartModifyFixedSizeROI(self, event):
        self._clearROI = False
        actor = None
        picklist = self._Pane.DoSmartPick(event)
        if picklist is not None:
            for item in picklist:
                if item.factory == self:
                    actor = item.actor
                    break

        if actor:
            self.pickedActor = self._ActorDict[event.renderer].index(actor)
            if self.pickedActor == 4:
                # show active color
                actor.GetProperty().SetColor(self._ActiveColor)
                # center picked, translate
                self._lastx = 0
                self._lasty = 0
                if self._XOnly:
                    self._Pane.BindEvent("<B1-Motion>", self._TranslateXROI)
                elif self._YOnly:
                    self._Pane.BindEvent("<B1-Motion>", self._TranslateYROI)
                else:
                    self._Pane.BindEvent("<B1-Motion>", self._TranslateROI)
        else:
            self._Pane.BindEvent("<B1-Motion>", None)

    def _TranslateXROI(self, event):
        curpos = self._GetCursorPosition(event)
        if (self._lastx == 0):
            self._lastx = curpos[0]
            # self._lasty = curpos[1]

        self.transx = (curpos[0] - self._lastx)

        # Move the ROI
        self._ROI.Translate(self.transx, 0, 0)

        # move the center
        self._Center.Translate(self.transx, 0, 0)

        self._lastx = curpos[0]

        for method in self._listenerMethods:
            method(self.GetROICenter(), self.GetROISize())

    def _TranslateYROI(self, event):
        curpos = self._GetCursorPosition(event)
        if (self._lasty == 0):
            self._lasty = curpos[1]

        self.transy = (curpos[1] - self._lasty)

        # Move the ROI
        self._ROI.Translate(0, self.transy, 0)

        # move the center
        self._Center.Translate(0, self.transy, 0)

        self._lasty = curpos[1]

        for method in self._listenerMethods:
            method(self.GetROICenter(), self.GetROISize())

    def _DoExpandROI(self, event):
        self._clearROI = False
        curpos = self._GetCursorPosition(event)
        curpos = (curpos[0] + self.diffx, curpos[1] + self.diffy, curpos[2])

        z = curpos[2]

        # Expand ROI
        self._ROI.SetBounds((self.pos[0], curpos[0],
                             self.pos[1], curpos[1],
                             z, z))

        self._Corners[0].SetCenter((self.pos[0], self.pos[1], z))
        self._Corners[1].SetCenter((curpos[0], self.pos[1], z))
        self._Corners[2].SetCenter((self.pos[0], curpos[1], z))
        self._Corners[3].SetCenter((curpos[0], curpos[1], z))

        # center
        self._Center.SetCenter(((self.pos[0] + curpos[0]) / 2.0,
                                (self.pos[1] + curpos[1]) / 2.0,
                                z))

        self._ROIProperty.SetOpacity(1)
        self._CornerProperty.SetOpacity(1)
        self._CenterProperty.SetOpacity(1)

        for method in self._listenerMethods:
            method(self.GetROICenter(), self.GetROISize())

    def _Point2PointDistance(self, a, b):
        return math.sqrt((a[0] - b[0]) * (a[0] - b[0]) +
                         (a[1] - b[1]) * (a[1] - b[1]) +
                         (a[2] - b[2]) * (a[2] - b[2]))

    def _MakeActors(self):
        actors = []
        # 4 corners
        for i in range(4):
            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInput(self._Corners[i].GetOutput())
            actor = self._NewActor()
            actor.SetProperty(self._CornerProperty)
            actor.SetMapper(mapper)
            actors.append(actor)

        # center
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInput(self._Center.GetOutput())
        actor = self._NewActor()
        actor.SetProperty(self._CenterProperty)
        actor.SetMapper(mapper)
        actors.append(actor)

        # rectangle roi
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInput(self._ROI.GetOutput())
        actor = self._NewActor()
        actor.SetProperty(self._ROIProperty)
        actor.SetMapper(mapper)
        actor.PickableOff()
        actors.append(actor)

        return actors

    def _NewActor(self):
        actor = ActorFactory.ActorFactory._NewActor(self)
        return actor

    def AddToRenderer(self, renderer):
        ActorFactory.ActorFactory.AddToRenderer(self, renderer)
        renderer.AddObserver('StartEvent', self.OnRenderEvent)

    def RemoveFromRenderer(self, renderer):
        # self.RemoveStencilFromFilter()
        ActorFactory.ActorFactory.RemoveFromRenderer(self, renderer)

    def OnRenderEvent(self, renderer, ev):
        """This method is called immediately before a render is performed.
        """
        camera = renderer.GetActiveCamera()
        worldsize = camera.GetParallelScale()
        windowWidth, windowHeight = renderer.GetSize()
        if windowWidth > 0 and windowHeight > 0:
            pitch = worldsize / windowHeight
            if self._Mode == 0 or self._Mode == 1:
                self._SetCornerSizes(pitch * 24)
                self._Center.SetSize(pitch * 48)
            elif self._Mode == 2:
                # fixed size, translate only
                self._Center.SetSize(pitch * 48)

                # self._ScaleTransform.Identity()
                # self._ScaleTransform.Scale(16*pitch,16*pitch,16*pitch)

    def _SetCornerSizes(self, size):
        for corner in self._Corners:
            corner.SetSizes(size, size)

""" A polydata source for a cross, used to mark a center,
or point of interest.
"""


class CrossSource(vtk.vtkAppendPolyData):

    def __init__(self):
        self._line1 = vtk.vtkLineSource()
        self._line2 = vtk.vtkLineSource()
        self.AddInput(self._line1.GetOutput())
        self.AddInput(self._line2.GetOutput())

        self._center = (0, 0, 0)
        self._size = 10

    def SetCenter(self, pos):
        self._center = pos
        self._Update()

    def SetSize(self, size):
        self._size = size
        self._Update()

    def Translate(self, transx, transy, transz):
        p = self._center
        self._center = (p[0] + transx, p[1] + transy, p[2] + transz)
        self._Update()

    def _Update(self):

        px, py, pz = self._center
        hs = self._size / 2.0

        self._line1.SetPoint1(px - hs, py, pz)
        self._line1.SetPoint2(px + hs, py, pz)

        self._line2.SetPoint1(px, py - hs, pz)
        self._line2.SetPoint2(px, py + hs, pz)

        self.Update()

""" A PolyData Source of rectangle: used to show an ROI.
"""


class RectangleSource(vtk.vtkAppendPolyData):

    def __init__(self):
        self._lines = []
        for i in range(4):
            line = vtk.vtkLineSource()
            self._lines.append(line)
            self.AddInput(line.GetOutput())

        self._bounds = None
        self._center = None
        self._sizes = None

    def SetBounds(self, bounds):
        "Define the rectangle bounds."
        x0, x1, y0, y1, z0, z1 = bounds
        if x0 > x1:
            x0, x1 = x1, x0
        if y0 > y1:
            y0, y1 = y1, y0
        # we don't care about z

        self._bounds = (x0, x1, y0, y1, z0, z0)
        self._center = ((bounds[0] + bounds[1]) / 2.0,
                        (bounds[2] + bounds[3]) / 2.0,
                        z0)
        self._sizes = ((bounds[1] - bounds[0]),
                       (bounds[3] - bounds[2]))
        self._Update()

    def SetCenter(self, center):
        """Convinient method: move center and keep
        size unchanged.
        """
        self._center = center
        self._UpdateBounds()

    def Translate(self, xtrans, ytrans, ztrans):
        c = self._center
        self.SetCenter((c[0] + xtrans, c[1] + ytrans, c[2] + ztrans))

    def SetSizes(self, xsize, ysize):
        """Convinient method: change the size, but
        keep the center. xsize and ysize are half of the dimensions.
        """
        self._sizes = (xsize, ysize)
        self._UpdateBounds()

    def _UpdateBounds(self):
        if self._center == None or self._sizes is None:
            return
        xc, yc, zc = self._center
        xs, ys = self._sizes[0] * 0.5, self._sizes[1] * 0.5
        self._bounds = (xc - xs, xc + xs, yc - ys, yc + ys, zc, zc)
        self._Update()

    def _Update(self):

        if self._bounds is None:
            return

        x0, x1, y0, y1, z0, z1 = self._bounds

        #  2----line1----3
        #  |             |
        # line2        line3
        #  |             |
        #  0---line0-----1

        p0 = (x0, y0, z0)
        p1 = (x1, y0, z0)
        p2 = (x0, y1, z0)
        p3 = (x1, y1, z0)

        self._lines[0].SetPoint1(p0)
        self._lines[0].SetPoint2(p1)

        self._lines[1].SetPoint1(p2)
        self._lines[1].SetPoint2(p3)

        self._lines[2].SetPoint1(p0)
        self._lines[2].SetPoint2(p2)

        self._lines[3].SetPoint1(p1)
        self._lines[3].SetPoint2(p3)

        self.Update()

    def GetCenter(self):
        return self._center

    def GetBounds(self):
        return self._bounds

    def GetSize(self):
        return self._sizes

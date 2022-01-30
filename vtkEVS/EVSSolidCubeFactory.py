# ========================================================================
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

import vtk
from vtkAtamai import ActorFactory


class EVSSolidCubeFactory(ActorFactory.ActorFactory):

    """displays a rectangular solid"""

    def __init__(self):
        ActorFactory.ActorFactory.__init__(self)
        self._CubeExists = 0
        self._Input = None
        self._Cube = vtk.vtkCubeSource()
        self._Property = vtk.vtkProperty()

    def SetInput(self, input):
        """Associate an image with this object."""
        if input is None:
            return

        self._Input = input
        ActorFactory.ActorFactory.SetTransform(self, self._Input._Transform)
        self.Modified()

    def GetInput(self, input):
        """Returns the image associated with this object."""
        return self._Input

    def SetBounds(self, x1, x2, y1, y2, z1, z2):
        """Set the bounding coordinates of the rectangular solid."""
        # must set the coords in this format
        self._minX = min(x1, x2)
        self._minY = min(y1, y2)
        self._minZ = min(z1, z2)
        self._maxX = max(x1, x2)
        self._maxY = max(y1, y2)
        self._maxZ = max(z1, z2)

        self._Cube.SetROIBounds(
            self._minX, self._maxX, self._minY, self._maxY, self._minZ, self._maxZ)

        self._CubeExists = 1

    def GetBounds(self):
        """Return the two coordinate points defining the rectangular solid."""
        if self._CubeExists == 1:
            return [self._minX, self._maxX, self._minY, self._maxY, self._minZ, self._maxZ]
        else:
            return None

    def SetColor(self, *args):
        """Set the color of the rectangular solid."""
        if len(args) == 1:
            args = args[0]
        apply(self._Property.SetColor, args)

    def GetColor(self):
        """Get the current color of the rectangular solid."""
        return self._Property.GetColor()

    def HasChangedSince(self, sinceMTime):
        if (ActorFactory.ActorFactory.HasChangedSince(self, sinceMTime)):
            return 1
        if (self._Input and self._Input.GetMTime > sinceMTime):
            return 1
        if (self._Input and self._Input.HasChangedSince(sinceMTime)):
            return 1
        return 0

    def SetOpacity(self, opacity):
        """Set the opacity of the rectangular solid."""
        self._Property.SetOpacity(opacity)

    def GetOpacity(self, opacity):
        """Returns the current opacity of the rectangular solid."""
        self._Property.GetOpacity()

    def _MakeActors(self):
        actors = []
        actor = self._NewActor()
        actor.PickableOff()
        actor.SetProperty(self._Property)
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInput(self._Cube.GetOutput())
        actor.SetMapper(mapper)
        actors.append(actor)
        return actors

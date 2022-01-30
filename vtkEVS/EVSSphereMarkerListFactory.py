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

from vtkAtamai import ActorFactory, SphereMarkFactory


class EVSSphereMarkerListFactory(ActorFactory.ActorFactory):

    """Generates a collection of SphereMarkers.

      EVSSphereMarkerListFactor is a container class that keeps a list of SphereMarkers.
      The class is useful for things like registration, where a number of markers needs to be
      displayed on the screen.

    """

    def __init__(self):
        ActorFactory.ActorFactory.__init__(self)
        self.SphereMarkList = []

        # this counter determines the colour of the next sphere.
        self.SphereCounter = 0
        self.SetSphereToEdit(-1)

    def IncrementSphereCounter(self):
        self.SphereCounter = self.SphereCounter + 1

    def SetSphereColor(self):
        length = self.SphereCounter
        div = length / 6
        remainder = length % 6
        if remainder == 0:
            color = [1.0, 0.0, 0.0]
            i = 1
            while (div >= i):
                color[0] = 0.25 + color[0] / 2
                i = i + 1
        elif remainder == 1:
            color = [0.0, 1.0, 0.0]
            i = 1
            while (div >= i):
                color[1] = 0.25 + color[1] / 2
                i = i + 1
        elif remainder == 2:
            color = [0.0, 0.0, 1.0]
            i = 1
            while (div >= i):
                color[2] = 0.25 + color[2] / 2
                i = i + 1
        elif remainder == 3:
            color = [1.0, 1.0, 0.0]
            i = 1
            while (div >= i):
                color[0] = 0.25 + color[0] / 2
                color[1] = 0.25 + color[1] / 2
                i = i + 1
        elif remainder == 4:
            color = [1.0, 0.0, 1.0]
            i = 1
            while (div >= i):
                color[0] = 0.25 + color[0] / 2
                color[2] = 0.25 + color[2] / 2
                i = i + 1
        elif remainder == 5:
            color = [0.0, 1.0, 1.0]
            i = 1
            while (div >= i):
                color[1] = 0.25 + color[1] / 2
                color[2] = 0.25 + color[2] / 2
                i = i + 1

        self.SphereMarkList[len(self.SphereMarkList) - 1].SetColor(
            color[0], color[1], color[2])

    def GetSphereColor(self, i):
        return self.SphereMarkList[i].GetColor()

    def SetSphereOpacity(self, i, a):
        self.SphereMarkList[i].SetOpacity(a)
        self.Modified()
        self.Render()

    # Insert a sphere into the list of spheres and display it.
    def InsertSphere(self, x, y, z, r, g, b, a, i):
        SphereMark = SphereMarkFactory.SphereMarkFactory()
        SphereMark.SetPosition((x, y, z))
        SphereMark.SetOpacity(a)
        SphereMark.SetSize(10.)

        self.SphereMarkList[i:i] = [SphereMark]
        self.SphereMarkList[i].SetColor(r, g, b)

        self.AddChild(self.SphereMarkList[i])
        self.Modified()
        self.Render()

    # Append a sphere to the list of spheres but don't display it.
    def AddSphere(self, x, y, z):
        SphereMark = SphereMarkFactory.SphereMarkFactory()
        SphereMark.SetPosition((x, y, z))
        SphereMark.SetOpacity(0.0)

        SphereMark.SetSize(10.)

        self.SphereMarkList.append(SphereMark)
        self.SetSphereColor()

        self.AddChild(self.SphereMarkList[len(self.SphereMarkList) - 1])

    # Update the coordinates of the sphere and display the sphere.
    def UpdateSphere(self, i, x, y, z):
        self.SphereMarkList[i].SetPosition((x, y, z))
        self.SphereMarkList[i].SetOpacity(1.0)
        self.Modified()
        self.Render()

    def SetSphereToEdit(self, i):
        self.SphereToEdit = i

    def GetSphereToEdit(self):
        return self.SphereToEdit

    def DeleteSphere(self, i):
        if ((i + 1) <= len(self.SphereMarkList)):
            self.RemoveChild(self.SphereMarkList[i])
            del self.SphereMarkList[i]
            if len(self.SphereMarkList) == 0:
                self.SphereCounter = 0
            self.Modified()
            self.Render()
            return 1
        else:
            return 0

    def DeleteAllSpheres(self):
        for i in range(len(self.SphereMarkList)):
            self.RemoveChild(self.SphereMarkList[i])
        self.Modified()
        self.Render()
        self.SphereMarkList = []
        self.SphereCounter = 0
        self.SetSphereToEdit(-1)

    def SetInput(self, i):
        "Set Input"
        self.ImageData = i

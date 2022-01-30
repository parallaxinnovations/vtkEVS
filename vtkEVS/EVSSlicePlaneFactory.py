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
from vtkAtamai import SlicePlaneFactory


class EVSSlicePlaneFactory(SlicePlaneFactory.SlicePlaneFactory):

    """Extends the basic functionality of the Atamai SlicePlaneFactory class."""

    def __init__(self):
        SlicePlaneFactory.SlicePlaneFactory.__init__(self)

        self.__UseSpacing = False
        self._PlaneIntersections = None
        self._sampleFactor = 1.0

    def tearDown(self):
        SlicePlaneFactory.SlicePlaneFactory.tearDown(self)
        self.RemoveAllEventHandlers()
        self.RemoveAllObservers()

    def SetDownSampleFactor(self, v):
        """Set texture downsample factor

        For Texture downsampling.  Set to > 1 to downsample textures and conserve memory

        TODO: is this still needed?

        """
        self._sampleFactor = v
        for name in self._ImageReslicers:
            rs = self._ImageReslicers[name]
            spacing = rs.GetInput().GetSpacing()
            e = list(rs.GetOutputExtent())
            for i in [1, 3, 5]:
                e[i] = int(e[i] / float(v))
            rs.SetOutputSpacing(spacing[0] * v, spacing[1] * v, spacing[2] * v)
            rs.SetOutputExtent(e)

    def GetDownSampleFactor(self):
        return self._sampleFactor

    def SetPlaneIntersections(self, planeintersections):
        self._PlaneIntersections = planeintersections

    def ToggleUseSpacing(self):
        self.SetUseSpacing(not self.GetUseSpacing())

    def SetUseSpacing(self, UseSpacing):

        if not isinstance(UseSpacing, bool):
            logging.error(
                "SetUseSpacing: value {} is not a bool!".format(UseSpacing))
            UseSpacing = bool(UseSpacing)

        # abort early
        if self.__UseSpacing is UseSpacing:
            return

        if UseSpacing is False:
            self.__UseSpacing = False
        else:
            input = self._ImageReslicers[0].GetInput()
            # input.UpdateInformation()  # VTK-6 figure out what to do with
            # this
            spacing = input.GetSpacing()
            origin = input.GetOrigin()

            SlicePosition = self.GetSlicePosition()
            Normal = self.GetNormal()
            if ((Normal[0] == 0) and (Normal[1] == 0)):
                diff = (round((SlicePosition - origin[2]) / spacing[2]) -
                        ((SlicePosition - origin[2]) / spacing[2])) * spacing[2]
            elif ((Normal[0] == 0) and (Normal[2] == 0)):
                diff = (((SlicePosition - origin[1]) / spacing[1]) -
                        round((SlicePosition - origin[1]) / spacing[1])) * spacing[1]
            else:
                diff = (round((SlicePosition - origin[0]) / spacing[0]) -
                        ((SlicePosition - origin[0]) / spacing[0])) * spacing[0]

            self.Push(diff)
            self.__UseSpacing = True

    def GetUseSpacing(self):
        return self.__UseSpacing

    def Push(self, distance):
        """Move the selected slice plane a given distance"""

        # abort early
        if distance == 0.0:
            return

        if self.__UseSpacing is True:
            input = self._ImageReslicers[0].GetInput()
            self._ImageReslicers[0].UpdateInformation()
            # input.UpdateInformation()  # TODO: VTK-6 fix required here
            spacing = input.GetSpacing()

            Normal = self.GetNormal()
            if ((Normal[0] == 0) and (Normal[1] == 0)):
                SpacingDistance = round(distance / spacing[2]) * spacing[2]
            elif ((Normal[0] == 0) and (Normal[2] == 0)):
                SpacingDistance = round(distance / spacing[1]) * spacing[1]
            else:
                SpacingDistance = round(distance / spacing[0]) * spacing[0]
        else:
            SpacingDistance = distance

        # just like vtkPlane::Push()
        o1 = self.GetTransformedCenter()

        self._Plane.Push(SpacingDistance)
        self._Plane.Update()

        self._UpdateOrigin()
        o2 = self.GetTransformedCenter()
        n = self.GetTransformedNormal()
        # JDG - don't call Modified() here -- it gets called in _UpdateOrigin() indirectly
        # self.Modified()

        # return the actual amount pushed, in case we hit bounds
        return (o2[0] - o1[0]) * n[0] + (o2[1] - o1[1]) * n[1] + (o2[2] - o1[2]) * n[2]

    def GetImageReslicers(self):
        return self._ImageReslicers

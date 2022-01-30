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

import AnnotateFactory
import vtk


class IntensityAnnotateFactory(AnnotateFactory.AnnotateFactory):

    """Displays intensity, or gray scale value, of the point of interest at the specified location in the window.

    vtkImageReslice is used to calculate the intensity at the point of interest.

    Parameters:
        dimension : 2 or 3. Specify 2D or 3D coordinates to display.

    """

    def __init__(self, dimension=3):
        AnnotateFactory.AnnotateFactory.__init__(self)

        self._Transform = None

        self._Shift = 0.0
        self._Scale = 1.0

        self._Input = None
        self._defaultLabel = 'Gray Scale Value'

        self._Reslice = vtk.vtkImageReslice()
        self._Reslice.SetOutputExtent(0, 0, 0, 0, 0, 0)
        self._Reslice.InterpolateOff()
        # HQ: vtkImageReslice doesn't work well for 2D image when interpolate is on.
        # self._Reslice.SetInterpolationModeToLinear()
        self._Dimension = dimension

        self._Point = None
        self._Intensity = None
        self.measurementUnit = 'mm'

    def SetInterpolate(self, interpolation):
        self._Reslice.SetInterpolate(interpolation)

    def GetInterpolate(self):
        return self._Reslice.GetInterpolate()

    def GetInterpolation(self):
        return self._reslice.GetInterpolation()

    def SetInput(self, input):

        self._Point = None
        self._Intensity = None
        self._Input = input
        self._Reslice.SetInput(input)

    def GetInput(self):
        return self._Input

    def SetShift(self, shift):
        self._Shift = shift

    def GetShift(self):
        return self._Shift

    def SetScale(self, scale):
        self._Scale = scale

    def GetScale(self):
        return self._Scale

    def SetTransform(self, transform):
        self._Transform = transform

    def GetTransform(self):
        return self._Transform

    def SetPointOfInterest(self, position):
        """ Set the point (x,y,z).

        We'll find the gray scale intensity and set the annotate text.

        """

        if not position:
            self.SetText(self._defaultLabel + ":\n(x,y,z)(%s)" % (
                self.measurementUnit))
            return

        x, y, z = position
        if self._Transform:
            x, y, z = self._Transform.TransformPoint(x, y, z)

        self._Reslice.SetOutputOrigin(x, y, z)

        # handle the case where our input is Null
        o = self._Reslice.GetInput()
        if o is None:
            return

        o.Update()
        self._Reslice.GetOutput().SetUpdateExtent(0, 0, 0, 0, 0, 0)
        self._Reslice.GetOutput().Update()

        numC = self._Reslice.GetOutput().GetNumberOfScalarComponents()

        val = []
        for i in range(numC):
            try:
                v = self._Reslice.GetOutput().GetScalarComponentAsDouble(
                    0, 0, 0, i)
            except AttributeError:
                v = self._Reslice.GetOutput().GetScalarComponentAsFloat(
                    0, 0, 0, i)
            val.append(v * self._Scale + self._Shift)

        self.RefreshText(val, position)

    def SetPoint(self, x, y, z):
        "Compatibility method to replace PointSelectionFactory."
        self.SetPointOfInterest((x, y, x))

    def SetMeasurementUnits(self, measurementUnit):
        self.measurementUnit = measurementUnit
        self.Modified()
        self.RefreshText()

    def RefreshText(self, intensity=None, point=None):
        "Update the current text displayed on the screen."

        self._Intensity = intensity
        self._Point = point

        if self._Input == None or self._Point is None:
            self.SetText(self._defaultLabel + ":\n(x,y,z)(%s)" % (
                self.measurementUnit))
            return

        x0, y0, z0 = self._Input.GetOrigin()
        xstep, ystep, zstep = self._Input.GetSpacing()
        type = self._Input.GetScalarType()

        x, y, z = self._Point

        # intensity annotate
        numC = self._Input.GetNumberOfScalarComponents()

        if numC == 1:
            self._defaultLabel = 'Gray Scale Value'
        elif numC == 3:
            self._defaultLabel = 'RGB'
        elif numC == 4:
            self._defaultLabel = 'RGBA'

        if type == vtk.VTK_FLOAT:
            line1 = self._defaultLabel + ": " + \
                (numC - 1) * '%1.3f, ' + '%1.3f\n'
            line1 = line1 % tuple(self._Intensity)
        else:
            line1 = self._defaultLabel + ": " + \
                (numC - 1) * '%1.0f, ' + '%1.0f\n'
            line1 = line1 % tuple(self._Intensity)

        # position annotate
        if self.measurementUnit == "mm":
            if self._Dimension == 3:
                line2 = "(%.3f, %.3f, %.3f) (mm)" % (x, y, z)
            else:
                line2 = "(%.3f, %.3f) (mm)" % (x, y)
        else:
            x = (x - x0) / xstep
            y = (y - y0) / ystep
            z = (z - z0) / zstep
            if self._Dimension == 3:
                line2 = "(%.1f, %.1f, %.1f) (pixel)" % (x, y, z)
            else:
                line2 = "(%.1f, %.1f) (pixel)" % (x, y)

        self.SetText(line1 + line2)

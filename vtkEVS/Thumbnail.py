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

import vtk
import base64
import tempfile
import os


class Thumbnail(object):

    def __init__(self):
        self._image = None
        self._threshold = 0

    def SetInput(self, im):
        self._image = im

    def GetInput(self):
        return self._image

    def SetThreshold(self, t):
        self._threshold = t

    def GetThreshold(self):
        return self._threshold

    def GetThumbnailAsString(self):
        """Returns a base64 encoded string version of the thumbnail"""
        fn = tempfile.mktemp('.jpg')
        self.WriteImageToDisk(fn)
        s = open(fn, 'rb').read()
        os.unlink(fn)
        return base64.encodestring(s)

    def WriteImageToDisk(self, filename):
        """Writes thumbnail to disk"""
        ren = vtk.vtkRenderer()
        renWin = vtk.vtkRenderWindow()
        renWin.AddRenderer(ren)
        ren.SetBackground(1.0, 1.0, 1.0)
        renWin.SetSize(200, 200)
        renWin.OffScreenRenderingOn()

        # determine image range
        self._image.Update()
        r = self._image.GetScalarRange()
        t = self._threshold

        # determine image spacing
        sp = self._image.GetSpacing()

        # cast image to unsigned char
        typ = self._image.GetScalarType()
        if ((typ != 3) or (typ != 5)):
            cast = vtk.vtkImageShiftScale()
            cast.SetInput(self._image)
            cast.SetOutputScalarTypeToUnsignedChar()
            cast.SetShift(-r[0])
            if r[1] == r[0]:
                cast.SetScale(255.0 / (r[1] - r[0] + 1))
                t = (self._threshold - r[0]) * (255.0 / (r[1] - r[0] + 1))
            else:
                cast.SetScale(255.0 / (r[1] - r[0]))
                t = (self._threshold - r[0]) * (255.0 / (r[1] - r[0]))
            r = [0, 255.0]
            o = cast.GetOutput()
        else:
            o = self._image.GetOutput()

        # build a LUT
        tfun = vtk.vtkPiecewiseFunction()
        tfun.AddPoint(r[0], 0.0)
        tfun.AddPoint(t - (r[1] - r[0]) / 1024., 0.0)
        tfun.AddPoint(t, 0.2)
        tfun.AddPoint(r[1], 0.2)
        ctfun = vtk.vtkColorTransferFunction()
        ctfun.AddRGBPoint(r[0], 1, 1, 1)
        ctfun.AddRGBPoint(r[1], 1, 1, 1)

        function = vtk.vtkVolumeRayCastIsosurfaceFunction()	         # tunable
        function.SetIsoValue(t)
        volumeMapper = vtk.vtkVolumeRayCastMapper()
        volumeMapper.SetInput(o)
        volumeMapper.SetVolumeRayCastFunction(function)
        volumeMapper.SetSampleDistance(max(sp) * 1.0)              # tunable
        volumeProperty = vtk.vtkVolumeProperty()
        volumeProperty.SetColor(ctfun)
        volumeProperty.SetScalarOpacity(tfun)
        volumeProperty.SetInterpolationTypeToLinear()            # tunable
        volumeProperty.ShadeOn()

        newvol = vtk.vtkVolume()
        newvol.SetMapper(volumeMapper)
        newvol.SetProperty(volumeProperty)

        # Add volume to renderer
        ren.AddVolume(newvol)

        # set up inital camera
        camera = ren.GetActiveCamera()
        camera.Elevation(-60.0)
        camera.SetViewAngle(20)

        # grab image
        renWin.Render()
        windowToimage = vtk.vtkWindowToImageFilter()
        windowToimage.SetInput(renWin)

        # save image
        writer = vtk.vtkJPEGWriter()
        writer.SetInput(windowToimage.GetOutput())
        writer.SetFileName(filename)
        writer.SetQuality(85)
        writer.Write()

if __name__ == '__main__':
    import PI.visualization.vtkMultiIO.vtkVFFReader as vtkVFFReader

    # grab image
    r = vtkVFFReader.vtkVFFReader()
    r.SetFileName(r'D:\Images\7um_spine_section_14um.vff')

    # Get thumbnail
    t = Thumbnail()
    t.SetInput(r.GetOutput())
    t.SetThreshold(2800)
    t.WriteImageToDisk('c:\\out9.jpg')

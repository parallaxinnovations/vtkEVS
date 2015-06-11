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
from vtkAtamai import ActorFactory, AnatomicalLabelsFactory


class EVSAnatomicalLabelsFactory(AnatomicalLabelsFactory.AnatomicalLabelsFactory):

    """Displays anatomical labels around the edges of an image.

      EVSAnatomicalLabelsFactory is simply an extension to the default
      'AnatomicalLabelsFactory' class that comes from Atamai.  The class
      adds only the option to toggle its opacity.

    """

    def __init__(self, labels=['-X', '+X', '-Y', '+Y', '-Z', '+Z']):
        AnatomicalLabelsFactory.AnatomicalLabelsFactory.__init__(self, labels)
        self._Visibility = 1
        self._textObjects = []

    def SetVisibility(self, val):
        """Sets the actor visibility

        Args:
            val (int): 0 or 1.  1 indicates actor is visible.

        """
        self._Visibility = val
        AnatomicalLabelsFactory.AnatomicalLabelsFactory.SetVisibility(
            self, val)

    def SetLabels(self, labels):
        self._Labels = labels

        for i, obj in zip(range(len(self._textObjects)), self._textObjects):
            obj.SetText(labels[i])

        self.Modified()
#        self.Render()

    def GetVisibility(self):
        """Gets the actor visibility

        Returns:
            int): 0 or 1.  1 indicates actor is visible.

        """
        return self._Visibility

    def ToggleVisibility(self):
        """switch actor from visible to invisible"""
        val = 1 - int(self.GetVisibility())
        self.SetVisibility(val)

    def SetPositiveColor(self, color):
        self._PositiveProperty.SetColor(color)

    def SetNegativeColor(self, color):
        self._NegativeProperty.SetColor(color)

    def _NewActor(self, label, point, scale, direction='positive'):
        # have to completely override ActorFactory._NewActor to create
        # a follower instead of an actor
        actor = ActorFactory.ActorFactory._NewActor(self)
        actor.PickableOff()
        if direction == 'positive':
            actor.SetProperty(self._PositiveProperty)
        else:
            actor.SetProperty(self._NegativeProperty)

        vectorText = vtk.vtkVectorText()
        vectorText.SetText(label)

        self._textObjects.append(vectorText)

        textMapper = vtk.vtkPolyDataMapper()
        textMapper.SetInputConnection(vectorText.GetOutputPort())

        actor.SetMapper(textMapper)
        actor.SetOrigin(0., 0., 0.)
        actor.SetPosition(point[0], point[1], point[2])
        actor.SetScale(scale)

        return actor

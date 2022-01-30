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

"""
SuperQuadricFactory - display SuperSqudric surfaces

Derived From:
   ActorFactory

"""

import vtk
from vtkAtamai import ActorFactory


class SuperquadricFactory(ActorFactory.ActorFactory):

    def __init__(self):
        ActorFactory.ActorFactory.__init__(self)

        squad = vtk.vtkSuperquadricSource()
        # buid ellipsoid for now
        squad.ToroidalOff()
        squad.SetPhiRoundness(1.0)
        squad.SetThetaRoundness(1.0)
        squad.SetPhiResolution(20)
        squad.SetThetaResolution(25)
        squad.SetSize(1)
        squad.SetCenter(0, 0, 0)
        # use scales to adjust the dimensions

        self._polyTrans = vtk.vtkTransformPolyDataFilter()
        self._polyTrans.SetInput(squad.GetOutput())
        self._polyTrans.SetTransform(vtk.vtkTransform())

        self._squad = squad
        del squad

        self._property = vtk.vtkProperty()

    def GetTransformedSquad(self):
        return self._polyTrans.GetOutput()

    def GetSquad(self):
        return self._squad

    def SetSize(self, size):
        self._squad.SetSize(size)
        self._squad.Update()

        self.Modified()

    def SetSquadTransform(self, matrix):
        self._polyTrans.GetTransform().SetMatrix(matrix)
        self.Modified()

    def SetScale(self, scale):
        """Scales in 3 dimensions:
        dims = scales * size
        """
        self._squad.SetScale(scale)
        self._squad.Update()

        self.Modified()

    def SetCenter(self, center):
        self._center = center
        self._squad.SetCenter(center)
        self._squad.Update()

        self.Modified()

    def SetOpacity(self, theOpacity):
        self._property.SetOpacity(theOpacity)

        self.Modified()

    def SetVisibility(self, renderer, yesno):
        for actor in self._ActorDict[renderer]:
            actor.SetVisibility(yesno)
        self.Modified()

    def SetColor(self, *args):
        apply(self._property.SetColor, args)
        self.Modified()

    def _MakeActors(self):
        actor = self._NewActor()
        actor.SetProperty(self._property)
        return [actor]

    def _NewActor(self):
        actor = ActorFactory.ActorFactory._NewActor(self)
        # actor.PickableOff()

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInput(self._polyTrans.GetOutput())
        actor.SetMapper(mapper)
        return actor

    def AddToRenderer(self, renderer):
        ActorFactory.ActorFactory.AddToRenderer(self, renderer)

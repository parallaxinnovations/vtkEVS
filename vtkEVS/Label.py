from vtkAtamai.Label import Label as oldLabel


class Label(oldLabel):

    """Enhanced Label Widget

    Adds Get/Set Opacity functions to modify background label opacity

    """

    def GetOpacity(self):
        for a in self._Actors:
            if a.GetMapper():
                if not a.GetMapper().IsA('vtkTextMapper'):
                    return a.GetProperty().GetOpacity()

    def SetOpacity(self, o):
        for a in self._Actors:
            if a.GetMapper():
                if not a.GetMapper().IsA('vtkTextMapper'):
                    a.GetProperty().SetOpacity(o)

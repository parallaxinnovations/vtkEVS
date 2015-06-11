from vtkAtamai import ConeMarkerFactory


class ConeMarkerFactory2(ConeMarkerFactory.ConeMarkerFactory):

    def SetSize(self, s):
        self._sz = s
        ConeMarkerFactory.ConeMarkerFactory.SetSize(self, s)

    def GetSize(self):
        return self._sz

    def HighlightOn(self):
        self._old = self._ConeMarkerFactory__property.GetColor()
        self.SetColor(1, 1, 0)
        self._old_size = self.GetSize()
        self.SetSize(self._old_size * 1.1)

    def HighlightOff(self):
        self.SetColor(self._old)
        self.SetSize(self._old_size)

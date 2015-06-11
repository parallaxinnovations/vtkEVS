#
# Simple class that defines the GE CUI colours
#


class CUIColours(object):

    def __init__(self):
        # default to hex
        self.HexadecimalOn()

    def HexadecimalOn(self):
        self.P1 = '#FFFFFF'
        self.P2 = '#F0F2F7'
        self.P3 = '#BABECC'
        self.P4 = '#868CA1'
        self.P5 = '#E4E7F1'
        self.P7 = '#BAC1DA'
        self.P8 = '#8D98BE'
        self.P9 = '#6875A3'
        self.P10 = '#2F3D6E'
        self.P11 = '#000000'
        self.P12 = '#FFFAE1'
        self.P13 = '#FFF1AB'
        self.Red = '#ED1C27'
        self.Yellow = '#FFE506'
        self.Green = '#00AB59'
        self.Orange = '#FF8D00'

    def RGB255On(self):
        self.P1 = (255, 255, 255)
        self.P2 = (240, 242, 247)
        self.P3 = (186, 190, 204)
        self.P4 = (134, 140, 161)
        self.P5 = (228, 231, 241)
        self.P7 = (186, 193, 218)
        self.P8 = (141, 152, 190)
        self.P9 = (104, 117, 163)
        self.P10 = (47, 61, 110)
        self.P11 = (0, 0, 0)
        self.P12 = (255, 250, 225)
        self.P13 = (225, 241, 171)
        self.Red = (237, 28, 39)
        self.Yellow = (255, 229, 6)
        self.Green = (0, 171, 89)
        self.Orange = (255, 141, 0)

    def NormalizedOn(self):
        self.P1 = (1.0, 1.0, 1.0)
        self.P2 = (240 / 255.0, 242 / 255.0, 247 / 255.0)
        self.P3 = (186 / 255.0, 190 / 255.0, 204 / 255.0)
        self.P4 = (134 / 255.0, 140 / 255.0, 161 / 255.0)
        self.P5 = (228 / 255.0, 231 / 255.0, 241 / 255.0)
        self.P7 = (186 / 255.0, 193 / 255.0, 218 / 255.0)
        self.P8 = (141 / 255.0, 152 / 255.0, 190 / 255.0)
        self.P9 = (104 / 255.0, 117 / 255.0, 163 / 255.0)
        self.P10 = (47 / 255.0, 61 / 255.0, 110 / 255.0)
        self.P11 = (0.0,  0.0, 0.0)
        self.P12 = (255 / 255.0, 250 / 255.0, 225 / 255.0)
        self.P13 = (225 / 255.0, 241 / 255.0, 171 / 255.0)
        self.Red = (237 / 255.0,  28 / 255.0,  39 / 255.0)
        self.Yellow = (255 / 255.0,  229 / 255.0,  6 / 255.0)
        self.Green = (0.0,  171 / 255.0,  89 / 255.0)
        self.Orange = (255 / 255.0,  141 / 255.0,  0.0)

from __future__ import division
#
# Simple class that defines the GE CUI colours
#


from builtins import object
from past.utils import old_div
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
        self.P2 = (old_div(240, 255.0), old_div(242, 255.0), old_div(247, 255.0))
        self.P3 = (old_div(186, 255.0), old_div(190, 255.0), old_div(204, 255.0))
        self.P4 = (old_div(134, 255.0), old_div(140, 255.0), old_div(161, 255.0))
        self.P5 = (old_div(228, 255.0), old_div(231, 255.0), old_div(241, 255.0))
        self.P7 = (old_div(186, 255.0), old_div(193, 255.0), old_div(218, 255.0))
        self.P8 = (old_div(141, 255.0), old_div(152, 255.0), old_div(190, 255.0))
        self.P9 = (old_div(104, 255.0), old_div(117, 255.0), old_div(163, 255.0))
        self.P10 = (old_div(47, 255.0), old_div(61, 255.0), old_div(110, 255.0))
        self.P11 = (0.0,  0.0, 0.0)
        self.P12 = (old_div(255, 255.0), old_div(250, 255.0), old_div(225, 255.0))
        self.P13 = (old_div(225, 255.0), old_div(241, 255.0), old_div(171, 255.0))
        self.Red = (old_div(237, 255.0),  old_div(28, 255.0),  old_div(39, 255.0))
        self.Yellow = (old_div(255, 255.0),  old_div(229, 255.0),  old_div(6, 255.0))
        self.Green = (0.0,  old_div(171, 255.0),  old_div(89, 255.0))
        self.Orange = (old_div(255, 255.0),  old_div(141, 255.0),  0.0)

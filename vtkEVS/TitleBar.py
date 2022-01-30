"""
A template to specific the title in the title bar of a window.

Methods:

  SetFileName(filename) - specify the file name

  GetFileName(filename) - get the file name

  SetTemplate(template) - specify the template for the title

  GetTemplate() - get the template for the title

  GetTitle() - get the title

"""

from builtins import object
import sys
import os


class TitleBar(object):

    def __init__(self):
        self._FileName = ""
        self._Template = "Parallax Innovations MicroView"

    def SetFileName(self, filename):
        self._FileName = filename

    def GetFileName(self):
        return self._FileName

    def SetTemplate(self, template):
        self._Template = template

    def GetTemplate(self):
        return self._Template

    def GetTitle(self):
        if (self._FileName == ""):
            if (self._Template.find("%s") == -1):
                return self._Template
            else:
                return (self._Template.replace("%s", ""))
        else:
            return (self._Template % self._FileName)

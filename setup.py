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

import sys
import os

# don't use distribute on Mac and Windows platforms
if sys.platform.startswith('linux'):
    from setuptools import setup
else:
    from distutils.core import setup

desc = """
  vtkEVS is an open source collection of Python/VTK classes which form
  part of the basic set of classes necessary to run MicroView.

  More information about MicroView can be found at
  http://www.sourceforge.net/projects/microview
"""

setup(name="vtkEVS",
      version="2.5.0",
      description="EVS VTK/Python visualization classes",
      long_description=desc,
      author="Jeremy Gill",
      author_email="jgill@parallax-innovations.com",
      maintainer="Jeremy Gill",
      maintainer_email="jgill@parallax-innovations.com",
      url="http://microview.sourceforge.net/vtkEVS",
      packages=['vtkEVS'],
      requires=['vtkAtamai'],
      license="MIT")

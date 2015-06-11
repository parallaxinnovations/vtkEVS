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

"""
EVSFileDialog - A simple file dialog interface, based on the default wx dialogs.

  EVSFileDialog extends on the built-in file dialogs by adding the ability to remember the current
  working directory between consecutive calls.

Global Functions:

  askdirectory(*options*) -- Prompt the user for a directory name
  askopenfilename(*options*) -- Prompt for a filename to read from
  asksaveasfilename(*options*) -- Prompt for a filename to write to

See Also:

  wx.FileDialog
"""

import logging
import wx
import collections

# this code should be retired soon


def convert_to_wx(_filter, default_extension):

    wildcard = ''
    idx = 0
    filter_index = 0

    # Add an "All known filetypes" entry at the beginning if it isn't already
    # there
    if 'All known filetypes' not in _filter:
        all_extensions = []
        for description in _filter:
            if description != 'All files':
                all_extensions.extend(_filter[description])
        _new_filter = collections.OrderedDict()
        _new_filter['All known filetypes'] = all_extensions
        for entry in _filter:
            _new_filter[entry] = _filter[entry]
        _filter = _new_filter

    if 'All files' not in _filter:
        _filter['All files'] = ['*']

    for e in _filter:
        found = False
        extensions = _filter[e][0]
        if default_extension == extensions:
            found = True
        for additional_extension in _filter[e][1:]:
            extensions += ';%s' % additional_extension
            if default_extension == additional_extension:
                found = True
        if e == 'All known filetypes':
            wildcard += '%s|%s|' % (e, extensions)
        else:
            wildcard += '%s (%s)|%s|' % (e, extensions, extensions)
            if found:
                filter_index = idx
        idx += 1

    wildcard = wildcard[:-1]

    return wildcard, filter_index


def askdirectory(**options):
    """Wrapper function that calls tkFileDialog.askdirectory()"""

    dlg = wx.DirDialog(-1, defaultPath=options['defaultdir'])
    if dlg.ShowModal() == wx.ID_OK:
        return dlg.GetPath()
    else:
        return None


def askopenfilename(**options):
    """Prompts the user for a filename to open"""

    if 'defaultdir' in options:
        defaultdir = options['defaultdir']
    else:
        defaultdir = '.'

    if 'message' in options:
        message = options['message']
    else:
        message = ''

    # for backward compatible reasons, we may be passed a bare list
    if not isinstance(options['filetypes'], collections.OrderedDict):
        options['filetypes'] = collections.OrderedDict(options['filetypes'])

    wildcard, filter_index = convert_to_wx(options['filetypes'], None)

    dlg = wx.FileDialog(wx.GetApp().GetTopWindow(), message=message, defaultDir=defaultdir, wildcard=wildcard,
                        style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_CHANGE_DIR)

    if dlg.ShowModal() == wx.ID_OK:
        return dlg.GetPath()
    else:
        return None


def asksaveasfilename(**options):
    """Prompts the user for a filename to save to."""

    if not 'filetypes' in options:
        logging.error("asksaveasfilename requires a 'filetypes' argument")
        return

    if not isinstance(options['filetypes'], collections.OrderedDict):
        logging.error(
            "asksaveasfilename filetypes must be of type OrderedDict!")
        return

    if 'defaultdir' in options:
        defaultdir = options['defaultdir']
    else:
        defaultdir = '.'
    if 'defaultextension' in options:
        default_extension = options['defaultextension']
    else:
        key = options['filetypes'].keys()[0]
        default_extension = options['filetypes'][key][0]
    if 'defaultfile' in options:
        defaultfile = options['defaultfile']
    else:
        defaultfile = ''

    if 'message' in options:
        message = options['message']
    else:
        message = ''

    wildcard, filter_index = convert_to_wx(
        options['filetypes'], default_extension)

    dlg = wx.FileDialog(
        wx.GetApp().GetTopWindow(), message=message, defaultDir=defaultdir,
        defaultFile=defaultfile,
        wildcard=wildcard,
        style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT | wx.FD_CHANGE_DIR)

    dlg.SetFilterIndex(filter_index)

    if dlg.ShowModal() == wx.ID_OK:
        return dlg.GetPath()
    else:
        return None

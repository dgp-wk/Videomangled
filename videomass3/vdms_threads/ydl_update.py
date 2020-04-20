# -*- coding: UTF-8 -*-

#########################################################
# Name: ydl_update.py
# Porpose: update tasks
# Compatibility: Python3, wxPython4 Phoenix
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2020 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: April.06.2020 *PEP8 compatible*
#########################################################
# This file is part of Videomass.

#    Videomass is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    Videomass is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with Videomass.  If not, see <http://www.gnu.org/licenses/>.

#########################################################
import subprocess
import shutil
import ssl
import urllib.request
import wx
from pubsub import pub
from threading import Thread


class CheckNewRelease(Thread):
    """
    Read the latest version of youtube-dl on github (see url) .
    """
    def __init__(self, url):
        """
        """
        Thread.__init__(self)
        """initialize"""
        self.url = url
        self.data = None

        self.start()  # start the thread (va in self.run())
    # ----------------------------------------------------------------#

    def run(self):
        """
        Check for new version release
        """
        try:
            req = (urllib.request.build_opener().open(
                   self.url).read().decode('utf-8').strip())
            self.data = req, None

        except urllib.error.HTTPError as error:
            self.data = None, error

        except urllib.error.URLError as error:
            self.data = None, error

        wx.CallAfter(pub.sendMessage,
                     "RESULT_EVT",
                     status=''
                     )
# -------------------------------------------------------------------------#


class Command_Execution(Thread):
    """
    Executes commands from the youtube-dl executable by subprocess
    class, e.g. read the installed version or update the downloaded
    sources.
    """
    def __init__(self, OS, cmd):
        """
        self.cmd is a list object
        self.data content output of the self.status
        self.status is a tuple object with exit status of the process
        """
        Thread.__init__(self)
        """initialize"""
        self.OS = OS
        self.cmd = cmd
        self.data = None
        self.status = None

        self.start()  # start the thread (va in self.run())
    # ----------------------------------------------------------------#

    def run(self):
        """
        """
        if self.OS == 'Windows':
            cmd = " ".join(self.cmd)
            info = subprocess.STARTUPINFO()
            info.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        else:
            cmd = self.cmd
            info = None

        try:
            p = subprocess.Popen(cmd,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT,
                                 universal_newlines=True,  # mod text
                                 startupinfo=info,
                                 )
            out = p.communicate()

        except OSError as oserr:  # executable do not exist
            self.status = ('%s' % oserr, 'error')
        else:
            if p.returncode:  # if returncode == 1
                self.status = (out[0], 'error')
            else:
                self.status = (out[0], out[1])

        self.data = self.status

        wx.CallAfter(pub.sendMessage,
                     "RESULT_EVT",
                     status=''
                     )
# ---------------------------------------------------------------------#


class Upgrade_Latest(Thread):
    """
    Download latest version of youtube-dl.exe, see self.url .
    """
    def __init__(self, latest, dest):
        """
        latest is the latest version getted by CheckNewRelease(Thread)
        self.dest is the location pathname to download

        """
        Thread.__init__(self)
        """initialize"""
        self.url = ('https://github.com/ytdl-org/youtube-dl/releases/'
                    'download/%s/youtube-dl.exe' % latest)
        self.dest = dest
        self.data = None
        self.status = None

        self.start()  # start the thread (va in self.run())
    # ----------------------------------------------------------------#

    def run(self):
        """
        Check for new version release
        """
        context = ssl._create_unverified_context()
        try:
            with urllib.request.urlopen(self.url, context=context) as \
                response, open(self.dest, 'wb') as out_file:
                shutil.copyfileobj(response, out_file)

            self.status = self.url, None

        except urllib.error.HTTPError as error:
            self.status = None, error

        except urllib.error.URLError as error:
            self.status = None, error

        self.data = self.status

        wx.CallAfter(pub.sendMessage,
                     "RESULT_EVT",
                     status=''
                     )
# -------------------------------------------------------------------------#
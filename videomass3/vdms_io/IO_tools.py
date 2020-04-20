# -*- coding: UTF-8 -*-

#########################################################
# Name: IO_tools.py
# Porpose: Redirect some input/output resources to process
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

import wx
import os
from videomass3.vdms_threads.ffplay_reproduction import Play
from videomass3.vdms_threads.ffprobe_parser import FFProbe
from videomass3.vdms_threads.volumedetect import VolumeDetectThread
from videomass3.vdms_threads.check_bin import ff_conf
from videomass3.vdms_threads.check_bin import ff_formats
from videomass3.vdms_threads.check_bin import ff_codecs
from videomass3.vdms_threads.check_bin import ff_topics
from videomass3.vdms_threads.opendir import browse
from videomass3.vdms_threads.ydl_extract_info import Extract_Info
from videomass3.vdms_threads.ydl_executable import GetFormatCode_Executable
from videomass3.vdms_threads import ydl_update
from videomass3.vdms_frames import ffmpeg_conf
from videomass3.vdms_frames import ffmpeg_formats
from videomass3.vdms_frames import ffmpeg_codecs
from videomass3.vdms_dialogs.popup import PopupDialog

get = wx.GetApp()
OS = get.OS
DIRconf = get.DIRconf
ffprobe_url = get.ffprobe_url
ffmpeg_url = get.ffmpeg_url
ffplay_url = get.ffplay_url


def stream_info(title, filepath):
    """
    Show media information of the streams content.
    This function make a bit control of file existance.
    """
    try:
        with open(filepath):
            miniframe = Mediainfo(title,
                                  filepath,
                                  ffprobe_url,
                                  OS,
                                  )
            miniframe.Show()

    except IOError:
        wx.MessageBox(_("File does not exist or not a valid file:  %s") % (
            filepath), "Videomass: warning", wx.ICON_EXCLAMATION, None)
# -----------------------------------------------------------------------#


def stream_play(filepath, timeseq, param):
    """
    Thread for media reproduction with ffplay
    """
    try:
        with open(filepath):
            thread = Play(filepath, timeseq, param)
            # thread.join() > attende fine thread, se no ritorna subito
            # error = thread.data
    except IOError:
        wx.MessageBox(_("File does not exist or not a valid file:  %s") % (
            filepath), "Videomass: warning", wx.ICON_EXCLAMATION, None)
        return
# -----------------------------------------------------------------------#


def probeInfo(filename):
    """
    Get data stream informations during dragNdrop action.
    It is called by MyListCtrl(wx.ListCtrl) only.
    Return tuple object with two items: (data, None) or (None, error).
    """
    metadata = FFProbe(ffprobe_url, filename, parse=False, writer='json')

    if metadata.ERROR():  # first execute a control for errors:
        err = metadata.error
        print("[FFprobe] Error:  %s" % err)
        return (None, err)

    data = metadata.custom_output()

    return (data, None)
# -------------------------------------------------------------------------#


def volumeDetectProcess(filelist, time_seq, audiomap):
    """
    Run thread to get audio peak level data and show a
    pop-up dialog with message.
    """
    thread = VolumeDetectThread(time_seq, filelist, audiomap, OS)
    loadDlg = PopupDialog(None,
                          _("Videomass - Loading..."),
                          _("\nWait....\nAudio peak analysis.\n"))
    loadDlg.ShowModal()
    # thread.join()
    data = thread.data
    loadDlg.Destroy()

    return data
# -------------------------------------------------------------------------#


def test_conf():
    """
    Call *check_bin.ffmpeg_conf* to get data to test the building
    configurations of the installed or imported FFmpeg executable
    and send it to dialog box.

    """
    out = ff_conf(ffmpeg_url, OS)
    if 'Not found' in out[0]:
        wx.MessageBox("\n{0}".format(out[1]),
                      "Videomass: error",
                      wx.ICON_ERROR,
                      None)
        return
    else:
        miniframe = ffmpeg_conf.Checkconf(out,
                                         ffmpeg_url,
                                         ffprobe_url,
                                         ffplay_url,
                                         OS,
                                         )
        miniframe.Show()
# -------------------------------------------------------------------------#


def test_formats():
    """
    Call *check_bin.ff_formats* to get available formats by
    imported FFmpeg executable and send it to dialog box.

    """
    diction = ff_formats(ffmpeg_url, OS)
    if 'Not found' in diction.keys():
        wx.MessageBox("\n{0}".format(diction['Not found']),
                      "Videomass: error",
                      wx.ICON_ERROR,
                      None)
        return
    else:
        miniframe = ffmpeg_formats.FFmpeg_formats(diction, OS)
        miniframe.Show()
# -------------------------------------------------------------------------#


def test_codecs(type_opt):
    """
    Call *check_bin.ff_codecs* to get available encoders
    and decoders by FFmpeg executable and send it to
    corresponding dialog box.

    """
    diction = ff_codecs(ffmpeg_url, type_opt, OS)
    if 'Not found' in diction.keys():
        wx.MessageBox("\n{0}".format(diction['Not found']),
                      "Videomass: error",
                      wx.ICON_ERROR,
                      None)
        return
    else:
        miniframe = ffmpeg_codecs.FFmpeg_Codecs(diction, OS, type_opt)
        miniframe.Show()
# -------------------------------------------------------------------------#


def findtopic(topic):
    """
    Call * check_bin.ff_topic * to run the ffmpeg command to search
    a certain topic. The ffmpeg_url is given by ffmpeg-search dialog.

    """
    retcod = ff_topics(ffmpeg_url, topic, OS)

    if 'Not found' in retcod[0]:
        s = ("\n{0}".format(retcod[1]))
        return(s)
    else:
        return(retcod[1])
# -------------------------------------------------------------------------#


def openpath(where):
    """
    Call vdms_threads.opendir.browse to open file browser into
    configuration directory or log directory.

    """
    pathname = os.path.join(DIRconf, where)
    if not os.path.exists(pathname):
        wx.MessageBox(_("Output log has not been created yet."),
                      "Videomass",
                      wx.ICON_INFORMATION, None)
        return
    ret = browse(OS, pathname)
    if ret:
        wx.MessageBox(ret, 'Videomass Error', wx.ICON_ERROR, None)
# -------------------------------------------------------------------------#


def youtube_info(url):
    """
    Call the thread to get extract info data object with
    youtube_dl python package and show a wait pop-up dialog .
    youtube_dl module.
    example without pop-up dialog:
    thread = Extract_Info(url)
    thread.join()
    data = thread.data
    yield data
    """
    thread = Extract_Info(url)
    loadDlg = PopupDialog(None,
                          _("Videomass - Loading..."),
                          _("\nWait....\nRetrieving required data.\n"))
    loadDlg.ShowModal()
    # thread.join()
    data = thread.data
    loadDlg.Destroy()
    yield data
# --------------------------------------------------------------------------#


def youtube_getformatcode_exec(url):
    """
    Call the thread to get format code data object with youtube-dl
    executable, (e.g. `youtube-dl -F url`) .
    While waiting, a pop-up dialog is shown.
    """
    thread = GetFormatCode_Executable(url)
    loadDlg = PopupDialog(None,
                          _("Videomass - Loading..."),
                          _("\nWait....\nRetrieving required data.\n"))
    loadDlg.ShowModal()
    # thread.join()
    data = thread.data
    loadDlg.Destroy()
    yield data


# --------------------------------------------------------------------------#

def youtubedl_latest(thisvers, url):
    """
    Call the thread to read the latest version of youtube-dl via the web.
    While waiting, a pop-up dialog is shown.
    """
    thread = ydl_update.CheckNewRelease(url)

    loadDlg = PopupDialog(None, _("Videomass - Loading..."),
                          _("\nWait....\nCheck for update.\n"))
    loadDlg.ShowModal()
    # thread.join()
    latest = thread.data
    loadDlg.Destroy()

    return latest
# --------------------------------------------------------------------------#


def youtubedl_update(cmd, waitmsg):
    """
    Call thread to execute generic tasks as updates youtube-dl executable
    or read the installed version. All these tasks are intended only for
    the local copy (not installed by the package manager) of youtube-dl.
    While waiting, a pop-up dialog is shown.
    """
    thread = ydl_update.Command_Execution(OS, cmd)

    loadDlg = PopupDialog(None, _("Videomass - Loading..."),
                          _("\nWait....\n%s\n" % waitmsg))
    loadDlg.ShowModal()
    # thread.join()
    update = thread.data
    loadDlg.Destroy()

    return update
# --------------------------------------------------------------------------#

def youtubedl_upgrade(latest):
    """
    Run thread to download the latest version of youtube-dl if not
    installed on Ms Windows.
    While waiting, a pop-up dialog is shown.
    """
    dest = os.path.join(DIRconf, 'youtube-dl.exe')
    thread = ydl_update.Upgrade_Latest(latest, dest)

    loadDlg = PopupDialog(None, _("Videomass - Loading..."),
                          _("\nWait....\nDownloading youtube-dl.\n"))
    loadDlg.ShowModal()
    # thread.join()
    status = thread.data
    loadDlg.Destroy()

    return status
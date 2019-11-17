# -*- coding: UTF-8 -*-

#########################################################
# Name: long_processing_task.py 
# Porpose: Console to show logging messages during processing
# Compatibility: Python3, wxPython4 Phoenix
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2019 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: Nov 17 2019
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

from __future__ import unicode_literals
import wx
from pubsub import pub
from videomass3.vdms_IO.make_filelog import write_log
from videomass3.vdms_PROCESS.ydl_download import YoutubeDL_Downloader
from videomass3.vdms_PROCESS.one_pass_process import OnePass
from videomass3.vdms_PROCESS.two_pass_process import TwoPass

# get videomass wx.App attribute
get = wx.GetApp()
OS = get.OS
DIRconf = get.DIRconf # path to the configuration directory:

########################################################################

class Logging_Console(wx.Panel):
    """
    displays a text control for the output logging, a progress bar 
    and a progressive percentage text label. This panel is used 
    in combination with separated threads for long processing tasks.
    It also implements the buttons to stop the current process and 
    close the panel during final activities.
    
    """
    def __init__(self, parent):
        """
        In the 'previous' attribute is stored an ID string used to
        recover the previous panel from which the process is started.
        The 'logname' attribute is the name_of_panel.log file in which 
        log messages will be written
        
        """
        self.parent = parent # main frame
        self.PARENT_THREAD = None # the instantiated thread
        self.ABORT = False # if True set to abort
        self.ERROR = False
        self.previus = None # stores the panel from which it starts
        self.countmax = None # the multiple task number
        self.count = None # initial setting of the counter
        self.logname = None # example: Videomass_VideoConversion.log
        self.duration = None # total duration or partial if set timeseq
        self.time_seq = None # a time segment
        self.varargs = None # tuple data
        
        wx.Panel.__init__(self, parent=parent)
        """ Constructor """

        lbl = wx.StaticText(self, label=_("Log View Console:"))
        self.OutText = wx.TextCtrl(self, wx.ID_ANY, "",
                                   style = wx.TE_MULTILINE | 
                                   wx.TE_READONLY | 
                                   wx.TE_RICH2
                                    )
        self.ckbx_text = wx.CheckBox(self, wx.ID_ANY,(_("Suppress excess "
                                                        "output")))
        self.barProg = wx.Gauge(self, wx.ID_ANY, range = 0)
        self.labPerc = wx.StaticText(self, label="Percentage: 0%")
        self.button_stop = wx.Button(self, wx.ID_STOP, _("Abort"))
        self.button_close = wx.Button(self, wx.ID_CLOSE, "")
        sizer = wx.BoxSizer(wx.VERTICAL)
        grid = wx.GridSizer(1, 2, 5, 5)
        sizer.Add(lbl, 0, wx.ALL, 5)
        sizer.Add(self.OutText, 1, wx.EXPAND|wx.ALL, 5)
        sizer.Add(self.ckbx_text, 0, wx.ALL, 5)
        sizer.Add(self.labPerc, 0, wx.ALL| wx.ALIGN_CENTER_VERTICAL, 5 )
        sizer.Add(self.barProg, 0, wx.EXPAND|wx.ALL, 5 )
        sizer.Add(grid, flag=wx.ALIGN_RIGHT|wx.RIGHT, border=5)
        grid.Add(self.button_stop, 0, wx.ALL, 5)
        grid.Add(self.button_close, 1, wx.ALL, 5)
        # set_properties:
        if OS == 'Darwin':
            self.OutText.SetFont(wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL))
        else:
            self.OutText.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL))

        self.ckbx_text.SetToolTip(_('If activated, hides some '
                                    'output messages.'))
        self.button_stop.SetToolTip(_("Stops current process"))
        self.SetSizerAndFit(sizer)

        # bind
        self.Bind(wx.EVT_BUTTON, self.on_stop, self.button_stop)
        self.Bind(wx.EVT_BUTTON, self.on_close, self.button_close)
        
        #------------------------------------------
        self.button_stop.Enable(True)
        self.button_close.Enable(False)
        
        pub.subscribe(self.update_download, "UPDATE_DOWNLOAD_EVT")
        pub.subscribe(self.update_display, "UPDATE_EVT")
        pub.subscribe(self.update_count, "COUNT_EVT")
        pub.subscribe(self.end_proc, "END_EVT")

    #-------------------------------------------------------------------#
    def topic_thread(self, panel, varargs, duration):
        """
        Thread redirection
        """
        self.previus = panel # stores the panel from which it starts
        self.countmax = varargs[9]# the multiple task number
        self.count = 0 # initial setting of the counter
        self.logname = varargs[8] # example: Videomass_VideoConversion.log
        self.duration = duration # total duration or partial if set timeseq
        self.time_seq = self.parent.time_seq # a time segment
        self.varargs = varargs # tuple data
        
        write_log(self.logname, "%s/log" % DIRconf) # set initial file LOG
        
        if self.varargs[0] == 'common':# from Audio/Video Conv.
            self.PARENT_THREAD = OnePass(self.varargs, self.duration,
                                         self.logname, self.time_seq,
                                         ) 
        elif self.varargs[0] == 'doublepass': # from Video Conv.
            self.PARENT_THREAD = TwoPass(self.varargs, self.duration,
                                         self.logname, self.time_seq
                                         )
        elif self.varargs[0] == 'EBU normalization': # from Audio/Video Conv.
            TwoPass_Loudnorm(self.varargs, self.duration, 
                             self.logname, self.time_seq
                            )
        elif self.varargs[0] == 'downloader':
            self.ckbx_text.Hide()
            self.PARENT_THREAD = YoutubeDL_Downloader(self.varargs,
                                                      self.logname)
            
        if not self.varargs[0] == 'downloader':
            self.ckbx_text.Show()
                             
    #-------------------------------------------------------------------#
    def update_download(self, output, duration, status):
        """
        Receive youtube-dl output message from 
        pubsub "UPDATE_DOWNLOAD_EVT".
        
        """
        if status == 'ERROR': 
            self.OutText.SetDefaultStyle(wx.TextAttr(wx.Colour(200,183,47)))
            self.OutText.AppendText('%s\n' % output)
            self.OutText.SetDefaultStyle(wx.TextAttr(wx.NullColour))
            
            self.OutText.SetDefaultStyle(wx.TextAttr(wx.Colour(210, 24, 20)))
            self.OutText.AppendText(_(' ...Failed\n'))
            self.OutText.SetDefaultStyle(wx.TextAttr(wx.NullColour))
            
        elif status == 'WARNING':
            self.OutText.SetDefaultStyle(wx.TextAttr(wx.Colour(200,183,47)))
            self.OutText.AppendText('%s\n' % output)
            self.OutText.SetDefaultStyle(wx.TextAttr(wx.NullColour))
            
        elif status == 'DEBUG':
            if '[download] Destination' in output:
                self.OutText.SetDefaultStyle(wx.TextAttr(wx.Colour(200,183,47)))
                self.OutText.AppendText('%s\n' % output)
                self.OutText.SetDefaultStyle(wx.TextAttr(wx.NullColour))
                
            elif not '[download]' in output:
                self.OutText.SetDefaultStyle(wx.TextAttr(wx.Colour(200,183,47)))
                self.OutText.AppendText('%s\n' % output)
                self.OutText.SetDefaultStyle(wx.TextAttr(wx.NullColour))

        elif status == 'DOWNLOAD': 
            self.labPerc.SetLabel("%s" % duration[0])
            self.barProg.SetValue(duration[1])
            
        elif status == 'FINISHED':
            self.OutText.SetDefaultStyle(wx.TextAttr(wx.Colour(200,183,47)))
            self.OutText.AppendText('%s\n' % duration)
            self.OutText.SetDefaultStyle(wx.TextAttr(wx.NullColour))

    #---------------------------------------------------------------------#
    def update_display(self, output, duration, status):
        """
        Receive message from thread of the second loops process
        by wxCallafter and pubsub UPDATE_EVT.
        The received 'output' is parsed for calculate the bar 
        progress value, percentage label and errors management.
        This method can be used even for non-loop threads.
        
        NOTE: During conversion the ffmpeg errors do not stop all 
              others tasks, if an error occurred it will be marked 
              with 'failed' but continue; if it has finished without 
              errors it will be marked with 'completed' on update_count
              method. Since not all ffmpeg messages are errors, sometimes 
              it happens to see more output marked with yellow color. 
              
        This strategy consists first of capturing all the output and 
        marking it in yellow, then in capturing the error if present, 
        but exiting immediately after the function.
        
        """
        #if self.ckbx_text.IsChecked(): # ffmpeg output messages in real time:
            #self.OutText.AppendText(output)
            
        if not status == 0:# error, exit status of the p.wait
            self.OutText.SetDefaultStyle(wx.TextAttr(wx.Colour(210, 24, 20)))
            self.OutText.AppendText(_(' ...Failed\n'))
            self.OutText.SetDefaultStyle(wx.TextAttr(wx.NullColour))
            return # must be return here
            
        if 'time=' in output:# ...in processing
            i = output.index('time=')+5
            pos = output[i:i+8].split(':')
            hours, minutes, seconds = pos[0],pos[1],pos[2]
            timesum = (int(hours)*60 + int(minutes))*60 + int(seconds)
            self.barProg.SetValue(timesum)
            percentage = timesum / duration * 100
            self.labPerc.SetLabel("Percentage: %s%%" % str(int(percentage)))
            del output, duration

        else:# append all others lines on the textctrl and log file
            if not self.ckbx_text.IsChecked():# not print the output
                self.OutText.SetDefaultStyle(wx.TextAttr(wx.Colour(200,183,47)))
                self.OutText.AppendText(' %s' % output)
                self.OutText.SetDefaultStyle(wx.TextAttr(wx.NullColour))
                
            with open("%s/log/%s" %(DIRconf, self.logname),"a") as logerr:
                logerr.write("[FFMPEG]: %s" % (output))
                # write a row error into file log
            
    #-------------------------------------------------------------------#
    def update_count(self, count, duration, fname, end):
        """
        Receive message from first 'for' loop in the thread process.
        This method can be used even for non-loop threads.
        
        """
        if end == 'ok':
            self.OutText.SetDefaultStyle(wx.TextAttr(wx.Colour(30, 164, 30)))
            self.OutText.AppendText(_(' ...Completed\n'))
            self.OutText.SetDefaultStyle(wx.TextAttr(wx.NullColour))
            return
            
        #if STATUS_ERROR == 1:
        if end == 'error':
            self.OutText.SetDefaultStyle(wx.TextAttr(wx.Colour(200, 183, 47)))
            self.OutText.AppendText('\n  %s\n' % (count))
            self.OutText.SetDefaultStyle(wx.TextAttr(wx.NullColour))
            self.ERROR = True
            #self.labPerc.SetLabel("Percentage: 0%")
        else:
            self.barProg.SetRange(duration)#set la durata complessiva
            self.barProg.SetValue(0)# resetto la prog bar
            self.labPerc.SetLabel("Percentage: 100%")
            self.OutText.AppendText('\n  %s : "%s"\n' % (count,fname))
    #-------------------------------------------------------------------#
    
    def on_stop(self, event):
        """
        The user change idea and was stop process
        """
        self.PARENT_THREAD.stop()
        self.PARENT_THREAD.join()
        self.ABORT = True
        
        event.Skip()
    #-------------------------------------------------------------------#
    def on_close(self, event):
        """
        close dialog and retrieve at previusly panel
        
        """
        if not self.PARENT_THREAD == None:
            return
        # reset all before close
        self.button_stop.Enable(True)
        self.button_close.Enable(False)
        self.PARENT_THREAD = None
        self.ABORT = False
        self.ERROR = False
        self.OutText.Clear()
        self.parent.panelShown(self.previus)# retrieve at previusly panel
        #event.Skip()
    #-------------------------------------------------------------------#
    def end_proc(self):
        """
        At the end of the process
        """
        if self.ERROR == True:
            self.OutText.SetDefaultStyle(wx.TextAttr(wx.Colour(210, 24, 20)))
            self.OutText.AppendText(_('\n Sorry, tasks failed !\n'))
            self.OutText.SetDefaultStyle(wx.TextAttr(wx.NullColour))

        elif self.ABORT == True:
            self.OutText.SetDefaultStyle(wx.TextAttr(wx.Colour(164, 30, 164)))
            self.OutText.AppendText(_('\n Interrupted Process !\n'))
            self.OutText.SetDefaultStyle(wx.TextAttr(wx.NullColour))

        else:
            self.OutText.SetDefaultStyle(wx.TextAttr(wx.Colour(30, 62, 164)))
            self.OutText.AppendText(_('\n All finished !\n'))
            self.OutText.SetDefaultStyle(wx.TextAttr(wx.NullColour))
            self.labPerc.SetLabel("Percentage: 100%")
            self.barProg.SetValue(0)
        
        self.button_stop.Enable(False)
        self.button_close.Enable(True)
        self.PARENT_THREAD = None

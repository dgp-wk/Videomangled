# -*- coding: UTF-8 -*-
"""
Name: video_to_sequence.py
Porpose: A simple images extractor UI
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyright: (c) 2018/2022 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Mar.31.2022
Code checker:
    flake8: --ignore F821, W504
    pylint: --ignore E0602, E1101
########################################################

This file is part of Videomass.

   Videomass is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   Videomass is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with Videomass.  If not, see <http://www.gnu.org/licenses/>.
"""
import os
import wx
import wx.lib.agw.hyperlink as hpl
import wx.lib.agw.floatspin as FS
import wx.lib.scrolledpanel as scrolled
from videomass.vdms_io.checkup import check_files
from videomass.vdms_dialogs.epilogue import Formula
from videomass.vdms_utils.utils import make_newdir_with_id


class VideoToSequence(wx.Panel):
    """
    A simple UI for extracting frames from videos,
    with a special automation for output files and
    abilities of customization.
    """
    MSG_1 = _("\n1. Import one or more video files, then select one."
              "\n\n2. To select a slice of time use the Timeline editor "
              "(CTRL+T) by scrolling the DURATION and the SEEK sliders."
              "\n\n3. Set the FPS (frames per second) control; the "
              "higher this value, the more images will be extracted."
              "\n\n4. Select an output format (jpg, png, bmp)."
              "\n\n5. Start the conversion."
              "\n\n\nThe images produced will be saved in a folder "
              "named 'Video-to-Frames' with a progressive digit, "
              "\nin the path you specify.")
    # ----------------------------------------------------------------#

    def __init__(self, parent):
        """
        This is a panel impemented on MainFrame
        """
        get = wx.GetApp()
        appdata = get.appset
        self.parent = parent  # parent is the MainFrame

        wx.Panel.__init__(self, parent=parent, style=wx.BORDER_THEME)
        sizer = wx.BoxSizer(wx.VERTICAL)
        panelscroll = scrolled.ScrolledPanel(self, -1, size=(-1, 200),
                                             style=wx.TAB_TRAVERSAL
                                             | wx.BORDER_THEME,
                                             name="panelscr",
                                             )
        fgs1 = wx.BoxSizer(wx.VERTICAL)
        lbl_help = wx.StaticText(panelscroll, wx.ID_ANY,
                                 label=VideoToSequence.MSG_1
                                 )
        fgs1.Add(lbl_help, 0, wx.ALL | wx.EXPAND, 5)
        sizer_link1 = wx.BoxSizer(wx.HORIZONTAL)
        fgs1.Add(sizer_link1)
        lbl_msg1 = wx.StaticText(panelscroll, wx.ID_ANY,
                                 label=_("For more information, "
                                         "visit the official FFmpeg "
                                         "documentation:")
                                 )
        link1 = hpl.HyperLinkCtrl(panelscroll, -1, "4.19 image2",
                                  URL="https://ffmpeg.org/ffmpeg-"
                                      "formats.html#image2-2"
                                  )
        link2 = hpl.HyperLinkCtrl(panelscroll, -1, ("3.3 FFmpeg FAQ"),
                                  URL="https://ffmpeg.org/faq.html#How-do-I-"
                                      "encode-movie-to-single-pictures_003f"
                                  )
        link3 = hpl.HyperLinkCtrl(panelscroll, -1, ("FFmpeg Wiki"),
                                  URL="https://trac.ffmpeg.org/wiki/Create%"
                                      "20a%20thumbnail%20image%20every"
                                      "%20X%20seconds%20of%20the%20video"
                                  )
        sizer_link1.Add(lbl_msg1, 0, wx.ALL | wx.EXPAND, 5)
        sizer_link1.Add(link1)
        sizer_link1.Add((20, 20))
        sizer_link1.Add(link2)
        sizer_link1.Add((20, 20))
        sizer_link1.Add(link3)
        sizer_link2 = wx.BoxSizer(wx.HORIZONTAL)
        fgs1.Add(sizer_link2)
        lbl_msg2 = wx.StaticText(panelscroll, wx.ID_ANY,
                                 label=_("Other unofficial resources:")
                                 )
        link4 = hpl.HyperLinkCtrl(panelscroll, -1, ("Help Tile filter"),
                                  URL="http://underpop.online.fr/f/ffmpeg"
                                      "/help/tile.htm.gz"
                                  )
        link5 = hpl.HyperLinkCtrl(panelscroll, -1, ("High quality gif"),
                                  URL="http://blog.pkh.me/p/21-high-quality-"
                                      "gif-with-ffmpeg.html"
                                  )
        sizer_link2.Add(lbl_msg2, 0, wx.ALL | wx.EXPAND, 5)
        sizer_link2.Add(link4)
        sizer_link2.Add((20, 20))
        sizer_link2.Add(link5)
        sizer.Add(panelscroll, 0, wx.ALL | wx.EXPAND, 0)
        panelscroll.SetSizer(fgs1)
        panelscroll.SetAutoLayout(1)
        panelscroll.SetupScrolling()
        line1 = wx.StaticLine(self, wx.ID_ANY, pos=wx.DefaultPosition,
                              size=wx.DefaultSize, style=wx.LI_HORIZONTAL,
                              name=wx.StaticLineNameStr
                              )
        sizer.Add(line1, 0, wx.ALL | wx.EXPAND, 5)
        # sizer.Add((20, 20))
        choices = [(_('From movie to pictures')),
                   (_('From movie to picture sheet (tiles)')),
                   (_('From movie to animated GIF')),
                   ]
        self.rdbx_opt = wx.RadioBox(self, wx.ID_ANY, (_("Options")),
                                    choices=choices,
                                    majorDimension=1,
                                    style=wx.RA_SPECIFY_ROWS,
                                    )
        sizer.Add(self.rdbx_opt, 0, wx.ALL | wx.EXPAND, 5)
        self.rdbx_opt.SetSelection(0)
        boxctrl = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY), wx.VERTICAL)
        sizer.Add(boxctrl, 0, wx.ALL | wx.EXPAND, 5)
        sizFormat = wx.BoxSizer(wx.HORIZONTAL)
        boxctrl.Add(sizFormat)
        siz_ctrl = wx.BoxSizer(wx.HORIZONTAL)
        boxctrl.Add(siz_ctrl)
        self.lbl_rate = wx.StaticText(self, wx.ID_ANY, label="FPS:")
        siz_ctrl.Add(self.lbl_rate, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
        self.spin_rate = FS.FloatSpin(self, wx.ID_ANY,
                                      min_val=0.1, max_val=30.0,
                                      increment=0.1, value=0.2,
                                      agwStyle=FS.FS_LEFT, size=(120, -1)
                                      )
        self.spin_rate.SetFormat("%f"), self.spin_rate.SetDigits(1)
        siz_ctrl.Add(self.spin_rate, 0, wx.ALL, 5)
        self.lbl_frmt = wx.StaticText(self, wx.ID_ANY,
                                      label=_("Output format:")
                                      )
        siz_ctrl.Add(self.lbl_frmt, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
        self.cmb_frmt = wx.ComboBox(self, wx.ID_ANY,
                                    choices=['jpeg', 'png', 'bmp', 'gif'],
                                    size=(160, -1), style=wx.CB_DROPDOWN |
                                    wx.CB_READONLY)
        siz_ctrl.Add(self.cmb_frmt, 0, wx.ALL, 5)
        self.cmb_frmt.SetSelection(2)

        siz_addparams = wx.BoxSizer(wx.HORIZONTAL)
        boxctrl.Add(siz_addparams, 0, wx.EXPAND, 0)

        self.ckbx_edit = wx.CheckBox(self, wx.ID_ANY, _('Edit'))
        siz_addparams.Add(self.ckbx_edit, 0, wx.ALL | wx.EXPAND, 5)
        self.txt_args = wx.TextCtrl(self, wx.ID_ANY, size=(700, -1),)
        siz_addparams.Add(self.txt_args, 1, wx.ALL | wx.EXPAND, 5)
        self.txt_args.Disable()

        self.SetSizer(sizer)

        if appdata['ostype'] == 'Darwin':
            lbl_help.SetFont(wx.Font(11, wx.SWISS, wx.NORMAL, wx.BOLD))
            lbl_msg1.SetFont(wx.Font(11, wx.SWISS, wx.NORMAL, wx.NORMAL))
            lbl_msg2.SetFont(wx.Font(11, wx.SWISS, wx.NORMAL, wx.NORMAL))
        else:
            lbl_help.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD))
            lbl_msg1.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))
            lbl_msg2.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))

        tip = (_('Set FPS control from 0.1 to 30.0 fps, default is 0.2 fps'))
        self.spin_rate.SetToolTip(tip)

        self.Bind(wx.EVT_CHECKBOX, self.on_edit, self.ckbx_edit)
        self.Bind(wx.EVT_RADIOBOX, self.on_options, self.rdbx_opt)
    # ---------------------------------------------------------

    def on_edit(self, event):
        """
        edit in place with additional paramemeters
        """
        if self.ckbx_edit.IsChecked():
            self.spin_rate.Disable()
            self.cmb_frmt.Disable()
            self.lbl_rate.Disable()
            self.lbl_frmt.Disable()
            self.txt_args.Enable()
            arg = self.update_arguments(self.cmb_frmt.GetValue())
            self.txt_args.write(arg[1])
        else:
            if self.rdbx_opt.GetSelection() == 0:
                self.spin_rate.Enable()
                self.lbl_rate.Enable()
            if self.rdbx_opt.GetSelection() in (0, 1):
                self.cmb_frmt.Enable()
                self.lbl_frmt.Enable()
            self.txt_args.Clear()
            self.txt_args.Disable()
    # ---------------------------------------------------------

    def on_options(self, event):
        """
        Available user options
        """
        if self.rdbx_opt.GetSelection() == 0:
            self.cmb_frmt.SetSelection(2)
            self.txt_args.Clear()
            self.on_edit(self)

        elif self.rdbx_opt.GetSelection() == 1:
            self.cmb_frmt.SetSelection(1)
            self.txt_args.Clear()
            self.lbl_rate.Disable()
            self.spin_rate.Disable()
            self.on_edit(self)

        elif self.rdbx_opt.GetSelection() == 2:
            self.cmb_frmt.SetSelection(3)
            self.cmb_frmt.Disable()
            self.txt_args.Clear()
            self.lbl_rate.Disable()
            self.spin_rate.Disable()
            self.on_edit(self)
    # ---------------------------------------------------------

    def update_arguments(self, fmt):
        """
        Given a image format return the corresponding
        ffmpeg argument
        """
        if self.rdbx_opt.GetSelection() == 1:
            cmd = ('-skip_frame nokey', '-vf "scale=128:72,tile=8x8:'
                   'padding=2:margin=2:color=White" -an -vsync 0')

        elif self.rdbx_opt.GetSelection() == 2:
            cmd = ('', '-vf "fps=10,scale=320:-1:flags=lanczos,split=2 '
                   '[a][b]; [a] palettegen [pal]; [b] fifo [b]; [b] '
                   '[pal] paletteuse" -loop 0')

        elif self.rdbx_opt.GetSelection() == 0:
            arg = {'jpeg': ('', f'-vsync cfr -r {self.spin_rate.GetValue()} '
                            f'-pix_fmt yuvj420p'),
                   'png': ('', f'-vsync cfr -r {self.spin_rate.GetValue()} '
                           f'-pix_fmt rgb24'),
                   'bmp': ('', f'-vsync cfr -r {self.spin_rate.GetValue()} '
                           f'-pix_fmt bgr24'),
                   'gif': ('', f'-vsync cfr -r {self.spin_rate.GetValue()}')
                   }
            cmd = arg[fmt]
        return cmd
    # ---------------------------------------------------------

    def on_start(self):
        """
        Check before Builds FFmpeg command arguments
        """
        fsource = self.parent.file_src
        if len(fsource) == 1:
            clicked = fsource[0]

        elif not self.parent.filedropselected:
            wx.MessageBox(_("A target file must be selected in the "
                            "queued files"),
                          'Videomass', wx.ICON_INFORMATION, self)
            return
        else:
            clicked = self.parent.filedropselected

        typemedia = self.parent.fileDnDTarget.flCtrl.GetItemText(
                                                     fsource.index(clicked), 3)
        if 'video' not in typemedia or 'sequence' in typemedia:
            wx.MessageBox(_("Invalid file: '{}'").format(clicked),
                          _('ERROR'), wx.ICON_ERROR, self)
            return

        checking = check_files((clicked,),
                               self.parent.outpath_ffmpeg,
                               self.parent.same_destin,
                               self.parent.suffix,
                               self.cmb_frmt.GetValue()
                               )
        if checking is None:  # User changing idea or not such files exist
            return

        self.build_command(clicked, checking[1])
    # -----------------------------------------------------------

    def build_command(self, filename, destdir):
        """
        Save as files image the selected video input. The saved
        images are named as file name + a progressive number + .jpg
        and placed in a folder with the same file name + a progressive
        number in the chosen output path.

        """
        basename = os.path.basename(filename.rsplit('.')[0])
        destdir = destdir[0]  # specified dest
        outputdir = make_newdir_with_id(destdir, 'Video-to-Frames_1')
        if self.cmb_frmt.GetValue() == 'gif':
            fileout = "{0}.{1}".format(basename, self.cmb_frmt.GetValue())
        else:
            fileout = "{0}-%d.{1}".format(basename, self.cmb_frmt.GetValue())
        outfilename = os.path.join(outputdir, fileout)

        if self.txt_args.IsEnabled():
            arg = self.update_arguments(self.cmb_frmt.GetValue())
            preargs = arg[0]
            command = " ".join(f'{self.txt_args.GetValue()} -y '
                               f'"{outfilename}"'.split())
        else:
            arg = self.update_arguments(self.cmb_frmt.GetValue())
            preargs = arg[0]
            command = " ".join(f'{arg[1]} {self.txt_args.GetValue()} -y '
                               f'"{outfilename}"'.split())

        valupdate = self.update_dict(filename, outputdir)
        ending = Formula(self, valupdate[0], valupdate[1], _('Starts'))

        if ending.ShowModal() == wx.ID_OK:
            self.parent.switch_to_processing('video_to_sequence',
                                             filename,
                                             preargs,
                                             outputdir,
                                             command,
                                             None,
                                             None,
                                             None,
                                             'from_movie_to_pictures.log',
                                             1,
                                             False,  # reserved
                                             )
    # -----------------------------------------------------------

    def update_dict(self, filename, outputdir):
        """
        Update information before send to epilogue

        """
        if self.parent.time_seq == "-ss 00:00:00.000 -t 00:00:00.000":
            time = _('Unset')
        else:
            t = self.parent.time_seq.split()
            time = _('start  {} | duration  {}').format(t[1], t[3])

        if self.txt_args.IsEnabled():
            args = _('Enabled')
            rate = ''
        else:
            rate = self.spin_rate.GetValue()
            args = _('Disabled')

        formula = (_("SUMMARY\n\nSelected File\nOutput Format\nRate (fps)\n"
                     "Custom Arguments\nTime Period\nDestination Folder"))
        dictions = (f"\n\n{filename}\n{self.cmb_frmt.GetValue()}"
                    f"\n{rate}\n{args}\n{time}\n{outputdir}"
                    )
        return formula, dictions

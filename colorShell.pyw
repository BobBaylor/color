#! /usr/bin/env python

#----------------------------------------------------------------------
# A simple dual image viewer
#----------------------------------------------------------------------

import os
import wx
import color
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import  wx.lib.filebrowsebutton as filebrowse
wide = 860

class MyPanel(wx.Panel):
    def __init__(self, *args, **kwds):
        """Trying to implement your magic ``panel```"""
        wx.Panel.__init__(self, *args, **kwds)
        self.backColor = (200,200,200)
        """
        pnl = self
        szmain = wx.BoxSizer(wx.HORIZONTAL)
        szmain.Add(wx.TextCtrl(pnl, -1, 'Database path'), 1, wx.EXPAND)
        szmain.Add(wx.Button(pnl, -1, 'Database path'), 0, wx.EXPAND)
        pnl.SetSizer(szmain)
        # make a minimalist menu bar
        """
        # Use a sizer to layout the controls, stacked vertically and with
        # a 6 pixel border around each
        space = 6
        sflags = wx.ALL
        self.sizer = wx.BoxSizer( wx.VERTICAL )
        x = self
        text = wx.StaticText(x, -1, "Set the proportions and background color, then press Create")
        text.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))
        text.SetSize(text.GetBestSize())
        self.sizer.Add( text,                  0, sflags, space)
        # sizer.Add(self.panel, wx.EXPAND )
        # and a few controls
        self.sc = []

        for val,img in zip([20,20,20,20,20,20],color.gfNamelst):
            self.sc += [wx.SpinCtrl(self, -1, "", size=(50, 20))]
            self.sc[-1].SetRange(0,99)
            self.sc[-1].SetValue(val)
            hsizer1 = wx.BoxSizer( wx.HORIZONTAL )
            hsizer1.Add( self.sc[-1],        0, sflags, space)
            bmp = wx.Image(img)
            sbm = wx.StaticBitmap(self, wx.ID_ANY, wx.BitmapFromImage(bmp))
            hsizer1.Add(sbm, 0, sflags, space)
            self.sizer.Add( hsizer1,                0, sflags, space)


               # bind the button events to handlers
        hsizer2 = wx.BoxSizer( wx.HORIZONTAL )
        colorbtn = wx.Button(self, -1, "Pick Background Color", (50,50))
        self.Bind(wx.EVT_BUTTON, self.OnColorButton, colorbtn)
        hsizer2.Add( colorbtn,                0, sflags, space)
        # add a text box for the background color
        self.txtColorBk = wx.TextCtrl(self, -1, "220,220,220", size=(125, -1))
        hsizer2.Add( self.txtColorBk,                0, sflags, space)

        makebtn = wx.Button(x, -1, "Create")
        self.Bind(wx.EVT_BUTTON, self.OnMakeFile, makebtn)
        hsizer2.Add( makebtn,                0, sflags, space)
        self.sizer.Add( hsizer2,                0, sflags, space)

        # now set up the double image viewer
        text = wx.StaticText(x, -1, "Browse to the two images, and press View")
        text.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))
        text.SetSize(text.GetBestSize())
        self.sizer.Add( text,                  0, sflags, space)

        self.upperFileBtn = filebrowse.FileBrowseButton(x, -1, size=(wide-10, -1),
            changeCallback = self.fbbCallback, labelText='Upper',startDirectory=os.getcwd())
        self.upperFileBtn.SetValue( 'color_20_20_20_20_20_20.jpg')
        self.sizer.Add( self.upperFileBtn,        0, sflags, space)

        self.lowerFileBtn = filebrowse.FileBrowseButton(x, -1, size=(wide-10, -1),
            changeCallback = self.fbbCallback, labelText='Lower',startDirectory=os.getcwd())
        self.lowerFileBtn.SetValue( 'color_25_20_15_30_00_20.jpg')
        self.sizer.Add( self.lowerFileBtn,        0, sflags, space)
               # bind the button events to handlers
        funbtn = wx.Button(x, -1, "View")
        self.Bind(wx.EVT_BUTTON, self.OnFunButton, funbtn)
        self.sizer.Add( funbtn,                0, sflags, space)

        self.SetSizer(self.sizer)
        clrBg = tuple([int(v.strip()) for v in self.txtColorBk.GetValue().split(',')])     # get a triplette of the background color
        self.SetBackgroundColour(clrBg)
        self.Refresh()



    def OnColorButton(self, evt):
        dlg = wx.ColourDialog(self)
        dlg.GetColourData().SetChooseFull(True)

        if dlg.ShowModal() == wx.ID_OK:

            # If the user selected OK, then the dialog's wx.ColourData will
            # contain valid information. Fetch the data ...
            data = dlg.GetColourData()

            # ... then do something with it. The actual colour data will be
            # returned as a three-tuple (r, g, b) in this particular case.
            self.backColor = data.GetColour().Get()
            # print 'You selected: %s\n' % str(data.GetColour().Get())
            self.SetBackgroundColour(self.backColor)
            self.txtColorBk.SetValue('%d,%d,%d'%self.backColor)
            self.Refresh()
        # Once the dialog is destroyed, Mr. wx.ColourData is no longer your
        # friend. Don't use it again!
        dlg.Destroy()


    def OnTimeToClose(self, evt):
        """Event handler for the button click."""
        # print "See ya later!"
        self.Close()

    def OnFunButton(self, evt):
        """Event handler for the button click."""
        self.SetStatusText( 'working...')
        imgs = [Image.open(self.upperFileBtn.GetValue()),Image.open(self.lowerFileBtn.GetValue()),]
        imgWidMax = 1
        for im in imgs:
            if  imgWidMax < im.size[0]:
                imgWidMax = im.size[0]

        margin = 50
        imout = Image.new('RGB',(imgWidMax+2*margin,imgs[0].size[1]+imgs[0].size[1]+3*margin))
        row = margin
        for im in imgs:
            imout.paste(im,(margin,row,margin+im.size[0],row+im.size[1]))
            row += im.size[1]+margin
        imout.show()


    def fbbCallback(self, evt):
        # print('FileBrowseButton: %s\n' % evt.GetString())
        pass

    def outDirRootButtonCallback(self, evt):
        # print('outDirButton: %s\n' % evt.GetString())
        pass

    def OnMakeFile(self,evt):
        opts = {'--background': '200,200,200',
            '--help': False,
            '--length': '0.4',
            '--position': '2,2',
            '--show': 'True',
            '--test': False,
            '--version': False,
            '--weights': '20,20,20,20,20,20'}
        opts['--background'] = self.txtColorBk.GetValue()
        opts['--weights'] = ','.join(['%d'%x.GetValue() for x in self.sc])
        # print opts['--background']
        # print opts['--weights']
        color.genGlass(opts)


    def SetStatusText(self, evt):
        # print('outDirButton: %s\n' % evt.GetString())
        pass



class MyFrame(wx.Frame):
    """
    This is MyFrame.  It just shows a few controls on a wxPanel,
    and has a simple menu.

    Use this file upperFileBtn
    Use this file lowerFileBtn
    Write this root name TextEntry
    and starting number TextEntry
    To here outDirRootButton
    Optional subdirectory TextEntry
    Move the input file there, too CheckBox
    """
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, wx.ID_ANY, title,
                          pos=(150, 150), size=(wide, 700), style=wx.DEFAULT_FRAME_STYLE)
        self.panel = MyPanel(self)

        self.CreateStatusBar()
        menuBar = wx.MenuBar()
        menu1 = wx.Menu()
        menu1.Append(101,'&Close','Close this frame')
        self.SetMenuBar( menuBar )
        self.Bind(wx.EVT_MENU, self.Close, id=101)



class MyApp(wx.App):
    def OnInit(self):
        frame = MyFrame(None, "colorShell.pyw Glass Viewer")
        self.SetTopWindow(frame)
        frame.Show(True)
        return True

# app = MyApp(redirect=True)
app = MyApp()
app.MainLoop()


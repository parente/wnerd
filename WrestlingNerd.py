'''
Start up script for Wrestling Nerd.
'''

import wx
from wnUI import wnFrame
import WrestlingNerd_wdr as GUI

if __name__ == '__main__':
  # create the frame
  app = wx.PySimpleApp(0)
  frame = wnFrame()
  frame.Centre()
  app.SetTopWindow(frame)
  frame.Show()
  
  # show the splash screen
  splash = wx.SplashScreen(GUI.LogoBitmaps(0), wx.SPLASH_CENTRE_ON_SCREEN|wx.SPLASH_TIMEOUT, 
                           3000, frame, -1)

  # start the application
  app.MainLoop()
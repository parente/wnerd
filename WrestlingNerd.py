'''
Start up script for Wrestling Nerd.
'''

from wxPython.wx import *
from wnUI import wnFrame
import WrestlingNerd_wdr as GUI
import warnings

if __name__ == '__main__':
  # turn off deprecation warnings
  warnings.filterwarnings('ignore')

  # create the frame
  app = wxPySimpleApp(0)
  frame = wnFrame()
  frame.Centre()
  app.SetTopWindow(frame)
  frame.Show()
  
  # show the splash screen
  splash = wxSplashScreen(GUI.LogoBitmaps(0), wxSPLASH_CENTRE_ON_SCREEN | wxSPLASH_TIMEOUT,
                          3000, frame, -1)

  # start the application    
  app.MainLoop()
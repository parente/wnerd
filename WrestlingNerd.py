'''
Start up script for Wrestling Nerd.
'''

from wxPython.wx import *
from wnUI import wnFrame
import warnings

if __name__ == '__main__':
  # turn off deprecation warnings
  warnings.filterwarnings('ignore')

  # start the application
  app = wxPySimpleApp(1)
  frame = wnFrame()
  frame.Centre()
  app.SetTopWindow(frame)
  frame.Show()
  app.MainLoop()
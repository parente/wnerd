from wxPython.wx import *
from wnUI import wnFrame

if __name__ == '__main__':
  app = wxPySimpleApp(0)
  frame = wnFrame()
  frame.Centre()
  app.SetTopWindow(frame)
  frame.Show()  
  app.MainLoop()
from wxPython.wx import *

class wnRenderer(object):
  pass
  
class wnPainter(wnRenderer):
  def __init__(self, canvas):
    self.canvas = canvas
    self.dc = None
    
  def SetDC(self, dc):
    self.dc = dc
    
  def DrawLine(self, x1, y1, x2, y2):
    if self.dc is None: return
    self.dc.DrawLine(x1, y1, x2, y2)
  
  def DrawText(self, pt, handler):
    wxStaticText(self.canvas, -1, 'Entry', point=wxPoint(pt[0], pt[1]), size=wxSize(100,20))
      
class wnPrinter(wnRenderer):
  pass
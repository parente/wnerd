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
  
  def DrawText(self, text, x, y):
    if self.dc is None: return
    self.dc.SetFont(wxSWISS_FONT)
    self.dc.DrawText(text, x, y)
   
  def DrawTextInput(self, text, handler, x, y):
    pass
    #wxStaticText(self.canvas, -1, 'Entry', point=wxPoint(pt[0], pt[1]), size=wxSize(100,20))
      
class wnPrinter(wnRenderer):
  pass
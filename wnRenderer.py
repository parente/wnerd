class wnRenderer(object):
  pass
  
class wnPainter(wnRenderer):
  def __init__(self, canvas):
    self.canvas = canvas
    self.dc = None
    
  def SetDC(self, dc):
    self.dc = dc
    
  def DrawLine(self, pt1, pt2):
    if self.dc is None: return
    
    self.dc.DrawLine(pt1[0], pt1[1], pt2[0], pt2[1])
  
  def CreateTextBox(self, pt, handler):
    wxStaticText(self.canvas, -1, 'Entry', point=wxPoint(pt[0], pt[1]), size=wxSize(100,20))
  
class wnPrinter(wnRenderer):
  pass
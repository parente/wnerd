from wxPython.wx import *

class wnRenderer(object):
  pass
  
class wnPainter(wnRenderer):
  def __init__(self, canvas):
    self.canvas = canvas
    self.dc = None
    self.controls = {}
    
  def SetDC(self, dc):
    self.dc = dc
    
  def DrawLine(self, x1, y1, x2, y2):
    if self.dc is None: return
    self.dc.DrawLine(x1, y1, x2, y2)
  
  def DrawText(self, text, x, y):
    if self.dc is None: return
    self.dc.SetFont(wxSWISS_FONT)
    self.dc.DrawText(text, x, y)
    
  def DrawStaticTextControl(self, text, x, y, length, id, handler):
    '''Draw a static text control. Create it if it doesn't exist. Register the new event handler
    to receive events from the user.'''
    
    #check to see if a static text control already exists for this round and entry
    if not self.controls.has_key(id):
      ctrl = wxStaticText(self.canvas, -1, text, pos=wxPoint(x, y), size=wxSize(length,20))
      ctrl.SetBackgroundColour(wxWHITE)
      self.controls[id] = ctrl
   
  def DrawDynamicTextControl(self, text, x, y, id, handler):
    pass
      
class wnPrinter(wnRenderer):
  pass
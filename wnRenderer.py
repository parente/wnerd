from wxPython.wx import *
from wnEvents import *
from wnControls import *

class wnRenderer(object):
  pass
  
class wnPainter(wnRenderer):
  def __init__(self, canvas):
    self.canvas = canvas
    self.dc = None
    self.controls = {}
    self.event_man = wnEventManager(self)
    
  def __del__(self):
    for ctrl in self.controls.values():
      ctrl.Destroy()
    del self.event_man
       
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
    
    #check to see if a static text control already exists for this entry
    if not self.controls.has_key(id):
      #make a panel at the given location so that all events can be received
      #panel = wxPanel(self.canvas, -1, pos=wxPoint(x, y), size=wxSize(length,20),
      #                style=wxTRANSPARENT_WINDOW)
      #
      ##now make the actual static text control
      #ctrl = wxStaticText(panel, -1, text, size=wxSize(length,20),
      #                    style=wxST_NO_AUTORESIZE|wxALIGN_LEFT)
      ctrl = wnStaticTextWithEvents(self.canvas, -1, text, pos=wxPoint(x,y),
                                    size=wxSize(length, 18))
      ctrl.SetBackgroundColour(wxWHITE)
      self.controls[id] = ctrl
      
      #hook the event manager properly
      self.event_man.RegisterMouseEvents(ctrl, handler)
      
    #if it already exists
    else:
      ctrl = self.controls[id]
      #hook the event manager
      self.event_man.RegisterMouseEvents(ctrl, handler)
      #set the current text
      ctrl.SetLabel(text)
   
  def DrawDynamicTextControl(self, text, x, y, length, id, handler):
    pass
      
class wnPrinter(wnRenderer):
  pass
'''
The renderer module defines classes that render tournament info to the screen and printer. These
objects are used to do all rendering operations.
'''
from wxPython.wx import *
from wnEvents import *
from wnControls import *

class wnRenderer(object):
  pass
  
class wnPainter(wnRenderer):
  def __init__(self, canvas, team_scores):
    self.canvas = canvas
    self.team_scores = team_scores
    
    self.dc = None

    self.controls = {}
    self.event_man = wnEventManager(self)
    
  def __del__(self):
    '''Clean out any stored controls and registered events.'''
    for ctrl in self.controls.values():
      ctrl.Destroy()
    del self.event_man
    
  def ResetControls(self):
    '''Clean out any stored controls and registered events.'''
    for ctrl in self.controls.values():
      ctrl.Destroy()
    self.controls = {}
    del self.event_man
    self.event_man = wnEventManager(self)
      
  def SetDC(self, dc):
    self.dc = dc
    
  def DrawLine(self, x1, y1, x2, y2):
    if self.dc is None: return
    self.dc.DrawLine(x1, y1, x2, y2)
  
  def DrawText(self, text, x, y):
    if self.dc is None: return
    self.dc.SetFont(wxSWISS_FONT)
    self.dc.DrawText(text, x, y)
    
  def DrawStaticTextControl(self, text, x, y, length, height, id, handler):
    '''Draw a static text control. Create it if it doesn't exist. Register the new event handler
    to receive events from the user.'''
    
    #check to see if a static text control already exists for this entry
    if not self.controls.has_key(id):
      ctrl = wnStaticTextWithEvents(self.canvas, -1, text, pos=wxPoint(x,y),
                                    size=wxSize(length, height))
      self.controls[id] = ctrl
      
      #hook the event manager properly
      self.event_man.RegisterMouseEvents(ctrl)
      self.event_man.RegisterEventHandler(ctrl.GetId(), handler)
      
    #if it already exists
    else:
      ctrl = self.controls[id]
      #hook the event manager
      self.event_man.RegisterEventHandler(ctrl.GetId(), handler)
      #set the current text
      ctrl.SetLabel(text)
   
  def DrawDynamicTextControl(self, text, x, y, length, height, id, handler):
    '''Draw a dynamic text control that let's the user enter text directly into it. Register the new
    event handler to receive events from the user.'''
    
    #check to see if a static text control already exists for this entry
    if not self.controls.has_key(id):
      ctrl = wxTextCtrl(self.canvas, -1, text, pos=wxPoint(x,y), size=wxSize(length, height),
                        style = wxTE_PROCESS_ENTER|wxTE_PROCESS_TAB)
      self.controls[id] = ctrl
      
      #hook the event manager properly
      self.event_man.RegisterFocusEvents(ctrl)
      self.event_man.RegisterEventHandler(ctrl.GetId(), handler)
      
    #if it already exists
    else:
      ctrl = self.controls[id]
      #hook the event manager
      self.event_man.RegisterEventHandler(ctrl.GetId(), handler)
      #set the current text
      ctrl.SetValue(text)
      
  def DrawTeamScores(self, items):
    self.team_scores.DeleteAllItems()
    for i in range(len(items)):
      name, score = items[i]
      self.team_scores.InsertStringItem(i, name)
      self.team_scores.SetStringItem(i, 1, str(score))

  def SetKeyboardFocus(self, id):
    '''Set the focus to the control associated with the given ID.'''
    try:
      ctrl = self.controls[id]
    except:
      return
    
    ctrl.SetFocus()

class wnPrinter(wnRenderer):
  pass
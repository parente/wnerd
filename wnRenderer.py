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
  def __init__(self, frame, canvas, team_scores):
    self.frame = frame
    self.canvas = canvas
    self.team_scores = team_scores
    self.control_cache = {}
    
    self.initial_id = None
    
    self.dc = None

    self.controls = {}
    self.event_man = wnEventManager(self)
    
  def __del__(self):
    '''Clean out any stored controls and registered events.'''
    for ctrl in self.controls.values():
      ctrl.Destroy()
    del self.event_man
    del self.control_cache
    
  def ResetControls(self):
    '''Clean out any stored controls and registered events.'''
    for ctrl in self.controls.values():
      ctrl.Destroy()
    self.controls = {}
    self.control_cache = {}
    del self.event_man
    self.event_man = wnEventManager(self)
      
  def SetDC(self, dc):
    if dc is not None:
      dc.BeginDrawing()
    else:
      self.dc.EndDrawing()
    self.dc = dc
   
  def SetInitialFocus(self):
    self.SetFocus(self.initial_id)
   
  def SetFocus(self, id):
    '''Give the focus to the control associated with the given ID if possible.'''
    try:
      self.controls[id].SetFocus()
    except:
      pass
    
  def GetFocus(self):
    ctrl = wxWindow_FindFocus()
    reverse = dict([(v,k) for k,v in self.controls.items()])
    return reverse.get(ctrl)
    
  def DrawLine(self, x1, y1, x2, y2):
    if self.dc is None: return
    self.dc.DrawLine(x1, y1, x2, y2)
  
  def DrawText(self, text, x, y):
    if self.dc is None: return
    self.dc.SetFont(wxSWISS_FONT)
    self.dc.DrawText(text, x, y)
    
  def DrawMatchTextControl(self, text, x, y, length, height, id, handler):
    '''Draw a static text control. Create it if it doesn't exist. Register the new event handler
    to receive events from the user.'''
    
    #check to see if a static text control already exists for this entry
    if not self.controls.has_key(id):
      ctrl = wnStaticText(self.canvas, -1, text, pos=wxPoint(x,y), size=wxSize(length, height))
      self.controls[id] = ctrl
      
      #hook the event manager properly
      self.event_man.RegisterMouseEvents(ctrl)
      self.event_man.RegisterFocusEvents(ctrl)
      self.event_man.RegisterEventHandler(ctrl.GetId(), handler)
      
    #if it already exists
    else:
      ctrl = self.controls[id]
      #hook the event manager
      self.event_man.RegisterEventHandler(ctrl.GetId(), handler)
      #set the current text
      ctrl.SetLabel(text)
   
  def DrawSeedTextControl(self, text, x, y, length, height, choices, id, handler):
    '''Draw a dynamic text control that let's the user enter text directly into it. Register the new
    event handler to receive events from the user.'''
    
    #check to see if a dynamic text control already exists for this entry
    if not self.controls.has_key(id):
      #don't create the text control immediately, delay until later so they can be defined in the
      #proper tabbing order
      self.control_cache[id] = {'args' : (self.canvas, -1, text, choices, wxPoint(x,y),
                                          wxSize(length, height)), 'handler' : handler}
      
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
      
  def Flush(self):
    '''Complete any drawing operations that were cached to be completed later. This is needed so
    that the dynamic text controls are drawn in the right order for tabbing.'''
    if len(self.control_cache) == 0: return
    
    keys = self.control_cache.keys()
    keys.sort()

    #store the initial control so we can set the focus easily
    self.initial_id = keys[0]
    
    for id in keys:
      ctrl = apply(wnDynamicText, self.control_cache[id]['args'])
      self.controls[id] = ctrl
      
      #hook the event manager properly
      self.event_man.RegisterFocusEvents(ctrl)
      self.event_man.RegisterMouseEvents(ctrl)
      self.event_man.RegisterEventHandler(ctrl.GetId(), self.control_cache[id]['handler'])
      
    self.control_cache = {}
    
  def ShowMatchDialog(self, wrestlers, result):
    '''Show a dialog box that let's the user enter match results. Initialize the box to the values
    provided by the entry. Return the winner and result entered by the user.'''
    dlg = wnMatchDialog(self.frame, wrestlers, result)
    if dlg.ShowModal() == wxID_OK:
      winner = dlg.GetWinner()
      loser = dlg.GetLoser()
      result_type = dlg.GetResultType()
      dlg.Destroy()
      return winner, loser, result_type
    else:
      dlg.Destroy()
      return None
    
                             
class wnPrinter(wnRenderer):
  pass
'''
The renderer module defines classes that render tournament info to the screen and printer. These
objects are used to do all rendering operations.
'''
from wxPython.wx import *
from wnEvents import *
from wnControls import *
import wnSettings

class wnRenderer(object):
  def DrawLine(self, x1, y1, x2, y2):
    pass
  
  def DrawText(self, text, x, y):
    pass
  
  def DrawMatchTextControl(self, text, x, y, length, height, id, obj):
    pass
       
  def DrawSeedTextControl(self, text, x, y, length, height, choices, id, obj):
    pass
  
class wnPainter(wnRenderer):
  def __init__(self, frame, canvas):
    self.frame = frame
    self.canvas = canvas
    self.control_cache = {}
    
    self.initial_id = None
    
    self.dc = None

    self.controls = {}
    self.event_man = wnEventManager(self)

  def ResetControls(self):
    '''Clean out any stored controls and registered events.'''
    self.initial_id = None
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
    
  def DrawMatchTextControl(self, text, x, y, length, height, id, obj):
    '''Draw a static text control. Create it if it does not exist. Register the new event handler
    to receive events from the user.'''
    
    #check to see if a static text control already exists for this entry
    if not self.controls.has_key(id):
      ctrl = wnStaticText(self.canvas, -1, text, pos=wxPoint(x,y), size=wxSize(length, height))
      self.controls[id] = ctrl
      
      #hook the event manager properly
      self.event_man.RegisterMouseEvents(ctrl)
      #self.event_man.RegisterFocusEvents(ctrl)
      self.event_man.RegisterMatchMenuEvents(ctrl)
      self.event_man.RegisterEventHandler(ctrl.GetId(), obj)
      
    #if it already exists
    else:
      ctrl = self.controls[id]
      #hook the event manager
      self.event_man.RegisterEventHandler(ctrl.GetId(), obj)
      #set the current text
      ctrl.SetLabel(text)
   
  def DrawSeedTextControl(self, text, x, y, length, height, choices, id, obj):
    '''Draw a dynamic text control that let's the user enter text directly into it. Register the new
    event handler to receive events from the user.'''
    
    #check to see if a dynamic text control already exists for this entry
    if not self.controls.has_key(id):
      #don't create the text control immediately, delay until later so they can be defined in the
      #proper tabbing order
      self.control_cache[id] = {'args' : (self.canvas, -1, text, choices, wxPoint(x,y),
                                          wxSize(length, height)), 'handler' : obj}
      
    #if it already exists
    else:
      ctrl = self.controls[id]
      #hook the event manager
      self.event_man.RegisterEventHandler(ctrl.GetId(), obj)
      #set the current text
      ctrl.SetValue(text)
      
  #def DrawTeamScores(self, items):
  #  self.team_scores.DeleteAllItems()
  #  for i in range(len(items)):
  #    score, name = items[i]
  #    self.team_scores.InsertStringItem(i, name)
  #    self.team_scores.SetStringItem(i, 1, str(score))
      
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
      self.event_man.RegisterSeedMenuEvents(ctrl)
      self.event_man.RegisterEventHandler(ctrl.GetId(), self.control_cache[id]['handler'])
      
    self.control_cache = {}
    
  def ShowMatchDialog(self, wrestlers, result, is_scoring):
    '''Show a dialog box that lets the user enter match results. Initialize the box to the values
    provided by the entry. Return the winner and result entered by the user.'''
    dlg = wnMatchDialog(self.frame, wrestlers, result, is_scoring)
    dlg.CentreOnScreen()
    
    if dlg.ShowModal() == wxID_OK:
      winner = dlg.GetWinner()
      loser = dlg.GetLoser()
      result_type = dlg.GetResultType()
      result_value = dlg.GetResultValue()
      is_scoring = dlg.GetIsScoring()
      dlg.Destroy()
      return winner, loser, result_type, result_value, is_scoring
    else:
      dlg.Destroy()
      return None
    
                             
class wnPrinter(wnRenderer):
  def __init__(self):
    self.dc = None
    self.max_size = None
    self.scale = 1.0
  
  def SetDC(self, dc):
    self.dc = dc
    self.max_size = self.dc.GetSize()
        
  def ScaleToFit(self, max_w, max_h):
    if self.dc is None: return
    
    # store the size of the printout
    self.max_size = max_w, max_h
    
    # add the margin to the bracket size
    max_w += 2*wnSettings.print_margin_x
    max_h += 2*wnSettings.print_margin_y
    
    # scale the drawing area to fit the page
    pw, ph = self.dc.GetSize()
    sx = float(pw)/float(max_w)
    sy = float(ph)/float(max_h)
    self.scale = min(sx, sy)
    self.dc.SetDeviceOrigin(wnSettings.print_margin_x, wnSettings.print_margin_y)    
    self.dc.SetUserScale(self.scale, self.scale)
    
  def DrawHeader(self, *args):
    if self.dc is None: return
    
    h = 0
    for l in args:
      d = self.dc.GetTextExtent(l)
      self.DrawText(l, self.max_size[0]-d[0], h)
      h += d[1]
               
  def DrawLine(self, x1, y1, x2, y2):
    if self.dc is None: return
    self.dc.DrawLine(x1, y1, x2, y2)

  
  def DrawText(self, text, x, y):
    if self.dc is None: return
    self.dc.DrawText(text, x, y)
    
  def DrawMatchTextControl(self, text, x, y, length, height, id, obj):
    self.DrawText(text, x, y)
    if obj.Result is not None:
      self.DrawText(str(obj.Result), x, y+height)
       
  def DrawSeedTextControl(self, text, x, y, length, height, choices, id, obj):
    try:
      name, team = text.split('|')
    except:
      return
    
    text = name.strip() + '-' + team.strip()
    self.DrawText(text, x, y)
'''
The events module defines classes that help tournament objects receive events from the user.
'''

import wx
import WrestlingNerd_wdr as GUI

class wnEvent(object):
  def __init__(self, **kwargs):
    self.__dict__.update(kwargs)

class wnMouseEventReceivable:
  '''Defines an interface that must be implemented for an object to receive mouse events from the
  event manager.'''
  def OnLeftDown(self, event):
    pass
  
  def OnLeftUp(self, event):
    pass
  
  def OnRightDown(self, event):
    pass
  
  def OnRightUp(self, event):
    pass
  
  def OnLeftDoubleClick(self, event):
    pass
  
  def OnMouseEnter(self, event):
    pass

  def OnMouseLeave(self, event):
    pass
  

class wnFocusEventReceivable:
  '''Defines an interface that must be implemented for an object to receive mouse events from the
  event manager.'''
  def OnSetFocus(self, event):
    pass
  
  def OnKillFocus(self, event):
    pass
  
class wnSeedMenuReceivable:
  '''Defines an interface that must be implemented for an object to receive menu events from the
  seed popup menu.'''
  def OnDelete(self, event):
    pass
  
  def OnDeleteMoveUp(self, event):
    pass
  
  def OnInsertMoveDown(self, event):
    pass
  
  def OnSetLastSeed(self, event):
    pass
  
  def OnSwapUp(self, event):
    pass
  
  def OnSwapDown(self, event):
    pass
    
  def OnSwapTo(self, event):
    pass

class wnMatchMenuReceivable:
  '''Defines an interface that must be implemented for an object to receive menu events from the
  match popup menu.'''
  def OnMoveIn(self, event):
    pass

  def OnDelete(self, event):
    pass
  
  def OnDeleteAll(self, event):
    pass
  
class wnEventManager(wx.EvtHandler):
  def __init__(self, painter):
    wx.EvtHandler.__init__(self)
    self.painter = painter
    self.handlers = {}
    self.mouse_dispatch = {wx.EVT_LEFT_DOWN.evtType[0] : 'OnLeftDown',
                           wx.EVT_RIGHT_DOWN.evtType[0] : 'OnRightDown',
                           wx.EVT_LEFT_DCLICK.evtType[0] : 'OnLeftDoubleClick',
                           wx.EVT_ENTER_WINDOW.evtType[0] : 'OnMouseEnter',
                           wx.EVT_LEAVE_WINDOW.evtType[0] : 'OnMouseLeave',
                           wx.EVT_LEFT_UP.evtType[0] : 'OnLeftUp',
                           wx.EVT_RIGHT_UP.evtType[0] : 'OnRightUp'}

    self.focus_dispatch = {wx.EVT_SET_FOCUS.evtType[0] : 'OnSetFocus',
                           wx.EVT_KILL_FOCUS.evtType[0] : 'OnKillFocus'}
                           
    self.menu_dispatch = {GUI.ID_DELETE_SEED_MENU : 'OnDelete',
                          GUI.ID_DELETE_MATCH_MENU : 'OnDelete',
                          GUI.ID_DELETEALL_MATCH_MENU : 'OnDeleteAll', 
                          GUI.ID_DELETEMOVEUP_SEED_MENU : 'OnDeleteMoveUp',
                          GUI.ID_INSERTMOVEDOWN_SEED_MENU : 'OnInsertMoveDown',
                          GUI.ID_SETLAST_SEED_MENU : 'OnSetLastSeed',
                          GUI.ID_SWAPDOWN_SEED_MENU : 'OnSwapDown',
                          GUI.ID_SWAPUP_SEED_MENU : 'OnSwapUp', 
                          GUI.ID_MOVEIN_MATCH_MENU : 'OnMoveIn',
                          GUI.ID_SWAPTO_SEED_MENU : 'OnSwapTo'}

  def RegisterMouseEvents(self, ctrl):
    '''Begin watching for events on the given control.'''
    wx.EVT_LEFT_DOWN(ctrl, self.OnMouseEvent)
    wx.EVT_RIGHT_DOWN(ctrl, self.OnMouseEvent)
    wx.EVT_LEFT_UP(ctrl, self.OnMouseEvent)
    wx.EVT_RIGHT_UP(ctrl, self.OnMouseEvent)
    wx.EVT_LEFT_DCLICK(ctrl, self.OnMouseEvent)
    wx.EVT_ENTER_WINDOW(ctrl, self.OnMouseEvent)
    wx.EVT_LEAVE_WINDOW(ctrl, self.OnMouseEvent)
    
  def RegisterFocusEvents(self, ctrl):
    wx.EVT_SET_FOCUS(ctrl, self.OnFocusEvent)
    wx.EVT_KILL_FOCUS(ctrl, self.OnFocusEvent)
    
  def RegisterMatchMenuEvents(self, frame):
    wx.EVT_MENU(frame, GUI.ID_DELETE_MATCH_MENU, self.OnMenuEvent)
    wx.EVT_MENU(frame, GUI.ID_DELETEALL_MATCH_MENU, self.OnMenuEvent)
    wx.EVT_MENU(frame, GUI.ID_MOVEIN_MATCH_MENU, self.OnMenuEvent)
    
  def RegisterSeedMenuEvents(self, frame):
    wx.EVT_MENU(frame, GUI.ID_DELETE_SEED_MENU, self.OnMenuEvent)
    wx.EVT_MENU(frame, GUI.ID_DELETEMOVEUP_SEED_MENU, self.OnMenuEvent)
    wx.EVT_MENU(frame, GUI.ID_INSERTMOVEDOWN_SEED_MENU, self.OnMenuEvent)
    wx.EVT_MENU(frame, GUI.ID_SWAPUP_SEED_MENU, self.OnMenuEvent)
    wx.EVT_MENU(frame, GUI.ID_SWAPDOWN_SEED_MENU, self.OnMenuEvent)
    wx.EVT_MENU(frame, GUI.ID_SWAPTO_SEED_MENU, self.OnMenuEvent)
    wx.EVT_MENU(frame, GUI.ID_SETLAST_SEED_MENU, self.OnMenuEvent)
    
  def RegisterEventHandler(self, id, handler):
    '''Register an event handler to receive callbacks from user actions on the given control.'''    
    #reference the handler function by the ID of the control for which it handles events
    self.handlers[id] = handler
    
  def OnMouseEvent(self, event):
    '''Dispatch to the proper object and function based on the event object and event type.'''
    obj = event.GetEventObject()
    i = obj.GetId()
    handler = self.handlers.get(i)
    if handler is not None:
      e = wnEvent(Painter=self.painter, Position=event.GetPosition(), Control=obj)
      func_name = self.mouse_dispatch[event.GetEventType()]
      func = getattr(handler, func_name)
      func(e)
    event.Skip()
      
  def OnFocusEvent(self, event):
    '''Dispatch to the proper object and function based on the event object and event type.'''
    obj = event.GetEventObject()
    i = obj.GetId()
    handler = self.handlers.get(i)
    if handler is not None:
      e = wnEvent(Painter=self.painter, Control=obj)
      func_name = self.focus_dispatch[event.GetEventType()]
      func = getattr(handler, func_name)
      func(e)
    event.Skip()
    
  def OnMenuEvent(self, event):
    '''Dispatch to the proper object and function based on the event object id.'''
    obj = event.GetEventObject()
        
    # the object could be a menu or the control itself
    try:
      control = obj.Control
      i = obj.Control.GetId()
    except:
      control = obj
      i = obj.GetId()
      
    handler = self.handlers.get(i)
    if handler is not None:
      e = wnEvent(Painter=self.painter, Control=control)
      func_name = self.menu_dispatch[event.GetId()]
      func = getattr(handler, func_name)
      func(e)
    event.Skip()
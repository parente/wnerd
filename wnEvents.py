'''
The events module defines classes that help tournament objects receive events from the user.
'''

from wxPython.wx import *

class wnEvent(object):
  def __init__(self, **kwargs):
    self.__dict__.update(kwargs)

class wnMouseEventReceivable:
  '''Defines an interface that must be implemented for an object to receive mouse events from the
  event manager.'''
  def OnLeftClick(self, event):
    pass
  
  def OnRightClick(self, event):
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
  
class wnEventManager(wxEvtHandler):
  def __init__(self, painter):
    wxEvtHandler.__init__(self)
    self.painter = painter
    self.handlers = {}

  def RegisterMouseEvents(self, ctrl):
    '''Begin watching for events on the given control.'''
    EVT_LEFT_DOWN(ctrl, self.OnMouseEvent)
    EVT_RIGHT_DOWN(ctrl, self.OnMouseEvent)
    EVT_LEFT_DCLICK(ctrl, self.OnMouseEvent)
    EVT_ENTER_WINDOW(ctrl, self.OnMouseEvent)
    EVT_LEAVE_WINDOW(ctrl, self.OnMouseEvent)
    
  def RegisterFocusEvents(self, ctrl):
    EVT_SET_FOCUS(ctrl, self.OnFocusEvent)
    EVT_KILL_FOCUS(ctrl, self.OnFocusEvent)
    
  def RegisterTextEvents(self, ctrl):
    '''Begin watching for text events on the given control.'''
    pass
    
  def RegisterEventHandler(self, id, handler):
    '''Register an event handler to receive callbacks from user actions on the given control.'''    
    #reference the handler function by the ID of the control for which it handles events
    self.handlers[id] = handler
    
  def OnMouseEvent(self, event):
    '''Dispatch to the proper object and function based on the event object and event type.'''
    dispatch = {wxEVT_LEFT_DOWN : 'OnLeftClick', wxEVT_RIGHT_DOWN : 'OnRightClick',
                wxEVT_LEFT_DCLICK : 'OnLeftDoubleClick', wxEVT_ENTER_WINDOW : 'OnMouseEnter',
                wxEVT_LEAVE_WINDOW : 'OnMouseLeave'}

    obj = event.GetEventObject()
    i = obj.GetId()
    handler = self.handlers.get(i)
    if handler is not None:
      e = wnEvent(Painter=self.painter, Position=event.GetPosition(), Control=obj)
      func_name = dispatch[event.GetEventType()]
      func = getattr(handler, func_name)
      func(e)
    event.Skip()
      
  def OnFocusEvent(self, event):
    '''Dispatch to the proper object and function based on the event object and event type.'''
    dispatch = {wxEVT_SET_FOCUS : 'OnSetFocus', wxEVT_KILL_FOCUS : 'OnKillFocus'}
    
    obj = event.GetEventObject()
    i = obj.GetId()
    handler = self.handlers.get(i)
    if handler is not None:
      e = wnEvent(Painter=self.painter, Control=obj)
      func_name = dispatch[event.GetEventType()]
      func = getattr(handler, func_name)
      func(e)
    event.Skip()
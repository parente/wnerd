from wxPython.wx import *

class wnEvent(object):
  def __init__(self, painter, pos, ctrl):
    self.painter = painter
    self.pos = pos
    self.ctrl = ctrl
    
  def GetPainter(self):
    return self.painter
  
  def GetX(self):
    return self.pos[0]
  
  def GetY(self):
    return self.pos[1]
  
  def GetPosition(self):
    return self.pos
  
  def GetControl(self):
    return self.ctrl
  
  Painter = property(fget=GetPainter)
  X = property(fget=GetX)
  Y = property(fget=GetY)
  Position = property(fget=GetPosition)
  Control = property(fget=GetControl)

class wnEventReceivable:
  '''Defines an interface that must be implemented for an object to receive events from the event
  manager.'''
  def OnLeftClick(self, painter, x, y):
    pass
  
  def OnRightClick(self, painter, x, y):
    pass
  
  def OnLeftDoubleClick(self, painter, x, y):
    pass
  
  def OnMouseEnter(self, painter, x, y):
    pass
  
  def OnMouseLeave(self, painter, x, y):
    pass
  
class wnEventManager(wxEvtHandler):
  def __init__(self, painter):
    wxEvtHandler.__init__(self)
    self.painter = painter
    
  def RegisterMouseEvents(self, ctrl, handler):
    '''Register an event handler to receive callbacks from actions on the provided control.'''
    #EVT_LEFT_DOWN(ctrl, self.OnLeftClick)
    #EVT_RIGHT_DOWN(ctrl, self.OnRightClick)
    #EVT_LEFT_DCLICK(ctrl, self.OnLeftDoubleClick)
    EVT_ENTER_WINDOW(ctrl, self.OnMouseEnter)
    #EVT_LEAVE_WINDOW(ctrl, self.OnLeave)
    
  def OnMouseEnter(self, event):
    print 'mouse enter', event.GetEventObject()
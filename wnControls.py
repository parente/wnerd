from wxPython.wx import *
from wxPython.lib.maskededit import Field, wxMaskedTextCtrl
import wnSettings

class wnStaticText(wxPanel):
  def __init__(self, parent, id, text, pos=wxPoint(0,0), size=wxSize(100,20)):
    wxPanel.__init__(self, parent, id, pos, size, style=wxTRANSPARENT_WINDOW)
    
    self.parent = parent
    self.popup = None
    
    EVT_ENTER_WINDOW(self, self.OnMouseEnter)
    EVT_LEAVE_WINDOW(self, self.OnMouseLeave)

    #make the actual static text control
    self.ctrl = wxStaticText(self, -1, text, wxPoint(0,0), size,
                             style=wxST_NO_AUTORESIZE|wxALIGN_LEFT)
    self.clear_color = self.ctrl.GetBackgroundColour()
    
  def SetLabel(self, text):
    self.ctrl.SetLabel(text)
    
  def GetLabel(self):
    return self.ctrl.GetLabel(text)
    
  def ShowPopup(self, text):    
    p = self.parent.ClientToScreen(self.GetPosition())
    s = self.GetClientSize()
    self.popup = wnPopup(self, text, p, s)
    self.popup.Show(True)
    
  def HidePopup(self):
    if self.popup is not None:
      self.popup.Show(False)
      self.popup.Destroy()
      self.popup = None
  
  def OnMouseEnter(self, event):
    self.ctrl.SetBackgroundColour(wnSettings.highlight_color)
    self.Refresh()
    
  def OnMouseLeave(self, event):
    self.ctrl.SetBackgroundColour(self.clear_color)
    self.ctrl.Refresh()

      
class wnDynamicText(wxMaskedTextCtrl):
  def __init__(self, parent, id, text, choices, pos=wxPoint(0,0), size=wxSize(-1,-1)):
    self.parent = parent
    self.bg_color = self.parent.GetBackgroundColour()
    wxMaskedTextCtrl.__init__(self, parent, -1, '', formatcodes='VF_<S',  mask='N{18} | N{18}',
                              pos=pos, size=size, emptyBackgroundColor=self.bg_color,
                              validBackgroundColor=self.bg_color,
                              fields = {0 : Field(validRegex='[a-zA-Z0-9]+'),
                                        1 : Field(choices=choices, choiceRequired=True)
                              },
                              style = wxNO_BORDER, retainFieldValidation = True
                             )
    
    EVT_SET_FOCUS(self, self.OnSetFocus)
    
  def OnSetFocus(self, event):
    x,y = self.GetPosition()
    px, py = self.parent.GetScrollPixelsPerUnit()
    sx, sy = self.parent.GetViewStart()
    self.parent.Scroll(0, sy+y/py)
                               
class wnPopup(wxPopupWindow):
  def __init__(self, parent, text, pos, size):
    wxPopupWindow.__init__(self, parent, wxSIMPLE_BORDER)
    st = wxStaticText(self, -1, text, pos=wxPoint(10,10))
    
    #compute the best position and size
    sz = st.GetBestSize()
    p = wxPoint(pos.x, pos.y+size.GetHeight())
    self.SetPosition(p)
    self.SetSize(wxSize(sz.width+20, sz.height+20))
    
    #set the proper colors
    self.SetBackgroundColour(wnSettings.popup_color)
    st.SetBackgroundColour(wnSettings.popup_color)
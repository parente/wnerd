from wxPython.wx import *
import wnSettings

class wnStaticTextWithEvents(wxPanel):
  def __init__(self, parent, id, text, pos=wxPoint(0,0), size=wxSize(100,20)):
    wxPanel.__init__(self, parent, id, pos, size, style=wxTRANSPARENT_WINDOW)
    
    self.parent = parent

    #make the actual static text control
    self.ctrl = wxStaticText(self, -1, text, wxPoint(0,0), size,
                             style=wxST_NO_AUTORESIZE|wxALIGN_LEFT)
    self.clear_color = self.ctrl.GetBackgroundColour()
    
  def SetLabel(self, text):
    self.ctrl.SetLabel(text)
    
  def GetLabel(self):
    return self.ctrl.GetLabel(text)
    
  def Highlight(self):
    self.ctrl.SetBackgroundColour(wnSettings.highlight_color)
    
  def Unhighlight(self):
    self.ctrl.SetBackgroundColour(self.clear_color)
    
  def ShowPopup(self, text):    
    p = self.parent.ClientToScreen(self.GetPosition())
    s = self.GetClientSize()
    self.popup = wnPopup(self, text, p, s)
    self.popup.Show(True)
    
  def HidePopup(self):
    self.popup.Show(False)
    self.popup.Destroy()
                               
class wnPopup(wxPopupWindow):
  def __init__(self, parent, text, pos, size):
    wxPopupWindow.__init__(self, parent, wxSIMPLE_BORDER)
    st = wxStaticText(self, -1, text, pos=wxPoint(10,10))
    
    #compute the best position and size
    sz = st.GetBestSize()
    p = wxPoint(pos.x, pos.y+size.GetHeight())
    self.SetPosition(p)
    self.SetSize(wxSize(sz.width+20, sz.height+20))
    #self.Fit()
    
    #set the proper colors
    self.SetBackgroundColour(wnSettings.popup_color)
    st.SetBackgroundColour(wnSettings.popup_color)
from wxPython.wx import *
from wxPython.lib.maskededit import Field, wxMaskedTextCtrl
import wnSettings
import WrestlingNerd_wdr as GUI

class wnStaticText(wxPanel):
  def __init__(self, parent, id, text, pos=wxPoint(0,0), size=wxSize(100,20)):
    wxPanel.__init__(self, parent, id, pos, size, style=wxTRANSPARENT_WINDOW)
    
    self.parent = parent
    self.popup = None

    #make the actual static text control
    self.ctrl = wxStaticText(self, -1, text, wxPoint(0,0), size,
                             style=wxST_NO_AUTORESIZE|wxALIGN_LEFT)
    self.ctrl.SetFont(wxFont(8, wxMODERN, wxNORMAL, wxNORMAL))
    self.clear_color = self.ctrl.GetBackgroundColour()
    
    #register events on the text control
    EVT_LEFT_DOWN(self.ctrl, self.OnPassEvent)
    EVT_RIGHT_DOWN(self.ctrl, self.OnPassEvent)
    EVT_LEFT_UP(self.ctrl, self.OnPassEvent)
    EVT_RIGHT_UP(self.ctrl, self.OnPassEvent)
    
    EVT_CLOSE(self, self.OnClose)
    
  def OnPassEvent(self, event):
    event.SetEventObject(self)
    wxPostEvent(self, event)
    
  def OnClose(self, event):
    self.ctrl.Destroy()
    self.Destroy()
    
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
  
  def Highlight(self, flag=True):
    if flag:
      self.ctrl.SetBackgroundColour(wnSettings.highlight_color)
    else:
      self.ctrl.SetBackgroundColour(self.clear_color)
    self.Refresh()

  def ShowMenu(self, pos):
    self.PopupMenu(wnMatchMenu(self), pos)
      
class wnDynamicText(wxMaskedTextCtrl):
  def __init__(self, parent, id, text, choices, pos=wxPoint(0,0), size=wxSize(-1,-1)):
    self.parent = parent
    bg_color = self.parent.GetBackgroundColour()
    mask = 'N{%d} | N{%d}' % (wnSettings.max_name_length, wnSettings.max_team_length)
    wxMaskedTextCtrl.__init__(self, parent, -1, '', formatcodes='VF_<S',  mask=mask,
                              pos=pos, size=size, emptyBackgroundColor=bg_color,
                              validBackgroundColor=bg_color,
                              fields = {0 : Field(validRegex='^[a-zA-Z0-9]+'),
                                        1 : Field(choices=choices, choiceRequired=True)
                              },
                              style = wxNO_BORDER, retainFieldValidation = True
                             )
    self.SetValue(text)
    
    EVT_RIGHT_UP(self, lambda e: None)
    
  def SetFocus(self):
    wxMaskedTextCtrl.SetFocus(self)    
    x,y = self.GetPosition()
    px, py = self.parent.GetScrollPixelsPerUnit()
    sx, sy = self.parent.GetViewStart()
    w, h = self.parent.GetClientSize()

    if y < sy or y > sy+h:
      self.parent.Scroll(0, sy+y/py)
      
  def ShowMenu(self, pos):
    self.PopupMenu(wnSeedMenu(self), pos)
                                     
class wnPopup(wxPopupWindow):
  def __init__(self, parent, text, pos, size):
    wxPopupWindow.__init__(self, parent, wxSIMPLE_BORDER)
    st = wxStaticText(self, -1, text, pos=wxPoint(5,5))
    st.SetFont(wxFont(8, wxMODERN, wxNORMAL, wxNORMAL))
    
    #compute the best position and size
    sz = st.GetBestSize()
    p = wxPoint(pos.x, pos.y+size.GetHeight())
    self.SetPosition(p)
    self.SetSize(wxSize(sz.width+10, sz.height+10))
    
    #set the proper colors
    self.SetBackgroundColour(wnSettings.popup_color)
    st.SetBackgroundColour(wnSettings.popup_color)
    
class wnMatchMenu(wxMenu):
  def __init__(self, ctrl):
    wxMenu.__init__(self)
    self.Append(GUI.ID_DELETE_MATCH_MENU, 'Delete')
    self.Control = ctrl

class wnSeedMenu(wxMenu):
  def __init__(self, ctrl):
    wxMenu.__init__(self)
    self.Append(GUI.ID_DELETE_SEED_MENU, 'Delete')
    self.Control = ctrl
    
class wnMatchDialog(wxDialog):
  '''Class that creates a dialog box that allows users to enter match results.'''
  def __init__(self, parent, wrestlers, result):
    wxDialog.__init__(self, parent, -1, 'Match results')
    GUI.CreateMatchDialog(self)

    #store important references
    self.winner = wxPyTypeCast(self.FindWindowById(GUI.ID_WINNER_CHOICE), 'wxChoice')
    self.result_type = wxPyTypeCast(self.FindWindowById(GUI.ID_RESULT_TYPE_RADIO), 'wxRadioBox')
    self.result_panel = wxPyTypeCast(self.FindWindowById(GUI.ID_RESULT_PANEL), 'wxPanel')
    
    #store the references
    self.wrestlers = wrestlers
    self.result_value = None
    
    #list the wrestlers
    for w in self.wrestlers:
      self.winner.Append(w.Name)
      
    #select the proper result type
    if result is not None:
      self.result_type.SetStringSelection(result.Name)
    
    #select the first wrestler
    self.winner.SetSelection(0)
    
    EVT_RADIOBOX(self, GUI.ID_RESULT_TYPE_RADIO, self.OnChooseResult)
    EVT_BUTTON(self, GUI.wxID_OK, self.OnOK)
    
  def OnOK(self, event):
    '''Make sure all values are filled in properly.'''
    if self.result_value is not None and not self.result_value.IsValid():
      dlg = wxMessageDialog(self, 'Please enter a valid result.', 'Invalid result', style=wxOK)
      dlg.ShowModal()
      dlg.Close()
    else:
      self.EndModal(wxID_OK)
    
  def OnChooseResult(self, event):
    '''Show the proper panel for the selected result type.'''    
    self.result_panel.DestroyChildren()    
    if self.result_type.GetStringSelection() == 'Pin':
      bg_color = self.GetBackgroundColour()
      self.result_value = wxMaskedTextCtrl(self.result_panel, -1, '', formatcodes='RrF',
                                           mask='##:##', validRegex='[0-9 ][0-9]:[0-5][0-9]')
      self.result_value.SetFocus()

    elif self.result_type.GetStringSelection() == 'Decision':
      bg_color = self.GetBackgroundColour()
      self.result_value = wxMaskedTextCtrl(self.result_panel, -1, '', formatcodes='RrF',
                                           mask='##-##', validRegex='[0-9 ][0-9]-[0-9 ][0-9]')
      self.result_value.SetFocus()
    
  def GetWinner(self):
    return self.wrestlers[self.winner.GetSelection()]

  def GetLoser(self):
    if self.winner.GetCount() > 1:
      i = self.winner.GetSelection()
      if i == 0:
        return self.wrestlers[1]
      else:
        return self.wrestlers[0]
  
  def GetResultType(self):
    return self.result_type.GetStringSelection()
  
  def GetResultValue(self):
    '''Return the value of the entered result.'''
    if self.result_type.GetStringSelection() == 'Pin':
      val = self.result_value.GetValue()
      min, sec = [int(v) for v in val.split(':')]
      return min*60 + sec
    
    elif self.result_type.GetStringSelection() == 'Decision':
      val = self.result_value.GetValue()
      scores = [int(v) for v in val.split('-')]
      scores.sort()
      scores.reverse()
      return scores
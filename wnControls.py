import wx
import wx.lib.masked
#from wx.lib.masked import TextCtrl, Field
#from wxPython.lib.maskededit import Field, wxMaskedTextCtrl
import wnSettings
import WrestlingNerd_wdr as GUI

class wnStaticText(wx.Panel):
  def __init__(self, parent, id, text, pos=wx.Point(0,0), size=wx.Size(100,20)):
    wx.Panel.__init__(self, parent, id, pos, size, style=wx.TRANSPARENT_WINDOW)
    
    self.parent = parent
    self.popup = None

    #make the actual static text control
    self.ctrl = wx.StaticText(self, -1, text, wx.Point(0,0), size,
                             style=wx.ST_NO_AUTORESIZE|wx.ALIGN_LEFT)
    self.ctrl.SetFont(wx.Font(wnSettings.screen_font_size, wx.MODERN, wx.NORMAL, wx.NORMAL))
    self.clear_color = self.ctrl.GetBackgroundColour()

    #register events on the text control
    wx.EVT_LEFT_DOWN(self.ctrl, self.OnPassEvent)
    wx.EVT_RIGHT_DOWN(self.ctrl, self.OnPassEvent)
    wx.EVT_LEFT_UP(self.ctrl, self.OnPassEvent)
    wx.EVT_RIGHT_UP(self.ctrl, self.OnPassEvent)
    
    wx.EVT_CLOSE(self, self.OnClose)
    
  def OnPassEvent(self, event):
    event.SetEventObject(self)
    wx.PostEvent(self, event)
    
  def OnClose(self, event):
    self.ctrl.Destroy()
    self.Destroy()
    
  def SetLabel(self, text):
    self.ctrl.SetLabel(text)
    
  def GetLabel(self):
    return self.ctrl.GetLabel(text)
    
  def ShowPopup(self, text):    
    #p = self.parent.ClientToScreen(self.GetPosition())
    s = self.GetClientSize()
    self.popup = wnPopup(self, text, wx.Point(0,0), s)
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
  
  def RefreshScores(self):
    wx.CallAfter(self.parent.RefreshScores)

class wnDynamicText(wx.lib.masked.TextCtrl):
  def __init__(self, parent, id, text, choices, pos=wx.Point(0,0), size=wx.Size(-1,-1)):
    self.parent = parent
    bg_color = self.parent.GetBackgroundColour()
    mask = 'X{%d} | X{%d}' % (wnSettings.max_name_length, wnSettings.max_team_length)
    wx.lib.masked.TextCtrl.__init__(self, parent, -1, '', formatcodes='V_><S',  mask=mask,
                              pos=pos, size=size, validBackgroundColour=bg_color,
                              emptyBackgroundColour=bg_color,
                              fields = {0 : wx.lib.masked.Field(validRegex='^\S+'),
                                        1 : wx.lib.masked.Field(choices=choices, choiceRequired=True, autoSelect=True)
                              },
                              style = wx.NO_BORDER, retainFieldValidation = True
                             )
    self.SetValue(text)
    
    # make an accelerator table that allows short cuts for some seed operations
    ae = [wx.AcceleratorEntry(wx.ACCEL_CTRL, wx.WXK_PRIOR, GUI.ID_SWAPUP_SEED_MENU),
          wx.AcceleratorEntry(wx.ACCEL_CTRL, wx.WXK_NEXT, GUI.ID_SWAPDOWN_SEED_MENU),
          wx.AcceleratorEntry(wx.ACCEL_CTRL, ord('l'), GUI.ID_SETLAST_SEED_MENU),
          wx.AcceleratorEntry(wx.ACCEL_CTRL, ord('L'), GUI.ID_SETLAST_SEED_MENU),
          wx.AcceleratorEntry(wx.ACCEL_CTRL, ord('t'), GUI.ID_SWAPTO_SEED_MENU),
          wx.AcceleratorEntry(wx.ACCEL_CTRL, ord('T'), GUI.ID_SWAPTO_SEED_MENU)]
    self.SetAcceleratorTable(wx.AcceleratorTable(ae))

    wx.EVT_RIGHT_UP(self, lambda e: None)

  def SetFocus(self):
    wx.lib.masked.TextCtrl.SetFocus(self)
    x,y = self.GetPosition()
    px, py = self.parent.GetScrollPixelsPerUnit()
    sx, sy = self.parent.GetViewStart()
    w, h = self.parent.GetClientSize()

    if y < sy or y > sy+h:
      self.parent.Scroll(0, sy+y/py)
      
  def ShowMenu(self, is_last, pos):
    self.PopupMenu(wnSeedMenu(self, is_last), pos)
  
  def RefreshScores(self):
    wx.CallAfter(self.parent.RefreshScores)
    
  def RefreshBracket(self):
    wx.CallAfter(self.parent.RefreshBracket)
                                     
class wnPopup(wx.PopupWindow):
  def __init__(self, parent, text, pos, size):
    wx.PopupWindow.__init__(self, parent, wx.SIMPLE_BORDER)
    st = wx.StaticText(self, -1, text, pos=wx.Point(5,5))
    st.SetFont(wx.Font(wnSettings.screen_font_size, wx.MODERN, wx.NORMAL, wx.NORMAL))
    
    #compute the best position and size
    sz = st.GetBestSize()
    p = wx.Point(pos.x, pos.y+size.GetHeight())
    self.SetPosition(p)
    self.SetSize(wx.Size(sz.width+10, sz.height+10))
    
    #set the proper colors
    self.SetBackgroundColour(wnSettings.popup_color)
    st.SetBackgroundColour(wnSettings.popup_color)
    
class wnMatchMenu(wx.Menu):
  def __init__(self, ctrl):
    wx.Menu.__init__(self)
    self.Append(GUI.ID_MOVEIN_MATCH_MENU, 'Move in')
    self.AppendSeparator()
    self.Append(GUI.ID_DELETE_MATCH_MENU, 'Delete')
    self.Append(GUI.ID_DELETEALL_MATCH_MENU, 'Delete all')
    self.Control = ctrl

class wnSeedMenu(wx.Menu):
  def __init__(self, ctrl, is_last):
    wx.Menu.__init__(self)
    self.AppendCheckItem(GUI.ID_SETLAST_SEED_MENU, 'Last seed\tCtrl-L')
    self.AppendSeparator()
    self.Append(GUI.ID_SWAPUP_SEED_MENU, 'Swap up\tCtrl-Page Up')
    self.Append(GUI.ID_SWAPDOWN_SEED_MENU, 'Swap down\tCtrl-Page Down')
    self.Append(GUI.ID_SWAPTO_SEED_MENU, 'Swap to...\tCtrl-T')
    self.AppendSeparator()
    self.Append(GUI.ID_DELETE_SEED_MENU, 'Delete')
    self.Append(GUI.ID_DELETEMOVEUP_SEED_MENU, 'Delete / Move up')
    self.Append(GUI.ID_INSERTMOVEDOWN_SEED_MENU, 'Insert / Move down')    
    self.Check(GUI.ID_SETLAST_SEED_MENU, is_last)
    
    self.Control = ctrl
    
class wnMatchDialog(wx.Dialog):
  '''Class that creates a dialog box that allows users to enter match results.'''
  def __init__(self, parent, wrestlers, winner, result, is_scoring):
    wx.Dialog.__init__(self, parent, -1, 'Match results')
    GUI.CreateMatchDialog(self)

    #store important references
    self.winner = self.FindWindowById(GUI.ID_WINNER_LIST)
    self.result_type = self.FindWindowById(GUI.ID_RESULT_TYPE_RADIO)
    self.result_panel = self.FindWindowById(GUI.ID_RESULT_PANEL)
    self.scoring_check = self.FindWindowById(GUI.ID_SCOREPOINTS_CHECK)
    
    #store the references
    self.parent = parent
    self.wrestlers = wrestlers
    self.result_value = None
  
    # set the scoring check box to the passed value  
    self.scoring_check.SetValue(is_scoring)
    
    #list the wrestlers
    for w in self.wrestlers:
      self.winner.Append(w.Name)
      
    #select the proper result type and show the result
    if result is not None:
      self.result_type.SetStringSelection(result.Name)
      self.OnChooseResult(None)      
      if result.Name in ['Pin', 'Decision']:
        try:
          self.result_value.SetValue(result.TextValue)
        except:
          pass
        self.result_value.SetFocus()
    
    #select the current wrestler and check is scoring appropriately
    try:
      self.winner.SetStringSelection(winner.Name)
    except:
      self.winner.SetSelection(0)
      
    if result is None:
      self.OnChooseWinner(None)
    else:
      self.scoring_check.SetValue(is_scoring)
    
    wx.EVT_RADIOBOX(self, GUI.ID_RESULT_TYPE_RADIO, self.OnChooseResult)
    wx.EVT_LISTBOX(self, GUI.ID_WINNER_LIST, self.OnChooseWinner) 
    wx.EVT_BUTTON(self, wx.ID_OK, self.OnOK)    
    
  def OnOK(self, event):
    '''Make sure all values are filled in properly.'''
    if self.result_value is not None and not self.result_value.IsValid():
      dlg = wx.MessageDialog(self, 'Please enter a valid result.', 'Invalid result', style=wx.OK)
      dlg.ShowModal()
      dlg.Close()
    else:
      # instruct the parent to update its scores
      wx.CallAfter(self.parent.RefreshScores)
      self.EndModal(wx.ID_OK)
    
  def OnChooseWinner(self, event):
    '''Set if the match is scoring or not based on the winner name. If it contains the non-scoring
    prefix, then do not score the match by default.'''
    if self.GetWinner().IsScoring:
      self.scoring_check.SetValue(True)
    else:
      self.scoring_check.SetValue(False)
    
  def OnChooseResult(self, event):
    '''Show the proper panel for the selected result type.'''    
    self.result_panel.DestroyChildren()
    self.result_value = None
    
    if self.result_type.GetStringSelection() == 'Pin':
      bg_color = self.GetBackgroundColour()
      self.result_value = wx.lib.masked.TextCtrl(self.result_panel, -1, '', formatcodes='RF',
                                           mask='##:##', validRegex='[0-9 ][0-9]:[0-5][0-9]',
                                           emptyInvalid = True)
      self.result_value.SetFocus()

    elif self.result_type.GetStringSelection() == 'Decision':
      bg_color = self.GetBackgroundColour()
      self.result_value = wx.lib.masked.TextCtrl(self.result_panel, -1, '', formatcodes='RrF',
                                           mask='##-##', validRegex='[0-9 ][0-9]-[0-9 ][0-9]',
                                           emptyInvalid = True)
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

  def GetIsScoring(self):
    return self.scoring_check.IsChecked()
'''
The UI module defines classes that present the major user interface components to the user including
the main frame, the bracket canvas, and the side panel.
'''

from wxPython.wx import *
from wxPython.wizard import *
from wnBuilder import *
from wnRenderer import *
import WrestlingNerd_wdr as GUI
import wnSettings
import cPickle

class wnFrame(wxFrame):
  '''Class that creates and manages the main WN window.'''
  
  def __init__(self):
    '''Initialize the frame.'''
    wxFrame.__init__(self, None, -1, 'Wrestling Nerd',
                     style=wxDEFAULT_FRAME_STYLE|wxNO_FULL_REPAINT_ON_RESIZE|wxCLIP_CHILDREN)
  
    #set the menu bar
    mb = GUI.CreateMenuBar()
    self.SetMenuBar(mb)
    
    #correct the background color
    self.SetBackgroundColour(mb.GetBackgroundColour())
    
    #create a sizer to layout the window
    sizer = wxFlexGridSizer(1,2,0,0)
    sizer.AddGrowableCol(0)
    sizer.AddGrowableRow(0)
  
    #create a bracket canvas
    self.canvas = wnBracketCanvas(self)
    sizer.AddWindow(self.canvas, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxLEFT|wxRIGHT|wxBOTTOM|wxTOP, 5)
    
    #create a frame housing the layer components
    panel = wxPanel(self, -1)
    score_frame = GUI.CreateScoreFrame(panel)
    sizer.AddSizer(panel, 0, 5)
    
    #add the sizer to the window
    self.SetSizer(sizer)
    
    #create class variables
    self.tournament = None
    self.filename = None
    self.weights = wxPyTypeCast(self.FindWindowById(GUI.ID_WEIGHTS_CHOICE), 'wxChoice')
    self.teams = wxPyTypeCast(self.FindWindowById(GUI.ID_TEAMS_LIST), 'wxListCtrl')
    
    #make a painter object
    self.painter = wnPainter(self, self.canvas)
    
    #set up the list control
    self.teams.InsertColumn(0, 'Team', width=-2)
    self.teams.InsertColumn(1, 'Score', width=-2)

    #disable menu items
    self.ChangeMenuState('on start')
    
    EVT_CLOSE(self, self.OnClose)
    EVT_MENU(self, GUI.ID_EXIT_MENU, self.OnClose)
    EVT_MENU(self, GUI.ID_NEW_MENU, self.OnNew)
    EVT_MENU(self, GUI.ID_SAVE_MENU, self.OnSave)
    EVT_MENU(self, GUI.ID_SAVEAS_MENU, self.OnSaveAs)
    EVT_MENU(self, GUI.ID_OPEN_MENU, self.OnOpen)
    EVT_MENU(self, GUI.ID_PRINT_MENU, self.OnPrint)
    EVT_MENU(self, GUI.ID_NUMBOUTS_MENU, self.OnCountBouts)
    EVT_MENU(self, GUI.ID_FASTFALL_MENU, self.OnFastFall)
    EVT_CHOICE(self, GUI.ID_WEIGHTS_CHOICE, self.OnSelectWeight)
    EVT_LIST_ITEM_ACTIVATED(self, GUI.ID_TEAMS_LIST, self.OnSelectTeam)
    
  def OnClose(self, event):
    '''Handle a window close event.'''
    self.canvas.Close()
    self.Destroy()
    
  def OnNew(self, event):
    '''Show the new tournament wizard.'''
    builder = wnBuilder()
    
    #create and configure the wizard
    wiz = wnNewTournamentWizard(self)
    wiz.SetAvailableLayouts(builder.GetTournaments())
    
    #if the wizard completes successfully
    if wiz.RunWizard():
      name = wiz.GetName()
      weights = wiz.GetWeights()
      teams = wiz.GetTeams()
      layout = wiz.GetLayout()
        
      #create the tournament
      self.tournament = builder.Create(layout, name, weights, teams)
      
      #reset the GUI
      self.ResetAfterNew()
      self.ChangeMenuState('on new')
      self.filename = None
      
  def OnSave(self, event):
    '''Save the current tournament to disk by pickling it.'''
    if self.filename is None:
      self.OnSaveAs(event)
    else:
      f = file(self.filename, 'wb')
      cPickle.dump(self.tournament, f, True)
      f.close()

  def OnSaveAs(self, event):
    dlg = wxFileDialog(self, 'Save tournament', wildcard='Wrestling Nerd files (*.wnd)|*.wnd',
                         style=wxSAVE|wxOVERWRITE_PROMPT)
      
    if dlg.ShowModal() == wxID_OK:
      f = file(dlg.GetPath(), 'wb')
      cPickle.dump(self.tournament, f, True)
      f.close()
      self.ChangeMenuState('on save')
      self.filename = dlg.GetPath()
      
  def OnOpen(self, event):
    '''Open a tournament from disk.'''
    dlg = wxFileDialog(self, 'Open tournament', wildcard='Wrestling Nerd files (*.wnd)|*.wnd',
                       style=wxOPEN|wxHIDE_READONLY)
    
    if dlg.ShowModal() == wxID_OK:
      f = file(dlg.GetPath(), 'rb')
      self.tournament = cPickle.load(f)
      f.close()
      self.ResetAfterNew()
      self.ChangeMenuState('on open')
      self.filename = dlg.GetPath()
      
  def OnPrint(self, event):
    '''Show the print dialog box.'''
    dlg = wnPrintDialog(self, self.tournament.Weights,
                        self.tournament.Rounds, self.GetCurrentWeight())
    dlg.CentreOnScreen()
    
    # if the user wants to print, show the print settings dialog
    if dlg.ShowModal() == wxID_OK:
      printer = wxPrinter()
      printer.Print(self, None, True)
      
    dlg.Destroy()
    
  def OnCountBouts(self, event):
    '''Count the number of bouts and show the result in a simple dialog.'''
    i = self.tournament.CountBouts()
    
    if i == 1:
      msg = 'There is 1 bout in the tournament.'
    else:
      msg = 'There are ' + str(i) + ' bouts in the tournament.'
    
    dlg = wxMessageDialog(self, msg, 'Bout count')
    dlg.ShowModal()
    dlg.Destroy()
    
  def OnFastFall(self, event):
    '''Show the fast fall dialog.'''
    dlg = wnFastFallDialog(self, self.tournament.CalcFastFall())
    dlg.CentreOnScreen()
    dlg.ShowModal()
    dlg.Destroy()
      
  def OnSelectWeight(self, event):
    '''Refresh the canvas to show the new weight.'''
    self.canvas.Refresh()
    
  def OnSelectTeam(self, event):
    '''Show a dialog box containing properties of a team.'''
    name = event.GetText()
    dlg = wnTeamDialog(self, self.tournament.Teams[name])
    dlg.CentreOnScreen()
    
    # check if the user wants to make changes to the team score
    if dlg.ShowModal() == wxID_OK:
      self.RefreshScores()
      
    dlg.Destroy()
    
  def GetTournament(self):
    return self.tournament
  
  def GetCurrentWeight(self):
    if self.weights.GetSelection() == -1:
      return None
    else:
      return self.weights.GetStringSelection()
    
  def RefreshScores(self):
    '''Refresh the team scores.'''
    # tell the tournament to update the scores for the current weight
    scores = self.tournament.CalcScores(self.GetCurrentWeight())
    
    # refresh the score display
    self.teams.DeleteAllItems()
    for i in range(len(scores)):
      score, name = scores[i]
      self.teams.InsertStringItem(i, name)
      self.teams.SetStringItem(i, 1, str(score))
      
  def ResetAfterNew(self):
    '''Reset the GUI after a tournament has been created or opened.'''

    #add the weights to the weight drop-down      
    self.weights.Clear()
    for w in self.tournament.Weights:
      self.weights.Append(w)
    self.weights.SetSelection(0)
    
    #add the teams to the team list
    self.RefreshScores()

    #show the tournament name in the window titlebar
    self.SetTitle('Wrestling Nerd - '+self.tournament.name)
        
    #reset and draw the bracket
    self.painter.ResetControls()
    self.canvas.Reset()
    self.canvas.Refresh()
     
  def ChangeMenuState(self, action):
    mb = self.GetMenuBar()
    if action == 'on start':
      mb.FindItemById(GUI.ID_FASTFALL_MENU).Enable(False)
      mb.FindItemById(GUI.ID_NUMBOUTS_MENU).Enable(False)
      mb.FindItemById(GUI.ID_SAVE_MENU).Enable(False)
      mb.FindItemById(GUI.ID_SAVEAS_MENU).Enable(False)
      mb.FindItemById(GUI.ID_PRINT_MENU).Enable(False)
    
    elif action == 'on new':
      mb.FindItemById(GUI.ID_FASTFALL_MENU).Enable(True)
      mb.FindItemById(GUI.ID_NUMBOUTS_MENU).Enable(True)
      mb.FindItemById(GUI.ID_SAVE_MENU).Enable(True)      
      mb.FindItemById(GUI.ID_SAVEAS_MENU).Enable(False)
      mb.FindItemById(GUI.ID_PRINT_MENU).Enable(True)
      
    elif action == 'on open':
      mb.FindItemById(GUI.ID_FASTFALL_MENU).Enable(True)
      mb.FindItemById(GUI.ID_NUMBOUTS_MENU).Enable(True)
      mb.FindItemById(GUI.ID_SAVE_MENU).Enable(True)      
      mb.FindItemById(GUI.ID_SAVEAS_MENU).Enable(True)
      mb.FindItemById(GUI.ID_PRINT_MENU).Enable(True)

    elif action == 'on save':
      mb.FindItemById(GUI.ID_SAVEAS_MENU).Enable(True)

    
  def GetPainter(self):
    '''Return a reference to the painter object.'''
    return self.painter
  
class wnBracketCanvas(wxScrolledWindow):
  def __init__(self, parent):
    wxScrolledWindow.__init__(self, parent, -1, style=wxNO_FULL_REPAINT_ON_RESIZE)
    self.parent = parent
    self.old_weight = None
    
    EVT_PAINT(self, self.OnPaint)
    
  def Reset(self):
    self.DestroyChildren()
    self.Scroll(0,0)
    self.old_weight = None
    
  def OnPaint(self, event):
    dc = wxPaintDC(self)
    self.PrepareDC(dc)

    t = self.parent.GetTournament()
    w = self.parent.GetCurrentWeight()

    if t is not None and w is not None:
      refresh = (w != self.old_weight)
      
      p = self.parent.GetPainter()    
      p.SetDC(dc)      
      xmax, ymax = t.Paint(p, w, refresh)
      p.Flush()
      p.SetDC(None)

      self.old_weight = w
      self.SetVirtualSize(wxSize(xmax, ymax))
      self.SetScrollRate(10,10)      

      if refresh: p.SetInitialFocus()
      
  def RefreshScores(self):
    self.parent.RefreshScores()
    
class wnNewTournamentWizard(wxWizard):
  '''Class that creates a wizard that assists users in setting up new tournaments.'''
  
  def __init__(self, parent):
    '''Initialize an instance of the wizard.
    
    Params:
    
    'parent': The parent window of the wizard
    '''
    wxWizard.__init__(self, parent, -1, 'New tournament')
    
    #create the pages of the wizard
    self.start_page = wxWizardPageSimple(self)
    GUI.WizardStartPanel(self.start_page)
    self.name_page  = wxWizardPageSimple(self)
    GUI.WizardNamePanel(self.name_page)
    self.teams_page = wxWizardPageSimple(self)
    GUI.WizardTeamsPanel(self.teams_page)
    self.weights_page = wxWizardPageSimple(self)
    GUI.WizardWeightsPanel(self.weights_page)
    self.layout_page = wxWizardPageSimple(self)
    GUI.WizardLayoutPanel(self.layout_page)
    self.finished_page = wxWizardPageSimple(self)
    GUI.WizardFinishedPanel(self.finished_page)
    
    #order the pages
    wxWizardPageSimple_Chain(self.start_page, self.name_page)
    wxWizardPageSimple_Chain(self.name_page, self.teams_page)
    wxWizardPageSimple_Chain(self.teams_page, self.weights_page)
    wxWizardPageSimple_Chain(self.weights_page, self.layout_page)
    wxWizardPageSimple_Chain(self.layout_page, self.finished_page)
    
    #size the wizard appropriately
    self.FitToPage(self.start_page)
    
    #store important references
    self.teams = wxPyTypeCast(self.FindWindowById(GUI.ID_TEAMS_COMBO), 'wxComboBox')
    self.weights = wxPyTypeCast(self.FindWindowById(GUI.ID_WEIGHTS_COMBO), 'wxComboBox')
    self.layouts = wxPyTypeCast(self.FindWindowById(GUI.ID_LAYOUT_LIST), 'wxListBox')
    self.name = wxPyTypeCast(self.FindWindowById(GUI.ID_NAME_TEXT), 'wxTextCtrl')
    self.description = wxPyTypeCast(self.FindWindowById(GUI.ID_LAYOUT_TEXT), 'wxTextCtrl')
        
    #set event handlers
    EVT_BUTTON(self, GUI.ID_ADD_TEAM, self.OnAddTeam)
    EVT_BUTTON(self, GUI.ID_REMOVE_TEAM, self.OnRemoveTeam)
    EVT_BUTTON(self, GUI.ID_ADD_WEIGHT, self.OnAddWeight)
    EVT_BUTTON(self, GUI.ID_REMOVE_WEIGHT, self.OnRemoveWeight)
    EVT_BUTTON(self, GUI.ID_ADD_STANDARD_WEIGHTS, self.OnAddStandardWeights)    
    EVT_WIZARD_PAGE_CHANGED(self, self.GetId(), self.OnPageChanged)
    EVT_WIZARD_PAGE_CHANGING(self, self.GetId(), self.OnPageChanging)
    EVT_LISTBOX(self, GUI.ID_LAYOUT_LIST, self.OnSelectLayout)
 
  def OnSelectLayout(self, event):
    '''Show the description of the selected layout.'''
    c = self.layouts.GetClientData(event.GetInt())
    self.description.SetValue(c.Description)
    
  def OnPageChanging(self, event):
    '''Make sure the values are valid.'''
    if event.GetPage() == self.name_page and self.name.GetValue() == '':
      wxMessageDialog(self, 'You must enter a tournament name.', 'Invalid name', wxOK).ShowModal()
      event.Veto()
    elif event.GetPage() == self.teams_page and self.teams.GetCount() == 0:
      wxMessageDialog(self, 'The tournament must have at least one team.', 'No teams',
                      wxOK).ShowModal()
      event.Veto()
    elif event.GetPage() == self.weights_page and self.weights.GetCount() == 0:
      wxMessageDialog(self, 'The tournament must have at least one weight class.',
                      'No weight classes', wxOK).ShowModal()
      event.Veto()
      
  def OnPageChanged(self, event):
    '''Change the accelerator table appropriately.'''
    if event.GetPage() == self.teams_page:
      table = wxAcceleratorTable([(wxACCEL_CTRL, WXK_RETURN, GUI.ID_ADD_TEAM)])
      self.SetAcceleratorTable(table)
    elif event.GetPage() == self.weights_page:
      table = wxAcceleratorTable([(wxACCEL_CTRL, WXK_RETURN, GUI.ID_ADD_WEIGHT)])
      self.SetAcceleratorTable(table)
                            
  def OnAddTeam(self, event):
    t = self.teams.GetValue()
    if self.teams.FindString(t) != -1 or t == '': return
    self.teams.Append(t[0:wnSettings.max_team_length])
    self.teams.SetValue('')
  
  def OnRemoveTeam(self, event):
    i = self.teams.GetSelection()
    if i == -1: return    
    self.teams.Delete(i)
    
    #select the next item in the teams list
    c = self.teams.GetCount()
    if i >= c:
      i = c-1
    if c > 0:
      self.teams.SetSelection(i)
      
  def OnAddWeight(self, event):
    w = self.weights.GetValue()
    if self.weights.FindString(w) != -1 or w == '': return
    self.weights.Append(w)
    self.weights.SetValue('')
    
  def OnRemoveWeight(self, event):
    i = self.weights.GetSelection()
    if i == -1: return
    self.weights.Delete(i)

    #select the next item in the weights list
    c = self.weights.GetCount()
    if i >= c:
      i = c-1
    if c > 0:
      self.weights.SetSelection(i)
      
  def OnAddStandardWeights(self, event):
    ws = ['95', '103', '112', '119', '125', '130', '135', '140', '145', '152', '160', '171', '189',
          '215', '275']
    for w in ws:
      self.weights.Append(w)
        
  def RunWizard(self):
    '''Override the run method to automatically use the first page.'''
    return wxWizard.RunWizard(self, self.start_page)
    
  def SetAvailableLayouts(self, ts):
    '''Set the available tournaments.'''
    for c in ts:
      self.layouts.Append(c.Name, c)
    self.layouts.SetSelection(0)
    c = self.layouts.GetClientData(0)
    self.description.SetValue(c.Description)
      
  def GetName(self):
    return self.name.GetValue()
  
  def GetWeights(self):
    ws = []
    for i in range(self.weights.GetCount()):
      ws.append(self.weights.GetString(i))
    return ws
  
  def GetTeams(self):
    ts = []
    for i in range(self.teams.GetCount()):
      ts.append(self.teams.GetString(i))
    return ts
  
  def GetLayout(self):
    i = self.layouts.GetSelection()
    return self.layouts.GetClientData(i)

class wnPrintDialog(wxDialog):
  '''Class that creates a dialog box that allows users to select what to print.'''
  def __init__(self, parent, weights, rounds, current_weight):
    wxDialog.__init__(self, parent, -1, 'Print')
    GUI.CreatePrintDialog(self)
    
    # store references
    self.weights = wxPyTypeCast(self.FindWindowById(GUI.ID_WEIGHTS_LIST), 'wxListBox')
    self.rounds = wxPyTypeCast(self.FindWindowById(GUI.ID_ROUNDS_LIST), 'wxListBox')
    self.type = wxPyTypeCast(self.FindWindowById(GUI.ID_TYPE_RADIOBOX), 'wxRadioBox')
    
    # fill the list boxes and set initial selections
    self.weights.Set(weights)
    self.rounds.Set(rounds)
    self.weights.SetStringSelection(current_weight)
    self.rounds.SetSelection(0)
    
    # watch for events to enable or disable the rounds control
    EVT_RADIOBOX(self, GUI.ID_TYPE_RADIOBOX, self.OnTypeChange)
    EVT_BUTTON(self, wxID_OK, self.OnOK)
    
  def OnOK(self, event):
    '''Make sure the selections are valid before closing the dialog.'''
    if len(self.weights.GetSelections()) == 0:
      wxMessageDialog(self, 'You must select at least one weight class.', 'Select a weight class', wxOK).ShowModal()
      return False
    if self.type.GetStringSelection() == 'Bouts' and len(self.rounds.GetSelections()) == 0:
      wxMessageDialog(self, 'You must select at least one round to print bouts.', 'Select a round', wxOK).ShowModal()
      return False
    
    self.EndModal(wxID_OK) 
  
  def OnTypeChange(self, event):
    '''Enable or disable the rounds box based on what's selected.'''
    self.rounds.Enable(self.type.GetStringSelection() == 'Bouts')
  
  def GetSelection(self):
    return []
  
class wnTeamDialog(wxDialog):
  '''Class that creates a dialog box that shows team info.'''
  def __init__(self, parent, team):
    wxDialog.__init__(self, parent, -1, 'Team Properties: '+team.Name)
    GUI.CreateTeamDialog(self)
    
    # get important references
    self.pa_text = wxPyTypeCast(self.FindWindowById(GUI.ID_POINTADJUST_TEXT), 'wxTextCtrl')
    self.wrestlers = wxPyTypeCast(self.FindWindowById(GUI.ID_WRESTLERS_LIST), 'wxListCtrl')
    
    # store the team for later reference
    self.team = team
    
    # set up the list control
    self.wrestlers.InsertColumn(0, 'Weight', width=-2)
    self.wrestlers.InsertColumn(1, 'Name', width=100)
    
    # show the current team stats
    self.pa_text.SetValue(str(self.team.PointAdjust))
    
    wrestlers = self.team.Wrestlers
    for i in range(len(wrestlers)):
      w = wrestlers[i]
      self.wrestlers.InsertStringItem(i, w.Weight)
      self.wrestlers.SetStringItem(i, 1, w.Name)      
    
    # set events
    EVT_SPIN_UP(self, GUI.ID_POINTADJUST_SPIN, self.OnPointUp)
    EVT_SPIN_DOWN(self, GUI.ID_POINTADJUST_SPIN, self.OnPointDown)
    EVT_BUTTON(self, wxID_OK, self.OnOK)
    
  def OnOK(self, event):
    self.team.PointAdjust = float(self.pa_text.GetValue())
    self.EndModal(wxID_OK)
    
  def OnPointUp(self, event):
    self.pa_text.SetValue(str(float(self.pa_text.GetValue()) + 0.5))
  
  def OnPointDown(self, event):
    self.pa_text.SetValue(str(float(self.pa_text.GetValue()) - 0.5))
    
class wnFastFallDialog(wxDialog):
  def __init__(self, parent, table):
    wxDialog.__init__(self, parent, -1, 'Fast fall results')
    GUI.CreateFastFallDialog(self)
    
    # get a reference to the results list control
    self.results = wxPyTypeCast(self.FindWindowById(GUI.ID_RESULTS_LIST), 'wxListCtrl')
    
    # set up the list control
    self.results.InsertColumn(0, 'Name', width=100)
    self.results.InsertColumn(1, 'Team', width=100)
    self.results.InsertColumn(2, 'Weight', width=-2)
    self.results.InsertColumn(3, 'Pins', width=-2)
    self.results.InsertColumn(4, 'Time', width=-2)
    
    # show the results
    for i in range(len(table)):
      num, time, time_str, name, team, weight = table[i]
      self.results.InsertStringItem(i, name)
      self.results.SetStringItem(i, 1, team)
      self.results.SetStringItem(i, 2, weight)
      self.results.SetStringItem(i, 3, str(num))
      self.results.SetStringItem(i, 4, time_str)

class wnScoreWindow(wxFrame):
  '''Class the creates a standalone frame for displaying team scores. Teams scroll past at a regular
  interval. Useful for multi-monitor setups with scores on public display.'''
  def __init__(self, parent):
    pass
    
if __name__ == '__main__':
  app = wxPySimpleApp(0)
  frame = wnFrame()
  frame.Centre()
  app.SetTopWindow(frame)
  frame.Show()  
  app.MainLoop()
'''
The UI module defines classes that present the major user interface components to the user including
the main frame, the bracket canvas, and the side panel.
'''

from wxPython.wx import *
from wxPython.wizard import *
from wnBuilder import *
from wnRenderer import *
from wnPrinting import *
from wnExport import *
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
    self.SetIcon(wxIcon(wnSettings.icon_filename, wxBITMAP_TYPE_ICO))
    
    #create a sizer to layout the window
    sizer = wxFlexGridSizer(1,2,0,0)
    sizer.AddGrowableCol(0)
    sizer.AddGrowableRow(0)
  
    #create a bracket canvas
    self.canvas = wnBracketCanvas(self)
    sizer.AddWindow(self.canvas, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxLEFT|wxRIGHT|wxBOTTOM|wxTOP, 5)
    
    #create a frame housing the layer components
    panel = wxPanel(self, -1)
    score_frame = GUI.CreateSidePanel(panel)
    sizer.AddWindow(panel, 0, wxGROW, 5)
    
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
    EVT_MENU(self, GUI.ID_EXPORT_MENU, self.OnExport)
    EVT_MENU(self, GUI.ID_OPEN_MENU, self.OnOpen)
    EVT_MENU(self, GUI.ID_PRINT_MENU, self.OnPrint)
    EVT_MENU(self, GUI.ID_NUMBOUTS_MENU, self.OnCountBouts)
    EVT_MENU(self, GUI.ID_FASTFALL_MENU, self.OnFastFall)
    EVT_MENU(self, GUI.ID_SCOREWIN_MENU, self.OnScoreWindow)
    EVT_MENU(self, GUI.ID_ADDTEAM_MENU, self.OnAddTeam)
    EVT_MENU(self, GUI.ID_REMOVETEAM_MENU, self.OnRemoveTeam)
    EVT_MENU(self, GUI.ID_TEAMSPELLING_MENU, self.OnChangeTeamSpelling)
    EVT_MENU(self, GUI.ID_WRESTLERSPELLING_MENU, self.OnChangeWrestlerSpelling)
    EVT_MENU(self, GUI.ID_ABOUT_MENU, self.OnAbout)
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
      
    dlg.Destroy()
      
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
      
    dlg.Destroy()
      
  def OnExport(self, event):
    '''Show the export dialog. Right now, only export to plain text.'''
    dlg = wxFileDialog(self, 'Export plain text', wildcard='Text files (*.txt)|*.txt',
                         style=wxSAVE|wxOVERWRITE_PROMPT)
    
    if dlg.ShowModal() == wxID_OK:
      exp = wnExportPlainText(dlg.GetPath(), self.tournament)
      exp.Save()
      
    dlg.Destroy()
      
  def OnPrint(self, event):
    '''Show the print dialog box.'''
    dlg = wnPrintDialog(self, self.tournament.Weights,
                        self.tournament.Rounds, self.GetCurrentWeight())
    dlg.CentreOnScreen()
    
    # if the user wants to print, show the print settings dialog
    if dlg.ShowModal() == wxID_OK:
      # use the print factory to do all the printing
      wnPrintFactory.Print(self, self.tournament, dlg.GetType(),
                           dlg.GetWeights(), dlg.GetRounds(), self.canvas.GetBracketSize())
      
    dlg.Destroy()
    
  def OnCountBouts(self, event):
    '''Count the number of bouts and show the result in a simple dialog.'''
    i = self.tournament.CountBouts()
    
    if i == 1:
      msg = 'There is 1 bout in the tournament.'
    else:
      msg = 'There are ' + str(i) + ' bouts in the tournament.'
    
    dlg = wxMessageDialog(self, msg, 'Bout count', style=wxOK)
    dlg.ShowModal()
    dlg.Destroy()
    
  def OnFastFall(self, event):
    '''Show the fast fall dialog.'''
    dlg = wnFastFallDialog(self, self.tournament.CalcFastFall())
    dlg.CentreOnScreen()
    dlg.ShowModal()
    dlg.Destroy()
    
  def OnScoreWindow(self, event):
    '''Show the score window.'''
    score_win = wnScoreWindow(self)
    score_win.Show(True)
    
  def OnAddTeam(self, event):
    # let the user enter a team name
    dlg = wxTextEntryDialog(self, 'Enter the name of the new team.', 'Add team')
    if dlg.ShowModal() == wxID_OK:
      try:
        self.tournament.TeamNames.index(dlg.GetValue())
      except:
        self.tournament.NewTeam(dlg.GetValue())
        self.ResetAfterNew()
      
    dlg.Destroy()
  
  def OnRemoveTeam(self, event):
    #make sure there is more than one team left
    if len(self.tournament.TeamNames) <= 1:
      dlg = wxMessageDialog(self, 'You cannot delete the last team.', 'One team left')
      dlg.ShowModal()
      dlg.Destroy()
      return
    
    # let the user pick the team to delete
    names = self.tournament.TeamNames
    dlg = wxSingleChoiceDialog(self, 'Choose the team to delete.', 'Remove team',
                               names)
    if dlg.ShowModal() == wxID_OK:
      self.tournament.DeleteTeam(dlg.GetStringSelection())
      self.ResetAfterNew()
      
    dlg.Destroy()
    
  def OnChangeTeamSpelling(self, event):
    '''Show the dialog that allows a user to change the spelling of a team name.'''
    dlg = wnTeamSpellingDialog(self, self.tournament.TeamNames)
    dlg.CentreOnScreen()
    
    if dlg.ShowModal() == wxID_OK:
      self.tournament.ChangeTeam(dlg.GetOldName(), dlg.GetNewName())
      self.ResetAfterNew()
        
    dlg.Destroy()
    
  def OnChangeWrestlerSpelling(self, event):
    '''Show the dialog that allows a user to change the spelling of a wrestler name.'''
    dlg = wnWrestlerSpellingDialog(self, self.tournament.Teams)
    dlg.CentreOnScreen()
    
    if dlg.ShowModal() == wxID_OK:
      t = self.tournament.Teams[dlg.GetTeamName()]
      t.ChangeWrestler(dlg.GetOldName(), dlg.GetNewName())
      self.ResetAfterNew()
        
    dlg.Destroy()    
    
  def OnAbout(self, event):
    '''Show the about window.'''
    dlg = wxDialog(self, -1, 'About')
    GUI.CreateAboutDialog(dlg)
    dlg.SetBackgroundColour(wxWHITE)
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
      mb.FindItemById(GUI.ID_EXPORT_MENU).Enable(False)
      mb.FindItemById(GUI.ID_PRINT_MENU).Enable(False)
      mb.FindItemById(GUI.ID_SCOREWIN_MENU).Enable(False)
      mb.FindItemById(GUI.ID_ADDTEAM_MENU).Enable(False)
      mb.FindItemById(GUI.ID_REMOVETEAM_MENU).Enable(False)
      mb.FindItemById(GUI.ID_TEAMSPELLING_MENU).Enable(False)
      mb.FindItemById(GUI.ID_WRESTLERSPELLING_MENU).Enable(False)
    
    elif action == 'on new':
      mb.FindItemById(GUI.ID_FASTFALL_MENU).Enable(True)
      mb.FindItemById(GUI.ID_NUMBOUTS_MENU).Enable(True)
      mb.FindItemById(GUI.ID_SAVE_MENU).Enable(True)      
      mb.FindItemById(GUI.ID_SAVEAS_MENU).Enable(False)
      mb.FindItemById(GUI.ID_EXPORT_MENU).Enable(True)
      mb.FindItemById(GUI.ID_PRINT_MENU).Enable(True)
      mb.FindItemById(GUI.ID_SCOREWIN_MENU).Enable(True)
      mb.FindItemById(GUI.ID_ADDTEAM_MENU).Enable(True)
      mb.FindItemById(GUI.ID_REMOVETEAM_MENU).Enable(True)
      mb.FindItemById(GUI.ID_TEAMSPELLING_MENU).Enable(True)
      
    elif action == 'on open':
      mb.FindItemById(GUI.ID_FASTFALL_MENU).Enable(True)
      mb.FindItemById(GUI.ID_NUMBOUTS_MENU).Enable(True)
      mb.FindItemById(GUI.ID_SAVE_MENU).Enable(True)      
      mb.FindItemById(GUI.ID_SAVEAS_MENU).Enable(True)
      mb.FindItemById(GUI.ID_EXPORT_MENU).Enable(True)
      mb.FindItemById(GUI.ID_PRINT_MENU).Enable(True)
      mb.FindItemById(GUI.ID_SCOREWIN_MENU).Enable(True)
      mb.FindItemById(GUI.ID_ADDTEAM_MENU).Enable(True)
      mb.FindItemById(GUI.ID_REMOVETEAM_MENU).Enable(True)
      mb.FindItemById(GUI.ID_TEAMSPELLING_MENU).Enable(True)

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
    self.bracket_size = wxSize(0,0)
    self.need_refresh = False
    
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
      xmax, ymax = t.Paint(p, w, refresh or self.need_refresh)
      p.Flush()
      p.SetDC(None)

      self.old_weight = w
      self.bracket_size = wxSize(xmax, ymax)
      self.SetVirtualSize(self.bracket_size)
      self.SetScrollRate(10,10)

      self.need_refresh = False
      if refresh: p.SetInitialFocus()
      
  def RefreshBracket(self):
    self.need_refresh = True
    self.Refresh()
      
  def RefreshScores(self):
    self.parent.RefreshScores()
    
  def GetBracketSize(self):
    return self.bracket_size
    
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
    
    #set the captions
    cap = wxPyTypeCast(self.FindWindowById(GUI.ID_START_CAPTION), 'wxStaticText')
    cap.SetLabel(GUI.start_caption)
    cap = wxPyTypeCast(self.FindWindowById(GUI.ID_NAME_CAPTION), 'wxStaticText')
    cap.SetLabel(GUI.name_caption)
    cap = wxPyTypeCast(self.FindWindowById(GUI.ID_TEAMS_CAPTION), 'wxStaticText')
    cap.SetLabel(GUI.teams_caption)
    cap = wxPyTypeCast(self.FindWindowById(GUI.ID_WEIGHTS_CAPTION), 'wxStaticText')
    cap.SetLabel(GUI.weights_caption)    
    cap = wxPyTypeCast(self.FindWindowById(GUI.ID_LAYOUT_CAPTION), 'wxStaticText')
    cap.SetLabel(GUI.layout_caption)
    cap = wxPyTypeCast(self.FindWindowById(GUI.ID_FINISHED_CAPTION), 'wxStaticText')
    cap.SetLabel(GUI.finished_caption)
    
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
    if self.type.GetStringSelection() == 'B&outs' and len(self.rounds.GetSelections()) == 0:
      wxMessageDialog(self, 'You must select at least one round to print bouts.', 'Select a round', wxOK).ShowModal()
      return False
    
    self.EndModal(wxID_OK) 
  
  def OnTypeChange(self, event):
    '''Enable or disable the rounds box based on what is selected.'''
    self.rounds.Enable(self.type.GetStringSelection() == 'B&outs')
    self.weights.Enable(self.type.GetStringSelection() != '&Scores')
  
  def GetWeights(self):
    weights = []
    for i in self.weights.GetSelections():
      weights.append(self.weights.GetString(i))
    return weights
                  
  def GetRounds(self):
    rounds = []
    for i in self.rounds.GetSelections():
      rounds.append(self.rounds.GetString(i))
    return rounds
  
  def GetType(self):
    strings = {'&Brackets' : 'Brackets', 'B&outs' : 'Bouts', '&Scores' : 'Scores',
               '&Places' : 'Places'}
    return strings[self.type.GetStringSelection()]
  
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
  '''Class that creates a dialog showing the fastest fall times in descending order.'''
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
      ff = table[i]
      self.results.InsertStringItem(i, ff.Name)
      self.results.SetStringItem(i, 1, ff.Team)
      self.results.SetStringItem(i, 2, ff.Weight)
      self.results.SetStringItem(i, 3, str(ff.Pins))
      self.results.SetStringItem(i, 4, ff.TimeText)

class wnScoreWindow(wxFrame):
  '''Class the creates a standalone frame for displaying team scores. Teams scroll past at a regular
  interval. Useful for multi-monitor setups with scores on public display.'''
  def __init__(self, parent):
    wxFrame.__init__(self, parent, -1, '', size=wxSize(640, 480),
                     style=wxDEFAULT_FRAME_STYLE|wxNO_FULL_REPAINT_ON_RESIZE|wxCLIP_CHILDREN)
    
    # set up the UI                 
    GUI.CreateScoreFrame(self, False, False)
    self.SetIcon(parent.GetIcon())
        
    # get a reference to the list control
    self.scores = wxPyTypeCast(self.FindWindowById(GUI.ID_SCORES_LIST), 'wxListCtrl')
    
    # set up the list control
    self.scores.InsertColumn(0, 'Place', width=120)
    self.scores.InsertColumn(1, 'Team', width=300)
    self.scores.InsertColumn(2, 'Score', width=140)
    
    # create object variables
    self.index = 0
    self.parent = parent
    
    # set the window title
    self.SetTitle(self.parent.GetTournament().Name)
    
    # show the scores
    self.OnDrawScores(None)
    
    # make a timer to refresh the scores at a set interval
    self.timer = wxTimer(self, 0)
    self.timer.Start(wnSettings.scores_timer_refresh_interval)
    EVT_TIMER(self, 0, self.OnDrawScores)
    
  def OnDrawScores(self, event):
    # get the current scores
    scores = self.parent.GetTournament().CalcScores()
    
    # fill the list box with the current scores
    self.scores.DeleteAllItems()
    for i in range(len(scores)):
      score, name = scores[i]
      self.scores.InsertStringItem(i, str(i+1))
      self.scores.SetStringItem(i, 1, name)
      self.scores.SetStringItem(i, 2, str(score))
    
class wnTeamSpellingDialog(wxDialog):
  '''Class that creates a dialog allowing users to change team name spellings.'''
  def __init__(self, parent, team_names):
    wxDialog.__init__(self, parent, -1, 'Change team spelling')
    GUI.CreateTeamSpellingDialog(self)
    
    # get references
    self.teams = wxPyTypeCast(self.FindWindowById(GUI.ID_TEAMS_CHOICE), 'wxChoice')
    self.name = wxPyTypeCast(self.FindWindowById(GUI.ID_NAME_TEXT), 'wxTextCtrl')
    
    # fill the choice box
    for name in team_names:
      self.teams.Append(name)
    self.teams.SetSelection(0)
    
    EVT_BUTTON(self, wxID_OK, self.OnOK)
  
  def OnOK(self, event):
    #make sure the team name change is valid
    if self.name.GetValue() == '':
      self.EndModal(wxID_CANCEL)
    else:
      self.EndModal(wxID_OK)
      
  def GetNewName(self):
    return self.name.GetValue()[0:wnSettings.max_team_length]
  
  def GetOldName(self):
    return self.teams.GetStringSelection()  
  
class wnWrestlerSpellingDialog(wxDialog):
  '''Class that creates a dialog allowing users to change wrestler name spellings.'''
  def __init__(self, parent, teams):
    wxDialog.__init__(self, parent, -1, 'Change wrestler spelling')
    GUI.CreateWrestlerSpellingDialog(self)
    
    # get references
    self.teams = wxPyTypeCast(self.FindWindowById(GUI.ID_TEAMS_CHOICE), 'wxChoice')
    self.wrestlers = wxPyTypeCast(self.FindWindowById(GUI.ID_WRESTLERS_CHOICE), 'wxChoice')
    self.name = wxPyTypeCast(self.FindWindowById(GUI.ID_NAME_TEXT), 'wxTextCtrl')
    self.team_objs = teams
    
    # fill the team choice box
    team_names = self.team_objs.keys()
    team_names.sort()
    for t in team_names:
      self.teams.Append(t)
    self.teams.SetSelection(0)
    
    # fill the wrestler choice box
    t = self.team_objs[self.teams.GetString(0)]
    for w in t.Wrestlers:
      self.wrestlers.Append(w.Name)
    self.wrestlers.SetSelection(0)
    
    EVT_CHOICE(self, GUI.ID_TEAMS_CHOICE, self.OnChangeTeam)
    EVT_BUTTON(self, wxID_OK, self.OnOK)
    
  def OnChangeTeam(self, event):
    self.wrestlers.Clear()
    t = self.team_objs[self.teams.GetStringSelection()]
    for w in t.Wrestlers:
      self.wrestlers.Append(w.Name)
    self.wrestlers.SetSelection(0)
  
  def OnOK(self, event):
    #make sure the team name change is valid
    if self.name.GetValue() == '':
      self.EndModal(wxID_CANCEL)
    else:
      self.EndModal(wxID_OK)
      
  def GetTeamName(self):
    return self.teams.GetStringSelection()
  
  def GetOldName(self):
    return self.wrestlers.GetStringSelection()  
      
  def GetNewName(self):
    return self.name.GetValue()[0:wnSettings.max_team_length]
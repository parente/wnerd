from wxPython.wx import *
from wxPython.wizard import *
from wxPython.lib.scrolledpanel import wxScrolledPanel
from wnBuilder import *
from wnRenderer import *
import WrestlingNerd_wdr as GUI
import cPickle

class wnFrame(wxFrame):
  '''Class that creates and manages the main WN window.'''
  
  def __init__(self):
    '''Initialize.
    '''
    wxFrame.__init__(self, None, -1, 'Wrestling Nerd',
                     style=wxDEFAULT_FRAME_STYLE|wxNO_FULL_REPAINT_ON_RESIZE)
  
    #set the menu bar
    mb = GUI.CreateMenuBar()
    self.SetMenuBar(mb)
    
    #correct the background color
    self.SetBackgroundColour(mb.GetBackgroundColour())
    
    #create a sizer to layout the window
    sizer = wxFlexGridSizer(1,3,0,0)
    sizer.AddGrowableCol(0)
    sizer.AddGrowableRow(0)
  
    #create a bracket canvas
    self.canvas = wnBracketCanvas(self)
    sizer.AddWindow(self.canvas, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxLEFT|wxRIGHT|wxBOTTOM|wxTOP, 5)
    
    #draw a separator
    line = wxStaticLine(self, -1, size=wxSize(1,-1), style=wxLI_VERTICAL)
    sizer.AddWindow(line, 0, wxGROW, 5)

    #create a frame housing the layer components
    score_frame = GUI.ScoreFrame(self, False, False)
    sizer.AddSizer(score_frame, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxLEFT|wxRIGHT|wxBOTTOM|wxTOP, 5)
    
    #add the sizer to the window
    self.SetSizer(sizer)
    
    #create class variables
    self.tournament = None
    self.filename = None
    self.weights = wxPyTypeCast(self.FindWindowById(GUI.ID_WEIGHTS_CHOICE), 'wxChoice')
    self.teams = wxPyTypeCast(self.FindWindowById(GUI.ID_TEAMS_LIST), 'wxListCtrl')
    
    #set up the list control
    self.teams.InsertColumn(0, 'Team', width=-2)
    self.teams.InsertColumn(1, 'Score', width=-2)

    #disable menu items
    self.ChangeMenuState('on start')
    
    EVT_CLOSE(self, self.OnClose)
    EVT_MENU(self, GUI.ID_EXIT_MENU, self.OnClose)
    EVT_MENU(self, GUI.ID_NEW_MENU, self.OnNew)
    EVT_MENU(self, GUI.ID_SAVE_MENU, self.OnSave)
    EVT_MENU(self, GUI.ID_OPEN_MENU, self.OnOpen)
    
    EVT_CHOICE(self, GUI.ID_WEIGHTS_CHOICE, self.OnSelectWeight)
    
  def OnClose(self, event):
    '''Handle a window close event.'''
    self.canvas.Destroy()
    self.Destroy()
    
  def OnNew(self, event):
    '''Show the new tournament wizard.'''
    builder = wnBuilder()
    
    wiz = wnNewTournamentWizard(self)
    wiz.SetAvailableLayouts(builder.GetTournaments())
    if wiz.RunWizard():
      name = wiz.GetName()
      weights = wiz.GetWeights()
      teams = wiz.GetTeams()
      layout = wiz.GetLayout()
        
      #create the tournament
      self.tournament = builder.Create(layout, name, weights, teams)
      
      #reset the GUI
      self.ResetAfterNew()
      
  def OnSave(self, event):
    '''Save the current tournament to disk by pickling it.'''
    dlg = wxFileDialog(self, 'Save tournament', wildcard='Wrestling Nerd files (*.wnd)|*.wnd',
                       style=wxSAVE|wxOVERWRITE_PROMPT)
    
    if dlg.ShowModal() == wxID_OK:
      f = file(dlg.GetPath(), 'wb')
      cPickle.dump(self.tournament, f, True)
      f.close()
      self.ChangeMenuState('on save')
      
  def OnOpen(self, event):
    '''Open a tournament from disk.'''
    dlg = wxFileDialog(self, 'Open tournament', wildcard='Wrestling Nerd files (*.wnd)|*.wnd',
                       style=wxOPEN|wxHIDE_READONLY)
    
    if dlg.ShowModal() == wxID_OK:
      f = file(dlg.GetPath(), 'rb')
      self.tournament = cPickle.load(f)
      f.close()
      self.ResetAfterNew()
      
  def OnSelectWeight(self, event):
    '''Refresh the canvas to show the new weight.'''
    self.canvas.Refresh()
    
  def GetTournament(self):
    return self.tournament
  
  def GetCurrentWeight(self):
    if self.weights.GetSelection() == -1:
      return None
    else:
      return self.weights.GetStringSelection()
    
  def RefreshScores(self):
    '''Refresh the team scores.'''
    scores = self.tournament.GetScores()
    #scores = {'Bristol Central' : 100.5, 'Bristol Eastern' : 0}
    items = scores.items()
    self.teams.DeleteAllItems()
    for i in range(len(items)):
      name, score = items[i]
      #print i, name, score
      self.teams.InsertStringItem(i, name)
      self.teams.SetStringItem(i, 1, str(score))
      
  def ResetAfterNew(self):
    '''Reset the GUI after a tournament has been created or opened.'''
      
    self.weights.Clear()
    #add the weights to the weight drop-down
    for w in self.tournament.Weights:
      self.weights.Append(w)
    self.weights.SetSelection(0)
    
    #add the teams to the team list
    self.RefreshScores()
    
    #change menu item state
    self.ChangeMenuState('on new')
    
    #draw the bracket
    self.canvas.Refresh()
      
  def ChangeMenuState(self, action):
    mb = self.GetMenuBar()
    if action == 'on start':
      mb.FindItemById(GUI.ID_FASTFALL_MENU).Enable(False)
      mb.FindItemById(GUI.ID_NUMBOUTS_MENU).Enable(False)
      mb.FindItemById(GUI.ID_SAVE_MENU).Enable(False)
      mb.FindItemById(GUI.ID_SAVEAS_MENU).Enable(False)
    
    elif action == 'on new':
      mb.FindItemById(GUI.ID_FASTFALL_MENU).Enable(True)
      mb.FindItemById(GUI.ID_NUMBOUTS_MENU).Enable(True)
      mb.FindItemById(GUI.ID_SAVE_MENU).Enable(True)      
      mb.FindItemById(GUI.ID_SAVEAS_MENU).Enable(False)
      
    elif action == 'on save':
      mb.FindItemById(GUI.ID_SAVEAS_MENU).Enable(True)

    
class wnBracketCanvas(wxScrolledWindow):
  def __init__(self, parent):
    wxScrolledWindow.__init__(self, parent, -1)
    self.parent = parent
    self.painter = wnPainter(self)
    
    EVT_PAINT(self, self.OnPaint)
    
  def OnPaint(self, event):
    dc = wxPaintDC(self)
    self.PrepareDC(dc)
    dc.BeginDrawing()

    t = self.parent.GetTournament()
    w = self.parent.GetCurrentWeight()
    if t is not None and w is not None:
      self.painter.SetDC(dc)
      xmax, ymax = t.Paint(self.painter, w)
      self.painter.SetDC(None)
      
      self.SetVirtualSize(wxSize(xmax, ymax))
      self.SetScrollRate(5,5)      

    dc.EndDrawing()
    
class wnNewTournamentWizard(wxWizard):
  '''Class that creates a wizard that assists users in setting up new
  tournaments.'''
  
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
    self.teams.Append(t)
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
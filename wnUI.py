from wxPython.wx import *
from wxPython.wizard import *
from wxPython.lib.scrolledpanel import wxScrolledPanel
from wnFactory import *
from wnRenderer import *
import WrestlingNerd_wdr as GUI

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
    sizer = wxFlexGridSizer(1,2,0,0)
    sizer.AddGrowableCol(0)
    sizer.AddGrowableRow(0)
  
    #create an OpenGL canvas
    self.canvas = wnBracketCanvas(self)
    sizer.AddWindow(self.canvas, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxLEFT|wxRIGHT|wxBOTTOM|wxTOP, 5)

    #create a frame housing the layer components
    score_frame = GUI.ScoreFrame(self, False, False)
    sizer.AddSizer(score_frame, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxLEFT|wxRIGHT|wxBOTTOM|wxTOP, 5)
    
    #add the sizer to the window
    self.SetSizer(sizer)    
    
    self.tournament = None

    #disable menu items
    mb.FindItemById(GUI.ID_FASTFALL_MENU).Enable(False)
    mb.FindItemById(GUI.ID_NUMBOUTS_MENU).Enable(False)
    mb.FindItemById(GUI.ID_SAVE_MENU).Enable(False)
    mb.FindItemById(GUI.ID_SAVEAS_MENU).Enable(False)
    
    EVT_CLOSE(self, self.OnClose)
    EVT_MENU(self, GUI.ID_EXIT_MENU, self.OnClose)
    EVT_MENU(self, GUI.ID_NEW_MENU, self.OnNew)
    
  def OnClose(self, event):
    '''Handle a window close event.'''
    self.canvas.Destroy()
    self.Destroy()
    
  def OnNew(self, event):
    '''Show the new tournament wizard.'''
    factory = wnFactory()
    
    wiz = wnNewTournamentWizard(self)
    wiz.SetAvailableLayouts(factory.GetTournaments())
    if wiz.RunWizard():
      name = wiz.GetName()
      weights = wiz.GetWeights()
      teams = wiz.GetTeams()
      layout = wiz.GetLayout()
    
      self.tournament = factory.Create(layout, name, weights, teams)
      self.canvas.Refresh()
    
  def GetTournament(self):
    return self.tournament

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
    if t is not None:
      self.painter.SetDC(dc)
      xmax, ymax = t.Paint(self.painter, '103')
      self.painter.SetDC(None)
      
      self.SetVirtualSize(wxSize(xmax, ymax))
      self.SetScrollRate(5,5)      

    dc.EndDrawing()
    

class wnNewTournamentWizard(wxWizard):
  '''Class that creates a wizard that assists users in setting up new
  tournaments.'''
  
  def __init__(self, parent):
    '''Initialize.
    
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
        
    #set event handlers
    EVT_BUTTON(self, GUI.ID_ADD_TEAM, self.OnAddTeam)
    EVT_BUTTON(self, GUI.ID_REMOVE_TEAM, self.OnRemoveTeam)
    EVT_BUTTON(self, GUI.ID_ADD_WEIGHT, self.OnAddWeight)
    EVT_BUTTON(self, GUI.ID_REMOVE_WEIGHT, self.OnRemoveWeight)
    EVT_BUTTON(self, GUI.ID_ADD_STANDARD_WEIGHTS, self.OnAddStandardWeights)    
    EVT_WIZARD_PAGE_CHANGED(self, self.GetId(), self.OnPageChanged)
    
  def OnPageChanged(self, event):
    '''Change the accelerator table appropriately.'''
    if event.GetPage() == self.teams_page:
      table = wxAcceleratorTable([(wxACCEL_CTRL, WXK_RETURN, GUI.ID_ADD_TEAM)])
    else:
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
    
if __name__ == '__main__':
  app = wxPySimpleApp(0)
  frame = wnFrame()
  frame.Centre()
  app.SetTopWindow(frame)
  frame.Show()  
  app.MainLoop()
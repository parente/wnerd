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
    self.canvas = wnBracketPanel(self)
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
    #wiz = wnNewTournamentWizard(self)
    #wiz.RunWizard()
    factory = wnFactory()
    options = factory.GetTournaments()
    self.tournament = factory.Create(options[0], 'Test Tournament',
                                     [95,103,112], ['BC', 'BE', 'WI'])
    self.canvas.Refresh()
    
  def GetTournament(self):
    return self.tournament

class wnBracketPanel(wxScrolledPanel):
  def __init__(self, parent):
    wxScrolledPanel.__init__(self, parent, -1)
    self.parent = parent
    self.painter = wnPainter(self)
    
    EVT_PAINT(self, self.OnPaint)
    
  def OnPaint(self, event):
    dc = wxPaintDC(self)
    dc.BeginDrawing()

    self.painter.SetDC(dc)
    t = self.parent.GetTournament()
    if t is not None:
      t.Paint(self.painter, '103')

    self.painter.SetDC(None)
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
    self.start = wxWizardPageSimple(self)
    GUI.WizardStartPanel(self.start)
    name  = wxWizardPageSimple(self)
    GUI.WizardNamePanel(name)
    teams = wxWizardPageSimple(self)
    GUI.WizardTeamsPanel(teams)
    weights = wxWizardPageSimple(self)
    GUI.WizardWeightsPanel(weights)
    layout = wxWizardPageSimple(self)
    GUI.WizardLayoutPanel(layout)
    finished = wxWizardPageSimple(self)
    GUI.WizardFinishedPanel(finished)
    
    #order the pages
    wxWizardPageSimple_Chain(self.start, name)
    wxWizardPageSimple_Chain(name, teams)
    wxWizardPageSimple_Chain(teams, weights)
    wxWizardPageSimple_Chain(weights, layout)
    wxWizardPageSimple_Chain(layout, finished)
    
    #size the wizard appropriately
    self.FitToPage(self.start)
    
  def RunWizard(self):
    '''Override the run method to automatically use the first page.'''
    wxWizard.RunWizard(self, self.start)
    
if __name__ == '__main__':
  app = wxPySimpleApp(0)
  frame = wnFrame()
  frame.Centre()
  app.SetTopWindow(frame)
  frame.Show()  
  app.MainLoop()
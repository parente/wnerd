from wxPython.wx import *
from wxPython.wizard import *
import WrestlingNerd_wdr as GUI

class wnUI(wxFrame):
  '''Class that creates and manages the main WN window.'''
  
  def __init__(self):
    '''Initialize.
    '''
    wxFrame.__init__(self, None, -1, 'Wrestling Nerd')
    
    #set the menu bar
    mb = GUI.CreateMenuBar()
    self.SetMenuBar(mb)
    
    mb.FindItemById(GUI.ID_FASTFALL_MENU).Enable(False)
    mb.FindItemById(GUI.ID_NUMBOUTS_MENU).Enable(False)
    mb.FindItemById(GUI.ID_SAVE_MENU).Enable(False)
    mb.FindItemById(GUI.ID_SAVEAS_MENU).Enable(False)
    
    EVT_MENU(self, GUI.ID_EXIT_MENU, self.OnClose)
    EVT_MENU(self, GUI.ID_NEW_MENU, self.OnNew)
    
  def OnClose(self, event):
    '''Handle a window close event.'''
    self.Destroy()
    
  def OnNew(self, event):
    '''Show the new tournament wizard.'''
    wiz = wnNewTournamentWizard(self)
    wiz.RunWizard()
  
  
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
  frame = wnUI()
  app.SetTopWindow(frame)
  frame.Show()  
  app.MainLoop()
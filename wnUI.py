'''
The UI module defines classes that present the major user interface components to the user including
the main frame, the bracket canvas, and the side panel.
'''
import wx
import wx.wizard
from wnBuilder import *
from wnRenderer import *
from wnPrinting import *
from wnExport import *
import WrestlingNerd_wdr as GUI
import wnSettings
import cPickle

class wnFrame(wx.Frame):
  '''Class that creates and manages the main WN window.'''
  
  def __init__(self):
    '''Initialize the frame.'''
    wx.Frame.__init__(self, None, -1, 'Wrestling Nerd', size=wx.Size(700,500),
                     style=wx.DEFAULT_FRAME_STYLE|wx.NO_FULL_REPAINT_ON_RESIZE|wx.CLIP_CHILDREN)
  
    #set the menu bar
    mb = GUI.CreateMenuBar()
    self.SetMenuBar(mb)
    
    #correct the background color
    self.SetBackgroundColour(mb.GetBackgroundColour())
    self.SetIcon(wx.Icon(wnSettings.icon_filename, wx.BITMAP_TYPE_ICO))
    
    #create a sizer to layout the window
    sizer = wx.FlexGridSizer(1,2,0,0)
    sizer.AddGrowableCol(0)
    sizer.AddGrowableRow(0)
  
    #create a bracket canvas
    self.canvas = wnBracketCanvas(self)
    sizer.Add(self.canvas, 0, 
              wx.FIXED_MINSIZE|wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.TOP, 5)
    
    #create a frame housing the layer components
    panel = wx.Panel(self, -1)
    score_frame = GUI.CreateSidePanel(panel)
    sizer.Add(panel, 0, wx.FIXED_MINSIZE|wx.GROW, 5)
    
    #add the sizer to the window
    self.SetSizer(sizer)
    
    #create class variables
    self.tournament = None
    self.filename = None
    self.weights = self.FindWindowById(GUI.ID_WEIGHTS_CHOICE)
    self.teams = self.FindWindowById(GUI.ID_TEAMS_LIST)
    
    #make a painter object
    self.painter = wnPainter(self, self.canvas)
    
    #set up the list control
    self.teams.InsertColumn(0, 'Team', width=-2)
    self.teams.InsertColumn(1, 'Score', width=-2)

    #disable menu items
    self.ChangeMenuState('on start')
    
    wx.EVT_CLOSE(self, self.OnClose)
    wx.EVT_MENU(self, GUI.ID_EXIT_MENU, self.OnClose)
    wx.EVT_MENU(self, GUI.ID_NEW_MENU, self.OnNew)
    wx.EVT_MENU(self, GUI.ID_SAVE_MENU, self.OnSave)
    wx.EVT_MENU(self, GUI.ID_SAVEAS_MENU, self.OnSaveAs)
    wx.EVT_MENU(self, GUI.ID_BACKUP_MENU, self.OnBackup)
    wx.EVT_MENU(self, GUI.ID_EXPORT_MENU, self.OnExport)
    wx.EVT_MENU(self, GUI.ID_OPEN_MENU, self.OnOpen)
    wx.EVT_MENU(self, GUI.ID_PRINT_MENU, self.OnPrint)
    wx.EVT_MENU(self, GUI.ID_PRINTPREVIEW_MENU, self.OnPrintPreview)
    wx.EVT_MENU(self, GUI.ID_NUMBOUTS_MENU, self.OnCountBouts)
    wx.EVT_MENU(self, GUI.ID_FASTFALL_MENU, self.OnFastFall)
    wx.EVT_MENU(self, GUI.ID_SCOREWIN_MENU, self.OnScoreWindow)
    wx.EVT_MENU(self, GUI.ID_ADDTEAM_MENU, self.OnAddTeam)
    wx.EVT_MENU(self, GUI.ID_REMOVETEAM_MENU, self.OnRemoveTeam)
    wx.EVT_MENU(self, GUI.ID_TEAMSPELLING_MENU, self.OnChangeTeamSpelling)
    wx.EVT_MENU(self, GUI.ID_WRESTLERSPELLING_MENU, self.OnChangeWrestlerSpelling)
    wx.EVT_MENU(self, GUI.ID_TOURNAMENTNAME_MENU, self.OnChangeTournamentName)
    wx.EVT_MENU(self, GUI.ID_ABOUT_MENU, self.OnAbout)
    wx.EVT_CHOICE(self, GUI.ID_WEIGHTS_CHOICE, self.OnSelectWeight)
    wx.EVT_LIST_ITEM_ACTIVATED(self, GUI.ID_TEAMS_LIST, self.OnSelectTeam)
    
  def OnClose(self, event):
    '''Handle a window close event.'''
    # quit immediately if there is no tournament
    if self.tournament is None:
      self.canvas.Close()
      self.Destroy()
      return
      
    # ask if we want to save before closing
    dlg = wx.MessageDialog(self, 'Do you want to save this tournament before quitting?',
                           'Save tournament',
                           wx.ICON_QUESTION|wx.YES_DEFAULT|wx.YES_NO|wx.CANCEL)
    result = dlg.ShowModal()
    dlg.Destroy()    
    if result == wx.ID_CANCEL:
      # don't quit
      event.Veto()
    elif result == wx.ID_YES:
      if self.OnSave(event):
        # save and quit
        self.canvas.Close()
        self.Destroy()
      else:
        # cancel the save and don't quit
        event.Veto()
    elif result == wx.ID_NO:
      # don't save and quit
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
      return self.OnSaveAs(event)
    else:
      f = file(self.filename, 'wb')
      cPickle.dump(self.tournament, f, True)
      f.close()
      return True

  def OnSaveAs(self, event):
    saved = False
    dlg = wx.FileDialog(self, 'Save tournament', 
                        wildcard='Wrestling Nerd files (*.wnd)|*.wnd',
                        style=wx.SAVE|wx.OVERWRITE_PROMPT)
      
    if dlg.ShowModal() == wx.ID_OK:
      f = file(dlg.GetPath(), 'wb')
      cPickle.dump(self.tournament, f, True)
      f.close()
      self.ChangeMenuState('on save')
      self.filename = dlg.GetPath()
      saved = True
      
    dlg.Destroy()
    return saved
    
  def OnBackup(self, event):
    dlg = wx.FileDialog(self, 'Backup tournament', wildcard='Wrestling Nerd files (*.wnd)|*.wnd',
                         style=wx.SAVE|wx.OVERWRITE_PROMPT)
      
    if dlg.ShowModal() == wx.ID_OK:
      f = file(dlg.GetPath(), 'wb')
      cPickle.dump(self.tournament, f, True)
      f.close()
      
    dlg.Destroy()
      
  def OnOpen(self, event):
    '''Open a tournament from disk.'''
    dlg = wx.FileDialog(self, 'Open tournament', wildcard='Wrestling Nerd files (*.wnd)|*.wnd',
                        style=wx.OPEN|wx.HIDE_READONLY)
    
    if dlg.ShowModal() == wx.ID_OK:
      f = file(dlg.GetPath(), 'rb')
      self.tournament = cPickle.load(f)
      f.close()
      self.ResetAfterNew()
      self.ChangeMenuState('on open')
      self.filename = dlg.GetPath()
      
    dlg.Destroy()
      
  def OnExport(self, event):
    '''Show the export dialog. Right now, only export to plain text.'''
    dlg = wx.FileDialog(self, 'Export plain text', wildcard='Text files (*.txt)|*.txt',
                         style=wx.SAVE|wx.OVERWRITE_PROMPT)
    
    if dlg.ShowModal() == wx.ID_OK:
      exp = wnExportPlainText(dlg.GetPath(), self.tournament)
      exp.Save()
      
    dlg.Destroy()
      
  def OnPrint(self, event):
    '''Show the print dialog box.'''
    dlg = wnPrintDialog(self, self.tournament.Weights,
                        self.tournament.Rounds, self.GetCurrentWeight())
    dlg.CentreOnScreen()
    # if the user wants to print, show the print settings dialog
    if dlg.ShowModal() == wx.ID_OK:
      # use the print factory to do all the printing
      wnPrintFactory.Print(self, self.tournament, dlg.GetType(),
                           dlg.GetWeights(), dlg.GetRounds(), self.canvas.GetBracketSize())
    dlg.Destroy()
    
  def OnPrintPreview(self, event):
    '''Show the print preview dialog box.'''
    dlg = wnPrintDialog(self, self.tournament.Weights,
                        self.tournament.Rounds, self.GetCurrentWeight())
    dlg.CentreOnScreen()
    # if the user wants to print, show the print settings dialog
    if dlg.ShowModal() == wx.ID_OK:
      # use the print factory to do all the printing
      wnPrintFactory.PrintPreview(self, self.tournament, dlg.GetType(),
                                  dlg.GetWeights(), dlg.GetRounds(),
                                  self.canvas.GetBracketSize())
    dlg.Destroy()
    
  def OnCountBouts(self, event):
    '''Count the number of bouts and show the result in a simple dialog.'''
    i = self.tournament.CountBouts()
    
    if i == 1:
      msg = 'There is 1 bout in the tournament.'
    else:
      msg = 'There are ' + str(i) + ' bouts in the tournament.'
    
    dlg = wx.MessageDialog(self, msg, 'Bout count', style=wx.OK)
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
    dlg = wx.TextEntryDialog(self, 'Enter the name of the new team.', 'Add team')
    if dlg.ShowModal() == wx.ID_OK:
      try:
        self.tournament.TeamNames.index(dlg.GetValue())
      except:
        self.tournament.NewTeam(dlg.GetValue())
        self.ResetAfterNew()
      
    dlg.Destroy()
  
  def OnRemoveTeam(self, event):
    #make sure there is more than one team left
    if len(self.tournament.TeamNames) <= 1:
      dlg = wx.MessageDialog(self, 'You cannot delete the last team.', 'One team left')
      dlg.ShowModal()
      dlg.Destroy()
      return
    
    # let the user pick the team to delete
    names = self.tournament.TeamNames
    dlg = wx.SingleChoiceDialog(self, 'Choose the team to delete.', 'Remove team',
                               names)
    if dlg.ShowModal() == wx.ID_OK:
      self.tournament.DeleteTeam(dlg.GetStringSelection())
      self.ResetAfterNew()
      
    dlg.Destroy()
    
  def OnChangeTeamSpelling(self, event):
    '''Show the dialog that allows a user to change the spelling of a team name.'''
    dlg = wnTeamSpellingDialog(self, self.tournament.TeamNames)
    dlg.CentreOnScreen()
    
    if dlg.ShowModal() == wx.ID_OK:
      self.tournament.ChangeTeam(dlg.GetOldName(), dlg.GetNewName())
      self.ResetAfterNew()
        
    dlg.Destroy()
    
  def OnChangeWrestlerSpelling(self, event):
    '''Show the dialog that allows a user to change the spelling of a wrestler name.'''
    dlg = wnWrestlerSpellingDialog(self, self.tournament.Teams)
    dlg.CentreOnScreen()
    
    if dlg.ShowModal() == wx.ID_OK:
      t = self.tournament.Teams[dlg.GetTeamName()]
      t.ChangeWrestler(dlg.GetOldName(), dlg.GetNewName())
      self.canvas.RefreshBracket()
        
    dlg.Destroy()
    
  def OnChangeTournamentName(self, event):
    '''Show a dialog that allows a user to enter a new name for the tournament.'''
    dlg = wx.TextEntryDialog(self, 'Enter a new name for the tournament.',
                            'Change tournament name', self.tournament.Name)
    if dlg.ShowModal() == wx.ID_OK:
      self.tournament.Name = dlg.GetValue()
      self.SetTitle('Wrestling Nerd - '+self.tournament.Name)
    dlg.Destroy()
    
  def OnAbout(self, event):
    '''Show the about window.'''
    dlg = wx.Dialog(self, -1, 'About')
    GUI.CreateAboutDialog(dlg)
    dlg.SetBackgroundColour(wx.WHITE)
    dlg.CentreOnScreen()
    dlg.ShowModal()
    dlg.Destroy()
      
  def OnSelectWeight(self, event):
    '''Refresh the canvas to show the new weight.'''
    self.canvas.RefreshBracket()
    
  def OnSelectTeam(self, event):
    '''Show a dialog box containing properties of a team.'''
    name = event.GetText()
    dlg = wnTeamDialog(self, self.tournament.Teams[name])
    dlg.CentreOnScreen()
    
    # check if the user wants to make changes to the team score
    if dlg.ShowModal() == wx.ID_OK:
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
    self.SetTitle('Wrestling Nerd - '+self.tournament.Name)
        
    #reset and draw the bracket
    self.painter.ResetControls()
    self.canvas.Reset()
    self.canvas.RefreshBracket()
     
  def ChangeMenuState(self, action):
    mb = self.GetMenuBar()
    if action == 'on start':
      mb.FindItemById(GUI.ID_FASTFALL_MENU).Enable(False)
      mb.FindItemById(GUI.ID_NUMBOUTS_MENU).Enable(False)
      mb.FindItemById(GUI.ID_SAVE_MENU).Enable(False)
      mb.FindItemById(GUI.ID_SAVEAS_MENU).Enable(False)
      mb.FindItemById(GUI.ID_BACKUP_MENU).Enable(False)
      mb.FindItemById(GUI.ID_EXPORT_MENU).Enable(False)
      mb.FindItemById(GUI.ID_PRINT_MENU).Enable(False)
      mb.FindItemById(GUI.ID_PRINTPREVIEW_MENU).Enable(False)
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
      mb.FindItemById(GUI.ID_BACKUP_MENU).Enable(False)
      mb.FindItemById(GUI.ID_EXPORT_MENU).Enable(True)
      mb.FindItemById(GUI.ID_PRINT_MENU).Enable(True)
      mb.FindItemById(GUI.ID_PRINTPREVIEW_MENU).Enable(True)
      mb.FindItemById(GUI.ID_SCOREWIN_MENU).Enable(True)
      mb.FindItemById(GUI.ID_ADDTEAM_MENU).Enable(True)
      mb.FindItemById(GUI.ID_REMOVETEAM_MENU).Enable(True)
      mb.FindItemById(GUI.ID_TEAMSPELLING_MENU).Enable(True)
      mb.FindItemById(GUI.ID_WRESTLERSPELLING_MENU).Enable(True)
            
    elif action == 'on open':
      mb.FindItemById(GUI.ID_FASTFALL_MENU).Enable(True)
      mb.FindItemById(GUI.ID_NUMBOUTS_MENU).Enable(True)
      mb.FindItemById(GUI.ID_SAVE_MENU).Enable(True)      
      mb.FindItemById(GUI.ID_SAVEAS_MENU).Enable(True)
      mb.FindItemById(GUI.ID_BACKUP_MENU).Enable(True)
      mb.FindItemById(GUI.ID_EXPORT_MENU).Enable(True)
      mb.FindItemById(GUI.ID_PRINT_MENU).Enable(True)
      mb.FindItemById(GUI.ID_PRINTPREVIEW_MENU).Enable(True)
      mb.FindItemById(GUI.ID_SCOREWIN_MENU).Enable(True)
      mb.FindItemById(GUI.ID_ADDTEAM_MENU).Enable(True)
      mb.FindItemById(GUI.ID_REMOVETEAM_MENU).Enable(True)
      mb.FindItemById(GUI.ID_TEAMSPELLING_MENU).Enable(True)
      mb.FindItemById(GUI.ID_WRESTLERSPELLING_MENU).Enable(True)

    elif action == 'on save':
      mb.FindItemById(GUI.ID_SAVEAS_MENU).Enable(True)
      mb.FindItemById(GUI.ID_BACKUP_MENU).Enable(True)
    
  def GetPainter(self):
    '''Return a reference to the painter object.'''
    return self.painter
  
class wnBracketCanvas(wx.ScrolledWindow):
  def __init__(self, parent):
    wx.ScrolledWindow.__init__(self, parent, -1, style=wx.NO_FULL_REPAINT_ON_RESIZE)
    self.parent = parent
    self.old_weight = None
    self.bracket_size = wx.Size(0,0)
    self.need_refresh = False
    
    wx.EVT_PAINT(self, self.OnPaint)
    
  def Reset(self):
    self.DestroyChildren()
    self.Scroll(0,0)
    self.old_weight = None
    
  def OnPaint(self, event):
    dc = wx.PaintDC(self)
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
      self.bracket_size = wx.Size(xmax, ymax)
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
    
class wnNewTournamentWizard(wx.wizard.Wizard):
  '''Class that creates a wizard that assists users in setting up new tournaments.'''  
  def __init__(self, parent):
    '''Initialize an instance of the wizard.
    
    Params:
    
    'parent': The parent window of the wizard
    '''
    wx.wizard.Wizard.__init__(self, parent, -1, 'New tournament')
    
    #create the pages of the wizard
    self.start_page = wx.wizard.WizardPageSimple(self)
    GUI.WizardStartPanel(self.start_page)
    self.name_page  = wx.wizard.WizardPageSimple(self)
    GUI.WizardNamePanel(self.name_page)
    self.teams_page = wx.wizard.WizardPageSimple(self)
    GUI.WizardTeamsPanel(self.teams_page)
    self.weights_page = wx.wizard.WizardPageSimple(self)
    GUI.WizardWeightsPanel(self.weights_page)
    self.layout_page = wx.wizard.WizardPageSimple(self)
    GUI.WizardLayoutPanel(self.layout_page)
    self.finished_page = wx.wizard.WizardPageSimple(self)
    GUI.WizardFinishedPanel(self.finished_page)
    
    #order the pages
    wx.wizard.WizardPageSimple_Chain(self.start_page, self.name_page)
    wx.wizard.WizardPageSimple_Chain(self.name_page, self.teams_page)
    wx.wizard.WizardPageSimple_Chain(self.teams_page, self.weights_page)
    wx.wizard.WizardPageSimple_Chain(self.weights_page, self.layout_page)
    wx.wizard.WizardPageSimple_Chain(self.layout_page, self.finished_page)
    
    #size the wizard appropriately
    self.FitToPage(self.start_page)
    
    #store important references
    self.teams = self.FindWindowById(GUI.ID_TEAMS_LIST)
    self.teams_entry = self.FindWindowById(GUI.ID_TEAMS_TEXT)
    self.weights = self.FindWindowById(GUI.ID_WEIGHTS_LIST)
    self.weights_entry = self.FindWindowById(GUI.ID_WEIGHTS_TEXT)
    self.layouts = self.FindWindowById(GUI.ID_LAYOUT_LIST)
    self.name = self.FindWindowById(GUI.ID_NAME_TEXT)
    self.description = self.FindWindowById(GUI.ID_LAYOUT_TEXT)
    
    #set the captions
    cap = self.FindWindowById(GUI.ID_START_CAPTION)
    cap.SetLabel(GUI.start_caption)
    cap = self.FindWindowById(GUI.ID_NAME_CAPTION)
    cap.SetLabel(GUI.name_caption)
    cap = self.FindWindowById(GUI.ID_TEAMS_CAPTION)
    cap.SetLabel(GUI.teams_caption)
    cap = self.FindWindowById(GUI.ID_WEIGHTS_CAPTION)
    cap.SetLabel(GUI.weights_caption)    
    cap = self.FindWindowById(GUI.ID_LAYOUT_CAPTION)
    cap.SetLabel(GUI.layout_caption)
    cap = self.FindWindowById(GUI.ID_FINISHED_CAPTION)
    cap.SetLabel(GUI.finished_caption)
    
    #set event handlers
    wx.EVT_TEXT_ENTER(self, GUI.ID_WEIGHTS_TEXT, self.OnAddWeight)
    wx.EVT_TEXT_ENTER(self, GUI.ID_TEAMS_TEXT, self.OnAddTeam)
    wx.EVT_BUTTON(self, GUI.ID_ADD_TEAM, self.OnAddTeam)
    wx.EVT_BUTTON(self, GUI.ID_REMOVE_TEAM, self.OnRemoveTeam)
    wx.EVT_BUTTON(self, GUI.ID_ADD_WEIGHT, self.OnAddWeight)
    wx.EVT_BUTTON(self, GUI.ID_REMOVE_WEIGHT, self.OnRemoveWeight)
    wx.EVT_BUTTON(self, GUI.ID_ADD_STANDARD_WEIGHTS, self.OnAddStandardWeights)    
    wx.wizard.EVT_WIZARD_PAGE_CHANGED(self, self.GetId(), self.OnPageChanged)
    wx.wizard.EVT_WIZARD_PAGE_CHANGING(self, self.GetId(), self.OnPageChanging)
    wx.EVT_LISTBOX(self, GUI.ID_LAYOUT_LIST, self.OnSelectLayout)
 
  def OnSelectLayout(self, event):
    '''Show the description of the selected layout.'''
    c = self.layouts.GetClientData(event.GetInt())
    self.description.SetValue(c.Description)
    
  def OnPageChanging(self, event):
    '''Make sure the values are valid.'''
    if event.GetPage() == self.name_page and self.name.GetValue() == '':
      wx.MessageDialog(self, 'You must enter a tournament name.', 'Invalid name', wx.OK).ShowModal()
      event.Veto()
    elif event.GetPage() == self.teams_page and self.teams.GetCount() == 0:
      wx.MessageDialog(self, 'The tournament must have at least one team.', 'No teams',
                      wx.OK).ShowModal()
      event.Veto()
    elif event.GetPage() == self.weights_page and self.weights.GetCount() == 0:
      wx.MessageDialog(self, 'The tournament must have at least one weight class.',
                      'No weight classes', wx.OK).ShowModal()
      event.Veto()
      
  def OnPageChanged(self, event):
    '''Change the accelerator table appropriately.'''
    if event.GetPage() == self.teams_page:
      table = wx.AcceleratorTable([(wx.ACCEL_CTRL, wx.WXK_RETURN, GUI.ID_ADD_TEAM)])
      self.SetAcceleratorTable(table)
    elif event.GetPage() == self.weights_page:
      table = wx.AcceleratorTable([(wx.ACCEL_CTRL, wx.WXK_RETURN, GUI.ID_ADD_WEIGHT)])
      self.SetAcceleratorTable(table)
    else:
      self.SetAcceleratorTable(wx.NullAcceleratorTable)
                            
  def OnAddTeam(self, event):
    t = self.teams_entry.GetValue()[0:wnSettings.max_team_length]
    if self.teams.FindString(t) != -1 or t == '': return
    self.teams.Append(t)
    self.teams_entry.SetValue('')
  
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
    w = self.weights_entry.GetValue()
    if self.weights.FindString(w) != -1 or w == '': return
    self.weights.Append(w)
    self.weights_entry.SetValue('')
    
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
    return wx.wizard.Wizard.RunWizard(self, self.start_page)
    
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

class wnPrintDialog(wx.Dialog):
  '''Class that creates a dialog box that allows users to select what to print.'''
  def __init__(self, parent, weights, rounds, current_weight):
    wx.Dialog.__init__(self, parent, -1, 'Print')
    GUI.CreatePrintDialog(self)
    
    # store references
    self.weights = self.FindWindowById(GUI.ID_WEIGHTS_LIST)
    self.rounds = self.FindWindowById(GUI.ID_ROUNDS_LIST)
    self.type = self.FindWindowById(GUI.ID_TYPE_RADIOBOX)
    
    # fill the list boxes and set initial selections
    self.weights.Set(weights)
    self.rounds.Set(rounds)
    self.weights.SetStringSelection(current_weight)
    self.rounds.SetSelection(0)
    
    # watch for events to enable or disable the rounds control
    wx.EVT_RADIOBOX(self, GUI.ID_TYPE_RADIOBOX, self.OnTypeChange)
    wx.EVT_BUTTON(self, wx.ID_OK, self.OnOK)
    
  def OnOK(self, event):
    '''Make sure the selections are valid before closing the dialog.'''
    if len(self.weights.GetSelections()) == 0:
      wx.MessageDialog(self, 'You must select at least one weight class.', 
                       'Select a weight class', wx.OK).ShowModal()
      return False
    if self.type.GetStringSelection() == 'B&outs' and len(self.rounds.GetSelections()) == 0:
      wx.MessageDialog(self, 'You must select at least one round to print bouts.', 
                       'Select a round', wx.OK).ShowModal()
      return False
    self.EndModal(wx.ID_OK) 
  
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
  
class wnTeamDialog(wx.Dialog):
  '''Class that creates a dialog box that shows team info.'''
  def __init__(self, parent, team):
    wx.Dialog.__init__(self, parent, -1, 'Team Properties: '+team.Name)
    GUI.CreateTeamDialog(self)
    
    # get important references
    self.pa_text = self.FindWindowById(GUI.ID_POINTADJUST_TEXT)
    self.wrestlers = self.FindWindowById(GUI.ID_WRESTLERS_LIST)
    
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
    wx.EVT_SPIN_UP(self, GUI.ID_POINTADJUST_SPIN, self.OnPointUp)
    wx.EVT_SPIN_DOWN(self, GUI.ID_POINTADJUST_SPIN, self.OnPointDown)
    wx.EVT_BUTTON(self, wx.ID_OK, self.OnOK)
    
  def OnOK(self, event):
    self.team.PointAdjust = float(self.pa_text.GetValue())
    self.EndModal(wx.ID_OK)
    
  def OnPointUp(self, event):
    self.pa_text.SetValue(str(float(self.pa_text.GetValue()) + 0.5))
  
  def OnPointDown(self, event):
    self.pa_text.SetValue(str(float(self.pa_text.GetValue()) - 0.5))
    
class wnFastFallDialog(wx.Dialog):
  '''Class that creates a dialog showing the fastest fall times in descending order.'''
  def __init__(self, parent, table):
    wx.Dialog.__init__(self, parent, -1, 'Fast fall results')
    GUI.CreateFastFallDialog(self)
    
    # get a reference to the results list control
    self.results = self.FindWindowById(GUI.ID_RESULTS_LIST)
    
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

# TODO: make this window scroll or refresh automatically
class wnScoreWindow(wx.Frame):
  '''Class the creates a standalone frame for displaying team scores. Teams scroll past at a regular
  interval. Useful for multi-monitor setups with scores on public display.'''
  def __init__(self, parent):
    wx.Frame.__init__(self, parent, -1, '', size=wx.Size(640, 480),
                     style=wx.DEFAULT_FRAME_STYLE|wx.NO_FULL_REPAINT_ON_RESIZE|wx.CLIP_CHILDREN)
    
    # set up the UI                 
    GUI.CreateScoreFrame(self, False, False)
    self.SetIcon(parent.GetIcon())
        
    # get a reference to the list control
    self.scores = self.FindWindowById(GUI.ID_SCORES_LIST)
    
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
    self.timer = wx.Timer(self, 0)
    self.timer.Start(wnSettings.scores_timer_refresh_interval)
    wx.EVT_TIMER(self, 0, self.OnDrawScores)
    
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
    
class wnTeamSpellingDialog(wx.Dialog):
  '''Class that creates a dialog allowing users to change team name spellings.'''
  def __init__(self, parent, team_names):
    wx.Dialog.__init__(self, parent, -1, 'Change team spelling')
    GUI.CreateTeamSpellingDialog(self)
    
    # get references
    self.teams = self.FindWindowById(GUI.ID_TEAMS_CHOICE)
    self.name = self.FindWindowById(GUI.ID_NAME_TEXT)
    
    # fill the choice box
    for name in team_names:
      self.teams.Append(name)
    self.teams.SetSelection(0)
    
    wx.EVT_BUTTON(self, wx.ID_OK, self.OnOK)
  
  def OnOK(self, event):
    #make sure the team name change is valid
    if self.name.GetValue() == '':
      self.EndModal(wx.ID_CANCEL)
    else:
      self.EndModal(wx.ID_OK)
      
  def GetNewName(self):
    return self.name.GetValue()[0:wnSettings.max_team_length]
  
  def GetOldName(self):
    return self.teams.GetStringSelection()  
  
class wnWrestlerSpellingDialog(wx.Dialog):
  '''Class that creates a dialog allowing users to change wrestler name spellings.'''
  def __init__(self, parent, teams):
    wx.Dialog.__init__(self, parent, -1, 'Change wrestler spelling')
    GUI.CreateWrestlerSpellingDialog(self)
    
    # get references
    self.teams = self.FindWindowById(GUI.ID_TEAMS_CHOICE)
    self.wrestlers = self.FindWindowById(GUI.ID_WRESTLERS_CHOICE)
    self.name = self.FindWindowById(GUI.ID_NAME_TEXT)
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
    
    wx.EVT_CHOICE(self, GUI.ID_TEAMS_CHOICE, self.OnChangeTeam)
    wx.EVT_BUTTON(self, wx.ID_OK, self.OnOK)
    
  def OnChangeTeam(self, event):
    self.wrestlers.Clear()
    t = self.team_objs[self.teams.GetStringSelection()]
    for w in t.Wrestlers:
      self.wrestlers.Append(w.Name)
    self.wrestlers.SetSelection(0)
  
  def OnOK(self, event):
    #make sure the team name change is valid
    if self.name.GetValue() == '':
      self.EndModal(wx.ID_CANCEL)
    else:
      self.EndModal(wx.ID_OK)
      
  def GetTeamName(self):
    return self.teams.GetStringSelection()
  
  def GetOldName(self):
    return self.wrestlers.GetStringSelection()  
      
  def GetNewName(self):
    return self.name.GetValue()[0:wnSettings.max_team_length]
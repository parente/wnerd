'''
The bracket data module defines the classes that store information about an entire tournament. The
classes define the weight classes, rounds, seeds, and matches of the tournament. These objects are
responsible for rendering themselves and responding to events using renderers provided at run time.
'''
from wnEvents import wnMouseEventReceivable, wnFocusEventReceivable
from wnScoreData import *
from wnTeamData import *
import wnSettings

class wnNode(object):
  '''The node class provides navigation from child nodes to parent nodes.'''
  def __init__(self, parent):
    self.parent = parent
    
  def GetParent(self):
    return self.parent
  
  Parent = property(fget=GetParent)

class wnTournament(wnNode):
  '''The tournament class is responsible for holding weight classes and teams.'''
  def __init__(self, name, seeds):
    wnNode.__init__(self, None)
    self.name = name
    self.seeds = seeds
    self.teams = {}
    self.weight_classes = {}
        
  def NewWeightClass(self, name):
    wc = wnWeightClass(str(name), self)
    self.weight_classes[str(name)] = wc
    
    return wc
  
  def NewTeam(self, name):
    t = wnTeam(str(name))
    t.tournament = self
    self.teams[str(name)] = t
    
    return t

 
  def GetWeightClass(self, name):
    return self.weight_classes.get(name)
  
  def Paint(self, painter, weight, refresh_labels):
    '''Draw the specified weight class to the screen. Pass the provided painter object to the
    weight class being drawn. Draw the seed numbers in the given order first.
    '''
    
    #make sure the weight exists first
    try:
      wc = self.weight_classes[weight]
    except:
      return
      
    result = wc.Paint(painter, (0, wnSettings.seed_start), wnSettings.initial_step, refresh_labels)    
      
    return result
  
  def CalcScores(self, painter):
    '''Calculate all the scores across this tournament.'''
    #for now, just return zero always
    scores = []
    for k in self.teams.keys():
      scores.append((k, 0.0))
        
    painter.DrawTeamScores(scores)

  def GetWeights(self):
    '''Return a list of all the weight classes in ascending order.'''
    k = self.weight_classes.keys()
    k.sort()
    return k
  
  def GetTeams(self):
    return self.teams
  
  def GetName(self):
    '''Return the tournament name.'''
    return self.name
  
  Weights = property(fget=GetWeights)
  Teams = property(fget=GetTeams)
  Name = property(fget=GetName)
  
class wnWeightClass(wnNode):
  '''The weight class is responsible for holding rounds.'''
  def __init__(self, name, parent):
    wnNode.__init__(self, parent)    
    self.name = name
    self.rounds = {}
    self.order = []
    
    #self.tournament = tournament
    
  def NewRound(self, name, points):
    r = wnRound(str(name), points, self)
    self.rounds[str(name)] = r
    self.order.append(str(name))
    
    return r
  
  def GetRound(self, name):
    return self.rounds.get(name)
  
  def Paint(self, painter, start, initial_step, refresh_labels):
    '''Go through all of the rounds and draw their bracket lines.'''

    step = initial_step
    max_x = 0
    max_y = 0
    
    #go through all the rounds in this weight class
    for i in range(len(self.order)):
      #get the current round, and the number of entries in the previous and next rounds if they
      #exist
      curr = self.rounds[self.order[i]]
      try:
        next_num = self.rounds[self.order[i+1]].NumEntries
      except:
        next_num = 0
        
      if i != 0:
        prev_num = self.rounds[self.order[i-1]].NumEntries
      else:
        prev_num = 1e300
        
      #if this round has fewer entries than the previous, reset drawing to the left side of the
      #bracket window, but below the first entry
      if curr.NumEntries > prev_num:
        step = initial_step
        start = (0, max_y+step*2)
        
      #make the outermost lines long to fit a full name and team name
      if i == 0:
        length = wnSettings.seed_length
      else:
        length = wnSettings.entry_length

      start, mx, my = curr.Paint(painter, start, length, step, refresh_labels)
      
      if curr.NumEntries != next_num:
        step *= 2
     
      max_x = max(mx, max_x)
      max_y = max(my, max_y)
      
    return max_x, max_y+initial_step
  
class wnRound(wnNode):
  '''The round class is responsible for holding onto individual matches and their results.'''
  def __init__(self, name, points, parent):
    wnNode.__init__(self, parent)
    self.name = name
    self.points = points    
    self.entries = []
    self.next_win = None
    self.next_lose = None
    
    #self.weight_class = weight_class
    
  def GetNumberOfEntries(self):
    return len(self.entries)
  
  def GetEntries(self):
    return self.entries
  
  def GetName(self):
    return self.name
  
  NumEntries = property(fget=GetNumberOfEntries)
  Entries = property(fget=GetEntries)
  Name = property(fget=GetName)
        
  def NewEntries(self, number):
    #check if we're making new entries based on an order defined in a list
    #if the order is defined, these must be seeds
    if type(number) == list or type(number) == tuple:
      for i in number:
        self.entries.append(wnSeedEntry(i, self))
    
    #otherwise, define them in order
    #if a number is given, these must be matches
    else:
      for i in range(number):
        self.entries.append(wnMatchEntry(i, self))
      
  def SetNextWinRound(self, round, to_map):
    if len(to_map) != self.NumEntries:
      raise IndexError('This round (%s) has %d entries and the to_map has %d links.' % (self.name, self.NumEntries, len(to_map)))

    #store the next win round
    self.next_win = round
     
    #link the entries between rounds
    for i in range(self.NumEntries):
      #link the entry in this round to the proper entry in the next round
      self.entries[i].NextWin = round.Entries[to_map[i]]
      
  def SetNextLoseRound(self, round, to_map):
    if len(to_map) != self.NumEntries:
      raise IndexError('The to_map must contain a link for every entry in this round. This round has %d entries and the to_map has %d links.' % (self.NumEntries, len(to_map)))

    #store the next win round
    self.next_lose = round
    
    #link the entries between rounds
    for i in range(self.NumEntries):
      #link the entry in this round to the proper entry in the next round
      self.entries[i].NextLose = round.Entries[to_map[i]]

  def Paint(self, painter, start, length, step, refresh_labels):
    '''Draw the bracket for this round only. Return the next starting position so the next round
    knows where to draw itself.'''
    
    #draw the horizontal lines and entries
    x,y = start
    for i in range(self.NumEntries):
      painter.DrawLine(x,y,x+length,y)
      self.entries[i].Paint(painter, (x,y), length, refresh_labels)
      y += step

    #store the maximum positions so the scrollbars can be set properly
    max_y = y-step
    max_x = x+length
  
    #draw the vertical lines
    x,y = start
    for i in range(0,self.NumEntries-1,2):
      painter.DrawLine(x+length,y,x+length,y+step)
      y += step*2
      
    #compute the next start
    new_start = start[0] + length, start[1] + step/2
    
    return new_start, max_x, max_y
      
class wnEntry(wnNode):
  '''The entry class holds individual match results.'''
  def __init__(self, name, parent):
    wnNode.__init__(self, parent)
    self.name = name
    self.wrestler = None
    self.next_win = None
    self.next_lose = None
    
    #self.round = round
    
  def GetID(self):
    '''Return the ID of this entry. This ID must be exactly the same as the ID of similar entries
    in other weight classes since it is used to construct text controls by the painter. If the ID
    is exactly the same, then the controls can be reused across weight classes.'''
    return (self.name, self.Parent.Name)
  
  def GetNextLose(self):
    return self.next_lose
  
  def SetNextLose(self, entry):
    self.next_lose = entry
    
  def GetNextWin(self):
    return self.next_win
  
  def SetNextWin(self, entry):
    self.next_win = entry
  
  def GetTeams(self):
    '''Get the available teams from the tournament. Encapsulate how we get this data using
    properties.'''
    return self.Parent.Parent.Parent.Teams
  
  def GetWeightClass(self):
    '''Get the weight class of this entry. Encapsulate how we get this data using properties.'''
    return self.Parent.Parent.Name
  
  ID = property(fget=GetID)
  NextLose = property(fget=GetNextLose, fset=SetNextLose)
  NextWin = property(fget=GetNextWin, fset=SetNextWin)
  Teams = property(fget=GetTeams)
  WeightClass = property(fget=GetWeightClass)
  
class wnMatchEntry(wnEntry, wnMouseEventReceivable, wnFocusEventReceivable):
  '''The match entry class hold individual match results.'''
  def __init__(self, name, parent):
    wnEntry.__init__(self, name, parent)
    self.result = None
    
  def Paint(self, painter, pos, length, refresh_labels):
    '''Paint all of the text controls.'''
    if self.wrestler is None: text = ''
    else: text = self.wrestler.Name
    
    if refresh_labels:
      painter.DrawMatchTextControl(text,
                                   pos[0]+wnSettings.entry_offset, pos[1]-wnSettings.entry_height,
                                   length-wnSettings.entry_offset*2, wnSettings.entry_height,
                                   self.ID, self)
    
  def OnMouseEnter(self, event):
    '''Show a popup window with the match results if available.'''
    if self.wrestler is not None:
      event.Control.ShowPopup(str(self.result))
      
  def OnMouseLeave(self, event):
    '''Hide the popup window with the match results.'''
    event.Control.HidePopup()
    
  def OnLeftDoubleClick(self, event):
    '''Display the dialog box that allows a user to enter result information, if there is at least
    one wrestler in the preceeding entries.'''
    pass
    
class wnSeedEntry(wnEntry, wnFocusEventReceivable):
  '''The seed entry class holds information about seeded wrestlers.'''
  def __init__(self, name, parent):
    wnEntry.__init__(self, name, parent)
    
  def Paint(self, painter, pos, length, refresh_labels):
    '''Paint all of the text controls.'''
    if self.wrestler is None: text = ''
    else: text = self.wrestler.Name
    
    #draw the seed number
    painter.DrawText(str(self.name), pos[0], pos[1]-wnSettings.seed_height)
 
    #draw the text control
    if refresh_labels:
      #get the available teams from the round->weight->tournament
      teams = self.Teams.keys()
      painter.DrawSeedTextControl(text,
                                  pos[0]+wnSettings.seed_offset, pos[1]-wnSettings.seed_height,
                                  wnSettings.seed_length, wnSettings.seed_height,
                                  teams, self.ID, self)
    
  def OnKillFocus(self, event):
    '''Store the entered value if it is valid. Give the next seed the focus, wrapping around at
    the first and last seeds.'''
    self.updateData(event)
    self.updateFocus(event)
      
  def updateData(self, event):
    '''Figure out what needs to be done to store the wrestler properly.'''
    if event.Control.IsValid() and not event.Control.IsEmpty():
      #get the strings from the control
      w_name, t_name = event.Control.GetValue().split(' | ')
      w_name = w_name.strip()
      t_name = t_name.strip()
      print 'Name:',w_name, 'Team:', t_name
      
  def updateFocus(self, event):
    '''Figure out where the focus should go next.'''
    #give the focus only to seeds, not to match entries
    next_id = event.Painter.GetFocus()
    if next_id is not None:
      #focus on the next entry
      if next_id[1] != self.ID[1]:
        if self.name == 1:
          event.Painter.SetFocus(self.Parent.Entries[1].ID)
        elif self.name == self.Parent.NumEntries:
          event.Painter.SetFocus(self.Parent.Entries[0].ID)


if __name__ == '__main__':
  pass
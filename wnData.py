'''
The data module defines the classes that store tournament data. These objects are also responsible
for rendering themselves using a draw object and a print object.
'''
from wnEvents import wnEventReceivable
import wnSettings

class wnTournament(object):
  '''The tournament class is responsible for holding weight classes and teams.'''
  def __init__(self, name, seeds):
    self.name = name
    self.seeds = seeds
    self.teams = {}
    self.weight_classes = {}
        
  def NewWeightClass(self, name):
    wc = wnWeightClass(str(name), self)
    self.weight_classes[str(name)] = wc
    
    return wc
  
  def NewTeam(self, name):
    t = wnTeam(name)
    t.tournament = self
    self.teams[str(name)] = t
    
    return t

  def GetTeam(self, name):
    return self.teams.get(name)
  
  def GetWeightClass(self, name):
    return self.weight_classes.get(name)
  
  def Paint(self, painter, weight):
    '''Draw the specified weight class to the screen. Pass the provided painter object to the
    weight class being drawn. Draw the seed numbers in the given order first.
    '''
    
    #make sure the weight exists first
    try:
      wc = self.weight_classes[weight]
    except:
      return
    
    #draw the numbers for each seed
    step = 30
    y = 0
    
    for num in self.seeds:
      painter.DrawText(str(num), 0, y)
      y += step
      
    return wc.Paint(painter, (0, wnSettings.initial_step), step)
  
  
  def CalcScores(self, painter):
    '''Calculate all the scores across this tournament.'''
    #for now, just return zero always
    scores = []
    for name in self.teams.keys():
      scores.append((name, 0.0))
        
    painter.DrawTeamScores(scores)

  def GetWeights(self):
    '''Return a list of all the weight classes in ascending order.'''
    k = self.weight_classes.keys()
    k.sort()
    return k
  
  def GetName(self):
    '''Return the tournament name.'''
    return self.name
  
  Weights = property(fget=GetWeights)
  Name = property(fget=GetName)
  
class wnWeightClass(object):
  '''The weight class is responsible for holding rounds.'''
  def __init__(self, name, tournament):
    self.name = name
    self.rounds = {}
    self.order = []
    
    self.tournament = tournament
    
  def NewRound(self, name, points):
    r = wnRound(str(name), points, self)
    self.rounds[str(name)] = r
    self.order.append(str(name))
    
    return r
  
  def GetRound(self, name):
    return self.rounds.get(name)
  
  def Paint(self, painter, start, initial_step):
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
        type = 'dynamic'
      else:
        length = wnSettings.entry_length
        type = 'static'

      start, mx, my = curr.Paint(painter, start, length, step, type)
      
      if curr.NumEntries != next_num:
        step *= 2
     
      max_x = max(mx, max_x)
      max_y = max(my, max_y)
      
    return max_x, max_y+initial_step
  
class wnRound(object):
  '''The round class is responsible for holding onto individual matches and their results.'''
  def __init__(self, name, points, weight_class):
    self.name = name
    self.points = points    
    self.entries = []
    self.next_win = None
    self.next_lose = None
    
    self.weight_class = weight_class
    
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
    for i in range(number):
      self.entries.append(wnEntry(i, self))
      
  def SetNextWinRound(self, round, to_map):
    if len(to_map) != self.NumEntries:
      raise IndexError('This round (%s) has %d entries and the to_map has %d links.' % (self.name, self.NumEntries, len(to_map)))

    #store the next win round
    self.next_win = round
     
    #link the entries between rounds
    for i in range(self.NumEntries):
      #link the entry in this round to the proper entry in the next round
      self.entries[i].next_win = round.Entries[to_map[i]]
      
  def SetNextLoseRound(self, round, to_map):
    if len(to_map) != self.NumEntries:
      raise IndexError('The to_map must contain a link for every entry in this round. This round has %d entries and the to_map has %d links.' % (self.NumEntries, len(to_map)))

    #store the next win round
    self.next_lose = round
    
    #link the entries between rounds
    for i in range(self.NumEntries):
      #link the entry in this round to the proper entry in the next round
      self.entries[i].next_lose = round.Entries[to_map[i]]

  def Paint(self, painter, start, length, step, type):
    '''Draw the bracket for this round only. Return the next starting position so the next round
    knows where to draw itself.'''
    
    #draw the horizontal lines
    x,y = start
    for i in range(self.NumEntries):
      painter.DrawLine(x,y,x+length,y)
      self.entries[i].Paint(painter, (x,y-wnSettings.entry_height), length, type)
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
      
class wnEntry(object, wnEventReceivable):
  '''The entry class holds individual match results.'''
  def __init__(self, name, round):
    self.name = name
    self.wrestler = None
    self.result = None
    self.next_win = None
    self.next_lose = None
    
    self.round = round
    
  def Paint(self, painter, pos, length, type):
    '''Paint all of the text controls, static or editable depending on the given flag.'''
    if type == 'static':
      if self.wrestler is None: text = str(self.name)
      else: text = self.wrestler.Name
      
      painter.DrawStaticTextControl(text, pos[0]+wnSettings.entry_offset, pos[1],
                                    length-wnSettings.entry_offset*2, wnSettings.entry_height,
                                    self.ID, self)
      
    elif type == 'dynamic':
      pass
    
  def OnMouseEnter(self, event):
    '''Highlight the text control under the cursor.'''
    event.Control.Highlight()
    event.Control.ShowPopup('Peter Parente\nBristol Central\nMajor\n15-5')
    event.Control.Refresh()
    
  def OnMouseLeave(self, event):
    '''Unhighlight the control under the cursor.'''
    event.Control.Unhighlight()
    event.Control.HidePopup()
    event.Control.Refresh()
    
  def OnLeftDoubleClick(self, event):
    '''Display the dialog box that allows a user to enter result information, if there is at least
    one wrestler in the preceeding entries.'''
    
    
  def GetID(self):
    '''Return the ID of this entry. This ID must be exactly the same as the ID of similar entries
    in other weight classes since it is used to construct text controls by the painter. If the ID
    is exactly the same, then the controls can be reused across weight classes.'''
    return (self.name, self.round.Name)
  
  ID = property(fget=GetID)
    
class wnPoints(object):
  def __init__(self, adv_pts=0, place_pts=0):
    self.adv_points = adv_pts
    self.place_pts = place_pts
  
class wnResult(object):
  '''The result class holds a reference to its entry.'''
  def __init__(self):
    self.entry = None
    
class wnResultPin(wnResult):
  '''This class holds information about a pin win.'''
  def __init__(self):
    wnResult.__init__(self)
    self.pin_time = 0

class wnResultDecision(wnResult):
  '''This class holds information about a decision.'''
  def __init__(self):
    wnResult.__init__(self)    
    self.win_score = 0
    self.lose_score = 0
    
class wnResultBye(wnResult):
  '''This class holds information about a bye.'''
  def __init__(self):
    wnResult.__init__(self)
    
class wnResultDefault(wnResult):
  '''This class holds information about a default win.'''
  def __init__(self):
    wnResult.__init__(self)    
  
class wnTeam(object):
  '''The team class holds wrestlers and points.'''
  def __init__(self, name):
    self.name = name    
    self.wrestlers = {}
    self.point_adjust = 0
    
    self.tournament = None
    
  def NewWrestler(self, name, weight):
    w = wnWrestler(str(name), str(weight))
    w.team = self
    self.wrestlers[str(weight)] = w
    
    return w
      
class wnWrestler(object):
  '''The wrestler class holds information about individuals in a tournament.'''
  def __init__(self):
    self.name = ''
    self.weight = ''
    self.is_scoring = True
    
    self.team = None
    
  def GetName(self):
    return self.name
  
  Name = property(fget=GetName)
    
if __name__ == '__main__':
  pass
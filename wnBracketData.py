'''
The bracket data module defines the classes that store information about an entire tournament. The
classes define the weight classes, rounds, seeds, and matches of the tournament. These objects are
responsible for rendering themselves and responding to events using renderers provided at run time.
'''
from wnEvents import wnMouseEventReceivable, wnFocusEventReceivable, wnMatchMenuReceivable, \
  wnSeedMenuReceivable
from wnScoreData import *
from wnTeamData import *
from wnTempData import *
import wnSettings

class wnNode(object):
  '''The node class provides navigation from child nodes to parent nodes.'''
  def __init__(self, parent, name):
    self.parent = parent
    self.name = name
    
  def GetParent(self):
    return self.parent
  
  def GetName(self):
    return self.name
  
  Name = property(fget=GetName)
  Parent = property(fget=GetParent)

class wnTournament(wnNode):
  '''The tournament class is responsible for holding weight classes and teams.'''
  def __init__(self, name, seeds):
    wnNode.__init__(self, None, name)
    self.seeds = seeds
    self.teams = {}
    self.weight_classes = {}
        
  def NewWeightClass(self, name):
    wc = wnWeightClass(name, self)
    self.weight_classes[name] = wc
    
    return wc
  
  def NewTeam(self, name):
    t = wnTeam(name, self)
    self.teams[name] = t
    
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
  
  def CalcScores(self, weight=None):
    '''Calculate all the scores across this tournament.'''
    # try to get the weight class that should be updated
    wc = self.weight_classes.get(weight)
    
    if wc is not None:
      # tell the current weight class to compute its scores
      scores = wc.CalcScores()
      for t in self.teams.keys():
        self.teams[t].SetWeightScore(weight, scores.get(t) or 0.0)

    # compute the total scores
    score_table = []
    for t in self.teams.keys():      
      score_table.append((self.teams[t].Score, t))
    
    # return for display in descending order
    score_table.sort()
    score_table.reverse()
    return score_table
  
  def CalcFastFall(self):
    '''Compute the fast fall results over all teams and their wrestlers.'''
    results = []
    for t in self.teams.values():
      results += t.CalcFastFall()
      
    # the fast fall objects know how to sort by pin and time
    results.sort()
    
    return results
  
  def GetBouts(self, weights, rounds):
    '''Return a list of all the bouts for the given weights and rounds.'''
    bouts = []
    
    # ask each weight class to compute the bouts for its rounds
    for w in weights:
      try:
        wc = self.weight_classes[w]
      except:
        continue
      bouts += wc.GetBouts(rounds)
      
    return bouts
  
  def GetPlaceWinners(self, weights):
    '''Return a list of all the place winners for the given weights.'''
    places = []
    
    # ask each weight class to compute its placewinners
    for w in weights:
      try:
        wc = self.weight_classes[w]
      except:
        continue
      places.append(wc.GetPlaceWinners())
      
    return places
    
  def CountBouts(self):
    '''Get a count of the total number of bouts.'''
    i = 0
    for w in self.weight_classes.values():
      i += w.CountBouts()
      
    return i

  def GetWeights(self):
    '''Return a list of all the weight classes in ascending order.'''
    k = self.weight_classes.keys()
    k.sort()
    return k
  
  def GetTeams(self):
    return self.teams
  
  def GetRoundNames(self):
    return self.weight_classes.values()[0].Rounds
  
  Weights = property(fget=GetWeights)
  Teams = property(fget=GetTeams)
  Rounds = property(fget=GetRoundNames)
  
class wnWeightClass(wnNode):
  '''The weight class is responsible for holding rounds.'''
  def __init__(self, name, parent):
    wnNode.__init__(self, parent, name)    
    self.rounds = {}
    self.order = []
    
  def NewRound(self, name, points):
    r = wnRound(name, points, self)
    self.rounds[name] = r
    self.order.append(name)
    
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
        
      #if this round has more entries than the previous, reset drawing to the left side of the
      #bracket window, but below the first entry
      if curr.NumEntries > prev_num:
        step = initial_step
        start = (0, max_y+step*2)
        
      #make the outermost lines long to fit a full name and team name
      if i == 0:
        length = wnSettings.seed_length
      else:
        length = wnSettings.match_length

      start, mx, my = curr.Paint(painter, start, length, step, refresh_labels)
      
      # line up rounds that have spots for wrestlers that drop down
      if curr.NumEntries != next_num:
        step *= 2
     
      max_x = max(mx, max_x)
      max_y = max(my, max_y)
      
    return max_x, max_y+initial_step
  
  def CalcScores(self):
    '''Compute all the team scores in this weight class.'''
    # go through the rounds in order and tell them to calculate their scores
    scores = {}
    for i in self.order:
      round = self.rounds[i]
      round.CalcScores(scores)
      
    # return a dictionary of team/score pairs
    return scores
  
  def GetBouts(self, rounds):
    '''Get a list of bouts for the given rounds.'''
    bouts = []
    
    for r in rounds:
      try:
        round = self.rounds[r]
      except:
        continue      
      bouts += round.GetBouts()
  
    return bouts
  
  def GetPlaceWinners(self):
    '''Get all the place winners by seeking rounds that have no next win round.'''
    places = wnPlaceWinners(self.name)
    for r in self.order:
      round = self.rounds[r]
      places += round.GetPlaceWinners()
    return places
  
  def CountBouts(self):
    '''Get a count of the total number of bouts.'''
    i = 0
    for r in self.rounds.values():
      i += r.CountBouts()
     
    return i  
  
  def GetRoundNames(self):
    return self.order
  
  Rounds = property(fget=GetRoundNames)
  
class wnRound(wnNode):
  '''The round class is responsible for holding onto individual matches and their results.'''
  def __init__(self, name, points, parent):
    wnNode.__init__(self, parent, name)
    self.points = points    
    self.entries = []
    self.ordered_entries = []
    self.next_win = None
    self.next_lose = None
        
  def GetNumberOfEntries(self):
    return len(self.entries)
  
  def GetEntries(self):
    return self.ordered_entries
  
  def GetRoundPoints(self):
    return self.points
          
  def NewEntries(self, number):
    #check if we're making new entries based on an order defined in a list
    #if the order is defined, these must be seeds
    if type(number) == list or type(number) == tuple:
      self.ordered_entries = range(len(number))
      for i in number:
        e = wnSeedEntry(i, self)
        self.entries.append(e)
        self.ordered_entries[i-1] = e
    
    #otherwise, define them in order
    #if a number is given, these must be matches
    else:
      for i in range(number):
        self.entries.append(wnMatchEntry(i, self))
      self.ordered_entries = self.entries
      
  def SetNextWinRound(self, round, to_map):
    if len(to_map) != self.NumEntries:
      raise IndexError('This round (%s) has %d entries and the to_map has %d links.' % (self.name, self.NumEntries, len(to_map)))

    #store the next win round
    self.next_win = round
     
    #link the entries between rounds
    for i in range(self.NumEntries):
      #link the entry in this round to the proper entry in the next round
      self.entries[i].NextWin = round.Entries[to_map[i]]
      #link the entry in the next round to this entry
      round.Entries[to_map[i]].Previous = self.entries[i]
      
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
      self.entries[i].Paint(painter, (x,y), refresh_labels)
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

  def CalcScores(self, scores):
    '''Start scoring threads in this round if possible.'''
    # quit right away if there is no next win round
    if self.next_win is None: return
    
    # go through all the entries 
    for entry in self.entries:
      # tell ones that start a thread to calculate their results
      if entry.Previous == [] and entry.Wrestler is not None:
        results = entry.CalcScores()
        
        # the result is a list of all results in a thread sorted from earliest to latest round
        # go through the list in reverse order and add the points
        # keep track of whether bye points should be added or not
        count_byes = False
        bye_score = 0.0
        thread_score = 0.0
        
        while len(results) != 0:
          match, round = results.pop()
          
          # if there was no match, just skip it
          if match is None: continue
          
          # add in non-byes normally and indicate future byes should be counted
          if match.Name != 'Bye':
            thread_score += bye_score + match.Points + round.AdvPoints + round.PlacePoints
            count_byes = True
            bye_score = 0.0
            
          # keep track of bye points for possible addition later
          elif match.Name == 'Bye' and not count_byes:
            bye_score += match.Points + round.AdvPoints + round.PlacePoints
            
          # count byes normally
          elif match.Name == 'Bye' and count_byes:
            thread_score += match.Points + round.AdvPoints + round.PlacePoints
        
        # store the result for this team so far
        tn = entry.Wrestler.Team.Name
        scores[tn] = scores.get(tn, 0.0) + thread_score
        
  def GetBouts(self):
    '''Return all of the matchups in the given round.'''
    bouts = []

    for i in range(0, len(self.entries), 2):
      try:
        e1 = self.entries[i]
        e2 = self.entries[i+1]
      except:
        continue
      
      # it's only a bout of two consecutive entries have wrestlers
      if e1.Wrestler is not None and e2.Wrestler is not None:
        bouts.append(wnBout(self.parent.Name, self.name, e1.Wrestler, e2.Wrestler))
        
    return bouts

  def GetPlaceWinners(self):
    '''Return a list of place winners if this round has no pointer to another win round.'''
    if self.next_win is None:
      # the sole entry must be the primary winner
      w1 = wnPlaceWinner(self.entries[0].Wrestler, self.entries[0].Result)

      # go back a round an get the loser, assume it's none to start
      w2 = wnPlaceWinner(None, None)
      for e in self.entries[0].Previous:
        if e.Wrestler is not None and e.Wrestler.Name != w1.Name:
          w2 = wnPlaceWinner(e.Wrestler, None)
          
      return [w1, w2]
    else:
      return []

  def CountBouts(self):
    '''Get a count of the total number of bouts.'''
    i = 0
    for e in self.entries:
      i += e.CountBouts()
     
    return i
  
  def OnMoveIn(self, event):
    '''Go through all the entries in this round and see if any of the wrestlers can be moved in
    automatically with byes or no matches.'''
    results = []
    count = 0
    
    # go through all the entries and see if any can be set automatically
    for e in self.entries:
      r = e.AutoMoveIn()
      if r is not None: count += 1
      results.append(r)
      
    # determine if the results should be none or byes
    if count != len(self.entries):
      result_obj = wnResultFactory.Create('Bye', None)
    else:
      result_obj = None
      
    # go through an set all the results
    for i in range(len(results)):
      # tell the corresponding entry to store this result, if there is a result
      md = results[i]
      try:
        md.Result = result_obj
        self.entries[i].StoreResult(md, event)
      except:
        pass
      
    # refresh scores
    event.Control.RefreshScores()      
      
  def OnDeleteAll(self, event):
    '''Delete all of the results in this round.'''
    for e in self.entries:
      e.DeleteResult(event)
    event.Control.RefreshScores()
      
  NumEntries = property(fget=GetNumberOfEntries)
  Entries = property(fget=GetEntries)
  RoundPoints = property(fget=GetRoundPoints)
      
class wnEntry(wnNode):
  '''The entry class holds individual match results.'''
  def __init__(self, name, parent):
    wnNode.__init__(self, parent, name)
    self.wrestler = None
    self.next_win = None
    self.next_lose = None
    self.previous = []
    self.result = None
    self.is_scoring = True
    
  def GetResult(self):
    return self.result
  
  def SetResult(self, result):
    self.result = result
    
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
    
  def GetPrevious(self):
    return self.previous
  
  def SetPrevious(self, entry):
    self.previous.append(entry)
  
  def GetTeams(self):
    '''Get the available teams from the tournament. Encapsulate how we get this data using
    properties.'''
    return self.Parent.Parent.Parent.Teams
  
  def GetWeight(self):
    '''Get the weight class name for this entry. Encapsulate how we get this data using
    properties.'''
    return self.parent.Parent.Name
  
  def GetWrestler(self):
    '''Get the wrestler stored at this entry.'''
    return self.wrestler
  def SetWrestler(self, wrestler):
    '''Set the wrestler stored at this entry.'''
    self.wrestler = wrestler
  
  def CalcScores(self):
    '''Begin a score calculation thread. Call CalcScores recursively on each following win
    entry to see if the same wrestler is present there. Collect points won in these rounds
    and update the team score with them.'''
    
    # if the wrestler has continued past this point
    if (self.next_win is not None) and (self.wrestler == self.next_win.Wrestler):
      # call calc scores again
      result = self.next_win.CalcScores()
      
      # prepend the result of this entry to the growing list
      if self.is_scoring:
        result.insert(0, (self.result, self.parent.RoundPoints))
      return result
      
    else:
      # return the result of this entry
      if self.is_scoring:
        return [(self.result, self.parent.RoundPoints)]
      else:
        return []


  def CountBouts(self):
    '''Get a count of the total number of bouts.'''
    if self.result is None:
      return 0
    else:
      return 1
  
  ID = property(fget=GetID)
  NextLose = property(fget=GetNextLose, fset=SetNextLose)
  NextWin = property(fget=GetNextWin, fset=SetNextWin)
  Previous = property(fget=GetPrevious, fset=SetPrevious)
  Teams = property(fget=GetTeams)
  Weight = property(fget=GetWeight)
  Wrestler = property(fget=GetWrestler, fset=SetWrestler)
  Result = property(fget=GetResult, fset=SetResult)
  
class wnMatchEntry(wnEntry, wnMouseEventReceivable, wnMatchMenuReceivable):
  '''The match entry class hold individual match results.'''
  def __init__(self, name, parent):
    wnEntry.__init__(self, name, parent)
    
  def Paint(self, painter, pos=(0,0), refresh_labels=False):
    '''Paint all of the text controls.'''
    if self.wrestler is None: text = ''
    else: text = self.wrestler.Name
    
    if refresh_labels:
      painter.DrawMatchTextControl(text,
                                   pos[0]+wnSettings.match_offset, pos[1]-wnSettings.match_height,
                                   wnSettings.match_length-wnSettings.match_offset*2, wnSettings.match_height,
                                   self.ID, self)
    
  def OnMouseEnter(self, event):
    '''Show a popup window with the match results if available. Highlight the entry if it can
    receive results.'''
    if self.wrestler is not None and self.previous != []:
      event.Control.ShowPopup(str(self.result))
    for e in self.previous:
      if e.Wrestler is not None:
        event.Control.Highlight(True)
        break
      
  def OnMouseLeave(self, event):
    '''Hide the popup window with the match results. Unhighlight the control if it was
    highlighted.'''
    event.Control.HidePopup()
    event.Control.Highlight(False)
    
  def OnLeftDown(self, event):
    '''Display the dialog box that allows a user to enter result information, if there is at least
    one wrestler in the preceeding entries.'''
    enabled = False
    for e in self.previous:
      if e.Wrestler is not None:
        enabled = True
        break
    
    #quit now if the dialog isn't enabled
    if not enabled: return
    
    #show the results dialog, providing the wrestlers and current results
    opponents = [entry.Wrestler for entry in self.previous if entry.Wrestler is not None]
    result = event.Painter.ShowMatchDialog(opponents, self.result, self.is_scoring)
    
    # store the result
    if result is not None:
      self.StoreResult(result, event)
      event.Control.RefreshScores()
             
  def OnRightUp(self, event):
    '''Show the popup menu.'''
    event.Control.ShowMenu(event.Position)
    
  def OnDelete(self, event):
    '''Delete the wrestler in this entry.'''
    self.DeleteResult(event)
    event.Control.HidePopup()
    event.Control.RefreshScores()
    
  def OnDeleteAll(self, event):
    '''Delete all the events in the round this entry is in.'''
    self.Parent.OnDeleteAll(event)
    
  def OnMoveIn(self, event):
    '''See if wrestlers can be moved into this round automatically. Just call the function in the
    parent round.'''
    self.Parent.OnMoveIn(event)
    
  def AutoMoveIn(self):
    '''See if a wrestler can be moved into this entry automatically.'''
    entries = []
    for e in self.previous:
      if e.Wrestler is not None:
        entries.append(e)
    
    # see if there is only one wrestler
    if len(entries) == 1:
      return wnMatchData(entries[0].Wrestler, None, None, None,
                  entries[0].Wrestler.IsScoring)
    # or if there are no wrestlers
    elif len(entries) == 0:
      return True
    # or if there are two, non-scoring wrestlers
    elif (not entries[0].Wrestler.IsScoring and not entries[1].Wrestler.IsScoring):
      return True
    else:
      return None
    
  def StoreResult(self, result, event):
    '''Store a result in this entry.'''
    # remove any old result first
    if self.wrestler is not None:
      self.wrestler.DeleteResult(self.ID)
    
    #store the information in the entry
    self.result = result.Result
    self.wrestler = result.Winner
    
    #store the result for the wrestler
    self.wrestler.StoreResult(self.ID, self.result)
    
    #show the new winner name
    event.Painter.GetControl(self.ID).SetLabel(self.wrestler.Name)
    
    #move the loser if he exists and isn't eliminated
    if result.Loser is not None:
      for e in self.previous:
        if e.Wrestler == result.Loser and e.NextLose is not None:
          e.NextLose.Wrestler = result.Loser
          e.NextLose.Paint(event.Painter, refresh_labels=True)
          
  def DeleteResult(self, event):
    if self.result is not None:
      self.wrestler.DeleteResult(self.ID)
    self.wrestler = None
    self.result = None
    event.Painter.GetControl(self.ID).SetLabel('')
        
class wnSeedEntry(wnEntry, wnMouseEventReceivable, wnFocusEventReceivable, wnSeedMenuReceivable):
  '''The seed entry class holds information about seeded wrestlers.'''
  def __init__(self, name, parent):
    wnEntry.__init__(self, name, parent)
    self.is_last = False
    
  def Paint(self, painter, pos=(0,0), refresh_labels=False, full=True):
    '''Paint all of the text controls.'''
    if full:
      #draw the seed number
      painter.DrawText(str(self.name), pos[0], pos[1]-wnSettings.seed_height)
 
    #draw the text control
    if refresh_labels:
      if self.wrestler is None:
        text = ''
      else:
        text = self.wrestler.FormattedName
      
      #get the available teams from the round->weight->tournament
      teams = self.Teams.keys()      
      painter.DrawSeedTextControl(text,
                                  pos[0]+wnSettings.seed_offset, pos[1]-wnSettings.seed_height,
                                  wnSettings.seed_length, wnSettings.seed_height,
                                  teams, self.ID, self)
    
  def OnRightUp(self, event):
    '''Show the popup menu.'''
    event.Control.ShowMenu(self.is_last, event.Position)
    
  def OnDelete(self, event):
    '''Delete the wrestler in this entry.'''
    if self.wrestler is not None and self.wrestler.Team is not None:
      self.wrestler.Team.DeleteWrestler(self.wrestler.Name, self.Weight)
    self.wrestler = None
    event.Control.ClearValue()
    event.Control.RefreshScores()
    
  def OnSwapUp(self, event):
    '''Swap the wrestler here with the wrestler one seed above.'''
    # get a ref to the previous entry
    e = self.parent.Entries[int(self.name)-2]
    
    # do the swap and redraw
    self.Swap(e, event.Painter)
        
    # change the focus
    event.Painter.SetFocus(e.ID)
    
  def OnSwapDown(self, event):
    '''Swap the wrestler here with the wrestler one seed below.'''
    # get a ref to the next entry
    e = self.parent.Entries[int(self.name)%self.Parent.NumEntries]
    
    # do the swap and redraw
    self.Swap(e, event.Painter) 
    
    # change the focus
    event.Painter.SetFocus(e.ID)
    
  def OnSetLastSeed(self, event):
    '''Set this seed as the last seed that should be moved in case of a delete and move up.'''
    self.is_last = True
    
    # make sure none of the other seeds are last
    for e in self.parent.Entries:
      if e.IsLast and e is not self:
        e.IsLast = False
        break

  def OnDeleteMoveUp(self, event):
    '''Delete this seed and move all others up until the last seed or a blank seed is encountered.'''
    # first kill this wrestler
    if self.wrestler is not None and self.wrestler.Team is not None:
      self.wrestler.Team.DeleteWrestler(self.wrestler.Name, self.Weight)
    self.wrestler = None
    event.Control.ClearValue()
        
    # make sure we weren't the last seed
    if self.is_last:
      # refresh the scores
      event.Control.RefreshScores()
      return

    # now move all the other wrestlers
    for i in range(int(self.name)-1, self.parent.NumEntries-1):
      e_this = self.parent.Entries[i]
      e_next = self.parent.Entries[i+1]
      
      # make sure the next entry is not None
      if e_next.Wrestler is None: break
      
      # do the swap and redraw
      e_this.Swap(e_next, event.Painter)
      
      # make sure this is not the last seed
      if e_this.is_last: break
    
    # refresh the scores
    event.Control.RefreshScores()
    
  def OnInsertMoveDown(self, event):
    '''Insert a new blank entry at this location, pushing down all wrestlers past this point. If
    there are wrestlers all the way to the last location, then the last wrestler will be lost.'''
    # build a dummy entry to hold temp data
    temp = wnSeedEntry(None, None)
    temp.Wrestler = None
    temp.IsLast = False
    temp.Paint = lambda painter, refresh_labels, full: full
    
    # go through the list and swap wrestlers down
    for i in range(int(self.name)-1, self.parent.NumEntries):
      self.parent.Entries[i].Swap(temp, event.Painter)
      
      # stop when the wrestler is none
      if temp.Wrestler is None: break
      
    # if the temp wrestler is not none, get rid of it from the team
    # this happens when the insert overflows the bracket
    if temp.wrestler is not None and temp.wrestler.Team is not None:
      temp.wrestler.Team.DeleteWrestler(temp.wrestler.Name, self.Weight)
    
    # refresh all scores
    event.Control.RefreshScores()
  
  def OnKillFocus(self, event):
    '''Store the entered value if it is valid. Give the next seed the focus, wrapping around at
    the first and last seeds.'''
    self.updateData(event)
    self.updateFocus(event)
    event.Control.RefreshScores()    
    
  def Swap(self, entry, painter):
    '''Swap this entry's values with another one.'''
    # store the entry values
    w1 = self.wrestler, self.is_last
    w2 = entry.Wrestler, entry.IsLast

    # swap the entry data
    entry.Wrestler, entry.IsLast = w1
    self.wrestler, self.is_last = w2

    # redraw the text controls    
    self.Paint(painter, refresh_labels=True, full=False)
    entry.Paint(painter, refresh_labels=True, full=False)
      
  def updateData(self, event):
    '''Figure out what needs to be done to store the wrestler properly.'''
    # the control is invalid or empty
    if not event.Control.IsValid() or event.Control.IsEmpty():
      # the current wrestler should be deleted
      if self.wrestler is not None:
        self.wrestler.Team.DeleteWrestler(self.wrestler.Name, self.Weight)
        self.wrestler = None
      return
        
    #get the data from the control since it must be valid
    w_name, t_name = event.Control.GetValue().split(' | ')
    w_name = w_name.strip()
    t_name = t_name.strip()
    
    # make sure both fields are present
    if w_name == '' or t_name == '':
      # the current wrestler should be deleted
      if self.wrestler is not None:
        self.wrestler.Team.DeleteWrestler(self.wrestler.Name, self.Weight)
        self.wrestler = None
      return

    # add a new wrestler
    if self.wrestler is None:
      self.wrestler = self.Teams[t_name].NewWrestler(w_name, self.Weight)
    
    # replace an existing wrestler
    elif self.wrestler is not None:
      #if the held team is equal to the new team
      if self.wrestler.Team.Name == t_name:
        #just update the wrestler in the current team
        self.wrestler.Name = w_name
      else:
        #otherwise, delete the current wrestler from the team
        self.wrestler.Team.DeleteWrestler(self.wrestler.Name, self.Weight)
        #and make a new wrestler in the new team
        self.wrestler = self.Teams[t_name].NewWrestler(w_name, self.Weight)
      
  def updateFocus(self, event):
    '''Figure out where the focus should go next.'''
    #give the focus only to seeds, not to match entries
    next_id = event.Painter.GetFocus()
    if next_id is not None:
      #focus on the next entry
      if next_id[1] != self.ID[1]:
        if self.name == 1:
          event.Painter.SetFocus(self.Parent.Entries[self.Parent.NumEntries-1].ID)
        elif self.name == self.Parent.NumEntries:
          event.Painter.SetFocus(self.Parent.Entries[0].ID)
      else:
        event.Painter.SetFocus(next_id)
        
  def GetIsLast(self):
    return self.is_last
  
  def SetIsLast(self, value):
    self.is_last = value
    
  IsLast = property(fget=GetIsLast, fset=SetIsLast)



if __name__ == '__main__':
  pass
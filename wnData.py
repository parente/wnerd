class wnTournament(object):
  def __init__(self, name, description):
    self.name = name
    self.description = description
    self.teams = {}
    self.weight_classes = {}
        
  def NewWeightClass(self, name):
    wc = wnWeightClass(str(name))
    wc.tournament = self
    self.weight_classes[str(name)] = wc
    
    return wc
  
  def NewTeam(self, name):
    t = wnTeam(name)
    t.tournament = self
    self.teams[str(name)] = t
    
    return t
  
class wnWeightClass(object):
  def __init__(self, name):
    self.name = name
    self.rounds = {}
    
    self.tournament = None
    
  def NewRound(self, name, points):
    r = wnRound(str(name), points)
    r.weight_class = self
    self.rounds[str(name)] = r
    
    return r
  
class wnRound(object):
  def __init__(self, name, points):
    self.name = name
    self.points = points    
    self.entries = []
    self.next_win = None
    self.next_lose = None
    
    self.weight_class = None
    
  def getNumberOfEntries(self):
    return len(self.entries)
  
  NumEntries = property(fget=getNumberOfEntries)
        
  def NewEntries(self, number):
    for i in range(number):
      self.entries.append(wnEntry())
      
  def SetNextWinRound(self, next, to_map):
    if len(to_map) != self.NumEntries:
      raise IndexError('The to_map must contain a link for every entry in this round. This round has %d entries and the to_map has %d links.' % (self.NumEntries, len(to_map)))

    #store the next win round
    self.next_win = next
    
    #link the entries between rounds
    for i in range(to_map):
      #link the entry in this round to the proper entry in the next round
      self.entries[i].next_win = self.next_win.entries[to_map[i]]
      
  #def SetNextWinRound(self, next, bottom=False, flip=False):
  #  #see how many entries the next round has
  #  #if the next round has half as many, then every two entries in this round link to one entry
  #  #  in the next round
  #  if next.NumEntries == self.NumEntries/2:
  #    for i in range(0,self.NumEntries,2):
  #      self.entries[i].next_win = next.entries[i]
  #      self.entries[i+1].next_win = next.entries[i]
  #      
  #  #if the next round has just as many entries, then alternate the winners top/bottom
  #  #  and decide if they should flip
  #  else:
  #    for i in range(bottom,self.NumEntries,2):
  #      self.entries[i].next_win = next.entries[i]
  #      
  #def SetNextLoseRound(self, next, bottom=False, flip=False):
  #  #see how many entries the next round has
  #  #if the next round has half as many, then every two entries in this round link to one entry
  #  #  in the next round
  #  if next.NumEntries == self.NumEntries/2:
  #    for i in range(0,self.NumEntries,2):
  #      self.entries[i].next_lose = next.entries[i]
  #      self.entries[i+1].next_lose = next.entries[i]
  #      
  #  #if the next round has just as many entries, then alternate the winners top/bottom
  #  #  and decide if they should flip
  #  else:
  #    for i in range(bottom,self.NumEntries,2):
  #      self.entries[i].next_lose = next.entries[i]
      
class wnEntry(object):
  def __init__(self):
    self.wrestler = None
    self.result = None
    self.next_win = None
    self.next_lose = None
    
    self.round = None
    
class wnPoints(object):
  def __init__(self, adv_pts=0, place_pts=0):
    self.adv_points = adv_pts
    self.place_pts = place_pts
  
class wnResult(object):
  def __init__(self):
    self.entry = None
    
class wnResultPin(wnResult):
  def __init__(self):
    wnResult.__init__(self)
    self.pin_time = 0

class wnResultDecision(wnResult):
  def __init__(self):
    wnResult.__init__(self)    
    self.win_score = 0
    self.lose_score = 0
    
class wnResultBye(wnResult):
  def __init__(self):
    wnResult.__init__(self)
    
class wnResultDefault(wnResult):
  def __init__(self):
    wnResult.__init__(self)    
  
class wnTeam(object):
  def __init__(self, name):
    self.name = name    
    self.wrestlers = []
    self.point_adjust = 0
    
    self.tournament = None
    
  def NewWrestler(self, name, weight):
    w = wnWrestler(str(name), str(weight))
    w.team = self
    self.wrestlers.append(w)
    
    return w
      
class wnWrestler(object):
  def __init__(self):
    self.name = ''
    self.weight = ''
    self.is_scoring = True
    
    self.team = None
    
if __name__ == '__main__':
  pass
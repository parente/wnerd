class wnTournament(object):
  def __init__(self):
    self.weight_classes = {}
    self.teams = {}
    
  def NewWeightClass(self, name):
    wc = wnWeightClass()
    wc.name = str(name)
    wc.tournament = self
    self.weight_classes[wc.name] = wc
    
    return wc
  
class wnWeightClass(object):
  def __init__(self):
    self.name = ''
    self.rounds = {}
    
    self.tournament = None
    
  def NewRound(self, name):
    r = wnRound()
    r.name = str(name)
    r.weight_class = self
    self.rounds[r.name] = r
    
    return r
  
class wnRound(object):
  def __init__(self):
    self.name = ''
    self.entries = []
    self.points = None
    
    self.weight_class = None
    
  def NewEntry(self):
    #how do we make it easy to set up links between rounds, at least for winners?
    #maybe pass in an optional previous and next round? won't work for swaps in losers bracket
    pass
  
class wnEntry(object):
  def __init__(self):
    self.wrestler = None
    self.result = None
    self.next_win = None
    self.next_lose = None
    self.previous_win = None
    self.previous_lose = None
    
    self.round = None
  
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
  def __init__(self):
    self.name = ''    
    self.location = ''
    self.wrestlers = []
    self.point_adjust = 0
    
  def NewWrestler(self, name, weight):
    w = wnWrestler()
    w.name = str(name)
    w.weight = str(weight)
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
  import cPickle as cp
  
  t = wnTournament()
  
'''
The score data module contains classes responsible for holding point related data, either for
individual matches or advancement and placement point systems.
'''

class wnPoints(object):
  def __init__(self, adv_pts=0, place_pts=0):
    self.adv_points = adv_pts
    self.place_pts = place_pts
  
class wnResult(object):
  '''The result class holds a reference to its entry.'''
  def __init__(self):
      pass
    
  def GetPoints(self):
    return 0
    
class wnResultPin(wnResult):
  '''This class holds information about a pin win.'''
  def __init__(self):
    wnResult.__init__(self)
    self.pin_time = 0
    
  def GetPoints(self):
    return 2

class wnResultDecision(wnResult):
  '''This class holds information about a decision.'''
  def __init__(self):
    wnResult.__init__(self)    
    self.win_score = 0
    self.lose_score = 0
    
  def GetPoints(self):
    diff = self.win_score - self.lose_score
    if diff >= 15:
      return 1.5
    elif diff >=8:
      return 1.0
    else:
      return 0
    
class wnResultBye(wnResult):
  '''This class holds information about a bye.'''
  def __init__(self):
    wnResult.__init__(self)
    
class wnResultDefault(wnResult):
  '''This class holds information about a default win.'''
  def __init__(self):
    wnResult.__init__(self)
    
  def GetPoints(self):
    return 2
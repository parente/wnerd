'''
The team data module contains classes that hold team and wrestler information.
'''

class wnTeam(object):
  '''The team class holds wrestlers and points.'''
  def __init__(self, name):
    self.name = name    
    self.wrestlers = {}
    self.point_adjust = 0
    
    self.tournament = None
    
  def GetName(self):
    return self.name
  
  Name = property(fget=GetName)
  
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
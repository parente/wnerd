'''
The team data module contains classes that hold team and wrestler information.
'''

class wnTeam(object):
  '''The team class holds wrestlers and points.'''
  def __init__(self, name):
    self.name = name    
    self.wrestlers = {}
    self.point_adjust = 0
   
  def GetName(self):
    return self.name
  
  Name = property(fget=GetName)
  
  def NewWrestler(self, name, weight, old=None):
    '''Add a new wrestler to the team. Make the wrestler scoring if he is the first to be added.
    Remove the old wrestler object if it exists.'''
    
    #just change the old wrestler if he exists


    #otherwise, add the new wrestler 

    w = wnWrestler(str(name), str(weight))
    w.team = self
    self.wrestlers[str(weight)] = w
    
    return w
      
class wnWrestler(object):
  '''The wrestler class holds information about individuals in a tournament.'''
  def __init__(self, name, weight, is_scoring=True):
    self.name = name
    self.weight = weight
    self.is_scoring = is_scoring
    
    self.team = None
    
  def GetName(self):
    return self.name
  
  Name = property(fget=GetName)
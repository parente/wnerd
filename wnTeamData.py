'''
The team data module contains classes that hold team and wrestler information.
'''
import wnSettings

class wnTeam(object):
  '''The team class holds wrestlers and points.'''
  def __init__(self, name):
    self.name = name    
    self.wrestlers = {}
    self.point_adjust = 0
   
  def GetName(self):
    return self.name
  
  Name = property(fget=GetName)
  
  def NewWrestler(self, name, weight):
    '''Add a new wrestler to the team. Make the wrestler scoring if he is the first to be added.'''
    w = wnWrestler(str(name), str(weight), self)
    self.wrestlers.setdefault(str(weight), [])
    self.wrestlers[str(weight)].append(w)
    
    return w
  
  def DeleteWrestler(self, name, weight):
    '''Delete a wrestler from the team.'''
    w_list = self.wrestlers[str(weight)]
    for i in range(len(w_list)):
      if w_list[i] == name:
        del w_list[i]
        break
      
class wnWrestler(object):
  '''The wrestler class holds information about individuals in a tournament.'''
  def __init__(self, name, weight, team, is_scoring=True):
    self.name = name
    self.weight = weight
    self.team = team
    self.is_scoring = is_scoring
    
  def GetFormattedName(self):
    n_fill = wnSettings.max_name_length - len(self.name)
    fill_text = ' '*n_fill
    return self.name + fill_text + ' | ' + self.team.Name
    
  def GetName(self):
    return self.name
  
  def SetName(self, name):
    self.name = name

  def GetTeam(self):
    return self.team
  
  def GetWeight(self):
    return self.weight
  
  Weight = property(fget=GetWeight)
  Team = property(fget=GetTeam)  
  Name = property(fget=GetName, fset=SetName)
  FormattedName = property(fget=GetFormattedName)
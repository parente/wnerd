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
    
  def __repr__(self):
    return '<Team Name: %s Wrestlers: %s>' % (self.name, self.wrestlers)
   
  def GetName(self):
    return self.name
  
  Name = property(fget=GetName)
  
  def NewWrestler(self, name, weight):
    '''Add a new wrestler to the team. Make the wrestler scoring if he is the first to be added.'''
    w = wnWrestler(name, weight, self)
    self.wrestlers.setdefault(weight, [])
    self.wrestlers[weight].append(w)
    
    return w
  
  def DeleteWrestler(self, name, weight):
    '''Delete a wrestler from the team.'''
    w_list = self.wrestlers[weight]
    
    # search all the wrestlers in this weight class
    for i in range(len(w_list)):
      if w_list[i].Name == name:
        # remove empty weight class lists
        if len(w_list) == 1:
          del self.wrestlers[weight]
        # otherwise just deleted the desired wrestler
        else:
          del w_list[i]
        break
      
class wnWrestler(object):
  '''The wrestler class holds information about individuals in a tournament.'''
  def __init__(self, name, weight, team, is_scoring=True):
    self.name = name
    self.weight = weight
    self.team = team
    self.is_scoring = is_scoring
    
  def __repr__(self):
    return '<Wrestler Name: %s Weight: %s Team: %s>' % (self.name, self.weight, self.team.Name)
    
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
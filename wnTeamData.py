'''
The team data module contains classes that hold team and wrestler information.
'''
from wnTempData import *
import wnSettings

class wnTeam(object):
  '''The team class holds wrestlers and points.'''
  def __init__(self, name, tournament):
    self.name = name
    self.wrestlers = {}
    self.point_adjust = 0.0
    self.points = dict([(w, 0.0) for w in tournament.Weights])
    
  def __repr__(self):
    return '<Team Name: %s Wrestlers: %s>' % (self.name, self.wrestlers)
   
  def GetWrestlers(self):
    '''Flatten all the wrestlers in each weight class into one list.'''
    wrestlers = []
    order = self.wrestlers.keys()
    order.sort()
    
    for i in order:
      for w in self.wrestlers[i]:
        wrestlers.append(w)
      
    return wrestlers
   
  def GetName(self):
    return self.name
  
  def SetName(self, val):
    self.name = str(val)
  
  def GetTotalScore(self):
    s = self.point_adjust
    for i in self.points.values():
      s += i
    return s
  
  def SetPointAdjust(self, value):
    self.point_adjust = value
    
  def GetPointAdjust(self):
    return self.point_adjust
  
  def CalcFastFall(self):
    '''Go through all the wrestlers on this team and compute their fast fall results.'''
    falls = []
    for weight in self.wrestlers:
      weight_list = self.wrestlers[weight]
      for wrestler in weight_list:
        ff = wrestler.CalcFastFall()
        if ff is not None:
          falls.append(ff)
        
    return falls
  
  def SetWeightScore(self, weight_name, value):
    '''Set the score for a weight to a certain value.'''
    self.points[weight_name] = value
  
  def NewWrestler(self, name, weight):
    '''Add a new wrestler to the team. Make the wrestler scoring if he is the first to be added.'''
    w = wnWrestler(name, weight, self)
    self.wrestlers.setdefault(weight, [])
    self.wrestlers[weight].append(w)
    
    return w
  
  def ChangeWrestler(self, old_name, new_name):
    '''Change the name of a wrestler.'''
    for l in self.wrestlers.values():
      for w in l:
        if w.Name == old_name:
          w.Name = new_name
          return
  
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
      
  Name = property(fget=GetName, fset=SetName)  
  Score = property(fget=GetTotalScore)
  PointAdjust = property(fget=GetPointAdjust, fset=SetPointAdjust)
  Wrestlers = property(fget=GetWrestlers)
      
class wnWrestler(object):
  '''The wrestler class holds information about individuals in a tournament.'''
  def __init__(self, name, weight, team, is_scoring=True):
    self.name = name
    self.weight = weight
    self.team = team
    self.results = {}
    
  def __repr__(self):
    return '<Wrestler Name: %s Weight: %s Team: %s>' % (self.name, self.weight, self.team.Name)
  
  def __eq__(self, w):
    '''Compare the properties of a wrestler, not just its ID.'''
    try:
      return (self.name == w.name and self.team == w.team)
    except:
      return False
      
  def __ne__(self, w):
    '''Compare the properties of a wrestler, not just its ID.'''
    try:
      return (self.name != w.name or self.team != w.team)
    except:
      return False
    
  def StoreResult(self, id, result):
    '''Store a result for a particular match ID.'''
    self.results[id] = result
    
  def DeleteResult(self, id):
    '''Delete a result for a particular match ID.'''
    try:
      del self.results[id]
    except:
      pass
    
  def CalcFastFall(self):
    '''Get the total number of pins and pin times.'''
    total = [0, 0]
    for r in self.results.values():
      if r is not None and r.Name == 'Pin':
        total[0] += 1
        total[1] += r.Value

    if total[0] == 0:
      return None
    else:
      return wnFastFall(self, total[0], total[1])
    
  def GetFormattedName(self):
    n_fill = wnSettings.max_name_length - len(self.name)
    fill_text = ' '*n_fill
    return self.name + fill_text + ' | ' + self.team.Name
    
  def GetShortName(self):
    if self.IsScoring:
      i = self.name.find(' ')
    else:
      i = self.name.find(' ', len(wnSettings.no_scoring_prefix)+1)
    return self.name[i+1:]
    
  def GetName(self):
    return self.name
  
  def SetName(self, name):
    self.name = name

  def GetTeam(self):
    return self.team
  
  def GetWeight(self):
    return self.weight
  
  def GetIsScoring(self):
    return (self.name.find(wnSettings.no_scoring_prefix) != 0)
  
  Weight = property(fget=GetWeight)
  Team = property(fget=GetTeam)  
  Name = property(fget=GetName, fset=SetName)
  FormattedName = property(fget=GetFormattedName)
  ShortName = property(fget=GetShortName)
  IsScoring = property(fget=GetIsScoring)
'''
The score data module contains classes responsible for holding point related data, either for
individual matches or advancement and placement point systems.
'''

class wnPoints(object):
  def __init__(self, adv_pts=0, place_pts=0):
    self.adv_points = adv_pts
    self.place_pts = place_pts
  
class wnResultFactory(object):
  def Create(cls, type):
    dispatch = {'None' : None, 'Pin' : wnResultPin, 'Decision' : wnResultDecision,
                'Bye' : wnResultBye, 'Default' : wnResultDefault}
    
    obj = dispatch[type]
    
    try:
      obj = obj()
    except:
      pass
    return obj
  
  Create = classmethod(Create)
  
class wnResult(object):
  '''The result class holds a reference to its entry.'''
  def __init__(self):
      pass
  
  def GetPoints(self):
    return 0
    
  Points = property(fget=GetPoints)
    
class wnResultPin(wnResult):
  '''This class holds information about a pin win.'''
  def __init__(self):
    wnResult.__init__(self)
    self.pin_time = 0
    
  def __str__(self):
    return 'Pin\nTime: %s' % str(self.pin_time)
    
  def GetPoints(self):
    return 2
  
  def GetName(self):
    return 'Pin'
  
  Points = property(fget=GetPoints)
  Name = property(fget=GetName)

class wnResultDecision(wnResult):
  '''This class holds information about a decision.'''
  def __init__(self):
    wnResult.__init__(self)    
    self.win_score = 0
    self.lose_score = 0
    
  def __str__(self):
    return 'Decision\n%d-%d' % (self.win_score, self.lose_score)
    
  def GetPoints(self):
    diff = self.win_score - self.lose_score
    if diff >= 15:
      return 1.5
    elif diff >=8:
      return 1.0
    else:
      return 0

  def GetName(self):
    return 'Decision'
    
  Points = property(fget=GetPoints)
  Name = property(fget=GetName)    
    
class wnResultBye(wnResult):
  '''This class holds information about a bye.'''
  def __init__(self):
    wnResult.__init__(self)
    
  def __str__(self):
    return 'Bye'
    
  def GetName(self):
    return 'Bye'

  Name = property(fget=GetName)    
    
class wnResultDefault(wnResult):
  '''This class holds information about a default win.'''
  def __init__(self):
    wnResult.__init__(self)
    
  def __str__(self):
    return 'Default'
    
  def GetPoints(self):
    return 2
  
  def GetName(self):
    return 'Default'
  
  Points = property(fget=GetPoints)
  Name = property(fget=GetName)
  
if __name__ == '__main__':
  print wnResultBye().Points
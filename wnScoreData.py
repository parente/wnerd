'''
The score data module contains classes responsible for holding point related data, either for
individual matches or advancement and placement point systems.
'''

class wnPoints(object):
  def __init__(self, adv_pts=0, place_pts=0):
    self.adv_points = adv_pts
    self.place_points = place_pts
    
  def GetAdvancementPoints(self):
    return self.adv_points
  
  def GetPlacementPoints(self):
    return self.place_points
  
  AdvPoints = property(fget=GetAdvancementPoints)
  PlacePoints = property(fget=GetPlacementPoints)
  
class wnResultFactory(object):
  def Create(cls, type, args=None):
    
    if type == 'None':
      return None
    elif type == 'Pin':
      return wnResultPin(args)
    elif type == 'Decision':
      return wnResultDecision(args[0], args[1])
    elif type == 'Bye':
      return wnResultBye()
    elif type == 'Default':
      return wnResultDefault()
      
  Create = classmethod(Create)
  
class wnResult(object):
  '''The result class holds a reference to its entry.'''
  def __init__(self):
      pass
  
  def GetPoints(self):
    return 0
  
  def GetTextValue(self):
    return None
  
  def GetValue(self):
    return None
    
  Points = property(fget=GetPoints)
  TextValue = property(fget=GetTextValue)
  Value = property(fget=GetValue)
    
class wnResultPin(wnResult):
  '''This class holds information about a pin win.'''
  def __init__(self, pin_time):
    wnResult.__init__(self)
    self.pin_time = pin_time
    
  def __str__(self):
    return 'Pin\nTime: %s' % self.TextValue
    
  def GetPoints(self):
    return 2
  
  def GetName(self):
    return 'Pin'
  
  def GetTextValue(self):
    m = str(int(self.pin_time/60.0)).rjust(2)
    s = self.pin_time%60
    if s < 10:
      s = '0' + str(s)
    else:
      s = str(s)
      
    return m + ':' + s
  
  def GetValue(self):
    return self.pin_time
  
  Points = property(fget=GetPoints)
  Name = property(fget=GetName)
  Value = property(fget=GetValue)
  TextValue = property(fget=GetTextValue)

class wnResultDecision(wnResult):
  '''This class holds information about a decision.'''
  def __init__(self, win_score, lose_score):
    wnResult.__init__(self)    
    self.win_score = win_score
    self.lose_score = lose_score
    
  def __str__(self):
    return 'Decision\n%d-%d' % (self.win_score, self.lose_score)

  def GetTextValue(self):
    sw = str(self.win_score).rjust(2)
    sl = str(self.lose_score).rjust(2)
    return sw + '-' +  sl
   
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

  TextValue = property(fget=GetTextValue)
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
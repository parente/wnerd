'''
The temp data module defines classes that are instantiated temporarily for calculations like fast
fall and bouts.
'''

from wnScoreData import wnResultPin

class wnBout(object):
  '''The bout class defines a match between two wrestlers. An instance of this class is only useful
  when the two paired wrestlers need to be explicitly named (i.e. when printing bouts). It is not a
  part of the bracket data hierarchy, and is only constructed as a temporary representation of part
  of a bracket.'''
  def __init__(self, weight, round, wrestler1, wrestler2):
    self.Weight = weight
    self.Round = round
    self.Wrestler1 = wrestler1
    self.Wrestler2 = wrestler2
    
class wnFastFall(object):
  '''The fast fall class hold info about a wrestler's fast fall results. It also defines methods
  that make sorting easier.'''
  def __init__(self, name, team, weight, pins, pin_time):
    self.Name = name
    self.Weight = weight
    self.Team = team
    self.Pins = pins
    self.TimeValue = pin_time
    self.TimeText = wnResultPin(self.TimeValue).TextValue
    
  def __cmp__(self, other):
    '''During sorting, compare by pins and time values. Sort so that the results are ordered
    descending primarily from most pins to least and secondarily from least time to most.'''
    # sort first by pins
    if self.Pins > other.Pins:
      return -1
    elif self.Pins < other.Pins:
      return 1
    else:
      # and then by time values
      if self.TimeValue < other.TimeValue:
        return -1
      elif self.TimeValue > other.TimeValue:
        return 1
      else:
        return 0
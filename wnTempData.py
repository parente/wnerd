'''
The temp data module defines classes that are instantiated temporarily for calculations like fast
fall and bouts.
'''

from wnScoreData import *
from UserList import UserList

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
  def __init__(self, wrestler, pins, pin_time):
    self.Name = wrestler.Name
    self.Weight = wrestler.Weight
    self.Team = wrestler.Team.Name
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
      
class wnMatchData(object):
  '''The match data class holds data about a match entered by a user that is used to
  fill in a match entry.'''
  def __init__(self, winner, loser, result_type, result_value, is_scoring):
    self.Winner = winner
    self.Loser = loser
    self.Result = wnResultFactory.Create(result_type, result_value)
    self.IsScoring = is_scoring
      
class wnPlaceWinner(object):
  '''The place winner class holds information about wrestlers that are place winners and the results
  of their last matches.'''
  def __init__(self, wrestler, result):
    if wrestler is None:
      self.Name = 'None'
      self.Team = 'None'
    else:
      self.Name = wrestler.Name
      self.Team = wrestler.Team.Name
    self.Result = str(result)
    
class wnPlaceWinners(UserList):
  '''A collection of place winners by weight.'''
  def __init__(self, weight):
    UserList.__init__(self)
    self.Weight = weight
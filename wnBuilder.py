from wnBracketData import *
from wnScoreData import *
from wnTeamData import *

class wnRoundSetup(object):
  def __init__(self, name, points, num_entries, next_win = None, win_map = None, next_lose = None,
               lose_map = None, order = None):
    self.Name = name
    self.Points = points
    self.NumEntries = num_entries
    self.NextWin = next_win
    self.NextLose = next_lose
    self.WinMap = win_map
    self.LoseMap = lose_map

class wnBuilder(object):
  def GetTournaments(self):
    '''Return the tournaments currently supported.'''
    configs = [v for k, v in globals().items() if k.find('Config') > -1]
    
    return configs
  
  def Create(self, config, name, weights, teams):
    '''Determine the type of tournament to create and then build it.'''
    #make sure the config is valid
    if config not in self.GetTournaments():
      raise TypeError('The tournament configuration is invalid.')
    
    #create the new tournament
    tourn = wnTournament(name, config.Seeds)
      
    #build the weights
    for w_name in weights:
      w = tourn.NewWeightClass(w_name)

      #build the rounds
      for round in config.Rounds:
        r = w.NewRound(round.Name, round.Points)
        
        #build the entries
        r.NewEntries(round.NumEntries)

      #connect the rounds
      self.connectRounds(w, config.Rounds)
      
    #add the teams
    for t in teams:
      tourn.NewTeam(t)      
    
    return tourn
  
  def connectRounds(self, weight, rounds):
    #cycle through all the rounds
    for round in rounds:
      #get the round
      this_round = weight.GetRound(round.Name)
      
      if round.WinMap is not None:
        #get the win round
        win_round = weight.GetRound(round.NextWin)
        #and connect it
        this_round.SetNextWinRound(win_round, round.WinMap)

      if round.LoseMap is not None:
        #get the lose round
        lose_round = weight.GetRound(round.NextLose)
        #and connect it
        this_round.SetNextLoseRound(lose_round, round.LoseMap)    

class wnBCInvitationalConfig:
  Name = 'Bristol Central Invitational'
  Description = 'The bracket format used in the Bristol Central Invitational tournaments. The outbracket has 32 seed slots, and double-elimination begins in the quarter finals. There are six places.'
  Seeds = [1, 32, 17, 16, 9, 24, 25, 8, 5, 28, 21, 12, 13, 20, 29, 4,
           3, 30, 19, 14, 11, 22, 27, 6, 7, 26, 23, 10, 15, 18, 31, 2]
  Rounds = [wnRoundSetup('Rat-Tails', wnPoints(0,0),
                         [1, 32, 17, 16, 9, 24, 25, 8, 5, 28, 21, 12, 13, 20, 29, 4,
                          3, 30, 19, 14, 11, 22, 27, 6, 7, 26, 23, 10, 15, 18, 31, 2],
                         'Sixteen Champion',
                         [0,0,1,1,2,2,3,3,4,4,5,5,6,6,7,7,8,8,9,9,10,10,11,11,12,12,13,13,
                          14,14,15,15]),
            wnRoundSetup('Sixteen Champion', wnPoints(2,0), 16, 'Quarter-Finals Champion',
                         [0,0,1,1,2,2,3,3,4,4,5,5,6,6,7,7]),
            wnRoundSetup('Quarter-Finals Champion', wnPoints(2,0), 8, 'Semi-Finals Champion',
                         [0,0,1,1,2,2,3,3], 'Quarter-Finals Consolation', [0,0,1,1,2,2,3,3]),
            wnRoundSetup('Semi-Finals Champion', wnPoints(2,3), 4, 'Finals Champion',
                         [0,0,1,1], 'Semi-Finals Consolation', [3,3,1,1]),
            wnRoundSetup('Finals Champion', wnPoints(2,9), 2, 'First Place', [0, 0]),
            wnRoundSetup('First Place', wnPoints(0,4), 1),
            
            wnRoundSetup('Quarter-Finals Consolation', wnPoints(1,0), 4,
                         'Semi-Finals Consolation', [0,0,2,2]),
            wnRoundSetup('Semi-Finals Consolation', wnPoints(1,3), 4, 'Finals Consolation',
                         [0,0,1,1], 'Finals Fifth', [0,0,1,1]),
            wnRoundSetup('Finals Consolation', wnPoints(1,4), 2, 'Third Place', [0,0]),
            wnRoundSetup('Third Place', wnPoints(0,2), 1),
            
            wnRoundSetup('Finals Fifth', wnPoints(0,0), 2, 'Fifth Place', [0,0]),
            wnRoundSetup('Fifth Place', wnPoints(0,2), 1)]

class wnCTChampionshipConfig:
  Name = 'Connecticut State Championships'
  Description = 'The bracket format used in the Connecticut State Division Championship tournaments. The outbracket has 32 seed slots, and double-elimination begins in the round of sixteen. There are six places.'
  Seeds = [1, 32, 17, 16, 9, 24, 25, 8, 5, 28, 21, 12, 13, 20, 29, 4,
           3, 30, 19, 14, 11, 22, 27, 6, 7, 26, 23, 10, 15, 18, 31, 2]
  Rounds = [wnRoundSetup('Rat-Tails Champion', wnPoints(0,0),
                         [1, 32, 17, 16, 9, 24, 25, 8, 5, 28, 21, 12, 13, 20, 29, 4,
                          3, 30, 19, 14, 11, 22, 27, 6, 7, 26, 23, 10, 15, 18, 31, 2],
                         'Sixteen Champion',
                         [0,0,1,1,2,2,3,3,4,4,5,5,6,6,7,7,8,8,9,9,10,10,11,11,12,12,13,13,
                          14,14,15,15]),
            wnRoundSetup('Sixteen Champion', wnPoints(2,0), 16, 'Quarter-Finals Champion',
                         [0,0,1,1,2,2,3,3,4,4,5,5,6,6,7,7], 'Rat-Tails Consolation',
                         [0,0,1,1,2,2,3,3,4,4,5,5,6,6,7,7]),
            wnRoundSetup('Quarter-Finals Champion', wnPoints(2,0), 8, 'Semi-Finals Champion',
                         [0,0,1,1,2,2,3,3], 'Eight Consolation', [7,7,5,5,3,3,1,1]),
            wnRoundSetup('Semi-Finals Champion', wnPoints(2,3), 4, 'Finals Champion',
                         [0,0,1,1], 'Semi-Finals Consolation', [1,1,3,3]),
            wnRoundSetup('Finals Champion', wnPoints(2,9), 2, 'First Place', [0, 0]),
            wnRoundSetup('First Place', wnPoints(0,4), 1),
            
            wnRoundSetup('Rat-Tails Consolation', wnPoints(1,0), 8,
                        'Eight Consolation', [0,0,2,2,4,4,6,6]),
            wnRoundSetup('Eight Consolation', wnPoints(1,0), 8,
                        'Quarter-Finals Consolation', [0,0,1,1,2,2,3,3]),
            wnRoundSetup('Quarter-Finals Consolation', wnPoints(1,0), 4,
                        'Semi-Finals Consolation', [0,0,2,2]),
            wnRoundSetup('Semi-Finals Consolation', wnPoints(1,3), 4, 'Finals Consolation',
                         [0,0,1,1], 'Finals Fifth', [0,0,1,1]),
            wnRoundSetup('Finals Consolation', wnPoints(1,4), 2, 'Third Place', [0,0]),
            wnRoundSetup('Third Place', wnPoints(0,2), 1),
            
            wnRoundSetup('Finals Fifth', wnPoints(0,0), 2, 'Fifth Place', [0,0]),
            wnRoundSetup('Fifth Place', wnPoints(0,2), 1)]
  
class wnCTOpenConfig:
  Name = 'Connecticut State Open'  
  Description = 'The bracket format used in the Connecticut State Open tournament. The outbracket has 16 seed slots, and double-elimination begins immediately. There are six places.'
  Seeds = [1, 16, 9, 8, 5, 12, 13, 4, 3, 14, 11, 6, 7, 10, 15, 2]
  Rounds = [wnRoundSetup('Sixteen Champion', wnPoints(2,0),
                         [1, 16, 9, 8, 5, 12, 13, 4, 3, 14, 11, 6, 7, 10, 15, 2],
                         'Quarter-Finals Champion', [0,0,1,1,2,2,3,3,4,4,5,5,6,6,7,7],
                         'Rat-Tails Consolation', [0,0,1,1,2,2,3,3,4,4,5,5,6,6,7,7]),
            wnRoundSetup('Quarter-Finals Champion', wnPoints(2,0), 8, 'Semi-Finals Champion',
                         [0,0,1,1,2,2,3,3], 'Eight Consolation', [7,7,5,5,3,3,1,1]),
            wnRoundSetup('Semi-Finals Champion', wnPoints(2,3), 4, 'Finals Champion',
                         [0,0,1,1], 'Semi-Finals Consolation', [1,1,3,3]),
            wnRoundSetup('Finals Champion', wnPoints(2,9), 2, 'First Place', [0, 0]),
            wnRoundSetup('First Place', wnPoints(0,4), 1),
            
            wnRoundSetup('Rat-Tails Consolation', wnPoints(1,0), 8,
                        'Eight Consolation', [0,0,2,2,4,4,6,6]),
            wnRoundSetup('Eight Consolation', wnPoints(1,0), 8,
                        'Quarter-Finals Consolation', [0,0,1,1,2,2,3,3]),
            wnRoundSetup('Quarter-Finals Consolation', wnPoints(1,0), 4,
                        'Semi-Finals Consolation', [0,0,2,2]),
            wnRoundSetup('Semi-Finals Consolation', wnPoints(1,3), 4, 'Finals Consolation',
                         [0,0,1,1], 'Finals Fifth', [0,0,1,1]),
            wnRoundSetup('Finals Consolation', wnPoints(1,4), 2, 'Third Place', [0,0]),
            wnRoundSetup('Third Place', wnPoints(0,2), 1),
            
            wnRoundSetup('Finals Fifth', wnPoints(0,0), 2, 'Fifth Place', [0,0]),
            wnRoundSetup('Fifth Place', wnPoints(0,2), 1)]  

if __name__ == '__main__':
  b = wnBuilder()
  print b.GetTournaments()
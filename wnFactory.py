from wnData import *
import new

class wnRoundSetup(object):
  def __init__(self, name, points, num_entries, next_win = None, next_lose = None,
               win_map = None, lose_map = None):
    self.Name = name
    self.Points = points
    self.NumEntries = num_entries
    self.NextWin = next_win
    self.NextLose = next_lose
    self.WinMap = win_map
    self.LoseMap = lose_map

class wnFactory(object):
  def GetTournaments(self):
    '''Return the tournaments currently supported.'''
    names =  ['wnBCInvitationalConfig']
  
  def Create(self, config, name, weights, team):
    '''Determine the type of tournament to create and then build it.'''
    tourn = wnTournament(name)
    
    #add the teams
    for t in teams:
      tourn.NewTeam(t)
      
    #build the weights
    for w_name in weights:
      w = tourn.NewWeightClass(w_name)

      #build the rounds
      for round in config.Rounds:
        r = w.NewRound(round.Name, round.Points)
        
        #build the entries
        r.NewEntries(round.NumEntries)

      #connect the rounds
      self.connectRounds(w, config.rounds)
    
    return tourn
  
  def connectRounds(self, weight, rounds):
    #cycle through all the rounds
    for round in rounds:
      #get the round
      this_round = weight.GetRound(round.Name)
      
      #get the win round
      win_round = weight.GetRound(round.NextWin)
      #and connect it
      this_round.SetNextWinRound(win_round, round.WinMap)
      
      #get the lose round
      lose_round = weight.GetRound(round.NextLose)
      #and connect it
      this_round.SetNextLoseRound(lose_round, round.LoseMap)    

class wnBCInvitationalConfig:
  Name = 'Bristol Central Invitational'
  Description = 'The bracket format used in the Bristol Central Invitational tournaments. The outbracket has 32 seed slots, and double-elimination begins in the quarter finals.'
  Rounds = [wnRoundSetup('Rat-Tails', wnPoints(0,0), 32, 'Sixteen Champion', range(32)),
            wnRoundSetup('Sixteen Champion', wnPoints(2,0), 16, 'Quarter-Finals Champion',
                        range(16)),
            wnRoundSetup('Quarter-Finals Champion', wnPoints(2,0), 8, 'Semi-Finals Champion',
                        'Semi-Finals Consolation', range(4), range(4)),
            wnRoundSetup('Semi-Finals Champion', wnPoints(2,0), 4, 'Finals Champion',
                        'Semi-Finals Consolation', [0,0,1,1], [3,3,0,0]),
            wnRoundSetup('Finals Champion', wnPoints(2,0), 2, 'First Place', [0, 0]),
            wnRoundSetup('First Place', wnPoints(0,0), 1),
            wnRoundSetup('Quarter-Finals Consolation', wnPoints(1,0), 4,
                        'Semi-Finals Consolation', [1,1,2,2]),
            wnRoundSetup('Semi-Finals Consolation', wnPoints(1,0), 4, 'Finals Consolation',
                        'Finals Fifth', [0,0,1,1], [0,0,1,1]),
            wnRoundSetup('Finals Consolation', wnPoints(1,0), 2, 'Third Place', [0,0]),
            wnRoundSetup('Third Place', wnPoints(0,0), 1),
            wnRoundSetup('Finals Fifth', wnPoints(0,0), 2, 'Fifth Place', [0,0]),
            wnRoundSetup('Fifth Place', wnPoints(0,0), 1)]

if __name__ == '__main__':
  f = wnFactory()
  #factory = wnFactoryBCInvite()
  #t = factory.Create(['95', '103', '112'],
              #                 ['Bristol Central', 'Bristol Eastern', 'Southington'])
  
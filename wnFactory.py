from wnData import *

class wnFactory:
  def Create(cls):
    pass
  
  Create = classmethod(Create)
  
class wnFactoryBCInvite(wnFactory):
  def __init__(self):
    self.rounds = [{'name' : 'Rat-Tails', 'points' : wnPoints(0,0), 'num_entries' : 32,
                    'next_win' : 'Sixteen Champion', 'win_map' : range(0,31)},

                   {'name' : 'Sixteen Champion', 'points' : wnPoints(2,0), 'num_entries' : 16,
                    'next_win' : 'Quarter-Finals Champion', 'win_map' : range(0,15)},
                   
                   {'name' : 'Quarter-Finals Champion', 'points' : wnPoints(2,0), 'num_entries' : 8,
                    'next_win' : 'Semi-Finals Champion', 'next_lose' : 'Semi-Finals Consolation',
                    'win_map' : range(0,3), 'lose_map' : range(0,3)},

                   {'name' : 'Semi-Finals Champion', 'points' : wnPoints(2,0), 'num_entries' : 4,
                    'next_win' : 'Finals Champion', 'next_lose' : 'Semi-Finals Consolation',
                    'win_map' : [0,1], 'lose_map' : [3,0]},

                   {'name' : 'Finals Champion', 'points' : wnPoints(2,0), 'num_entries' : 2,
                    'next_win' : 'First Place', 'win_map' : [0]},

                   {'name' : 'First Place', 'points' : wnPoints(0,0), 'num_entries' : 1},

                   {'name' : 'Quarter-Finals Consolation', 'points' : wnPoints(1,0),
                    'num_entries' : 4, 'next_win' : 'Semi-Finals Consolation',
                    'win_map': [1,2]},

                   {'name' : 'Semi-Finals Consolation', 'points' : wnPoints(1,0), 'num_entries' : 4,
                    'next_win' : 'Finals Consolation', 'next_lose' : 'Finals Fifth',
                    'win_map' : [0,1], 'lose_map' : [0,1]},

                   {'name' : 'Finals Consolation', 'points' : wnPoints(1,0), 'num_entries' : 2,
                    'next_win' : 'Third Place', 'win_map' : [0]},

                   {'name' : 'Third Place', 'points' : wnPoints(0,0), 'num_entries' : 1},

                   {'name' : 'Finals Fifth', 'points' : wnPoints(0,0), 'num_entries' : 2,
                    'next_win' : 'Fifth Place'},

                   {'name' : 'Fifth Place', 'points' : wnPoints(0,0), 'num_entries' : 1}]
  
  def Create(self, weights, teams):
    name = 'Bristol Central Invitational'
    description = 'The bracket format used in the Bristol Central Invitational tournaments. The outbracket has 32 seed slots, and double-elimination begins in the quarter finals.'
    tourn = wnTournament(name, description)
    
    #add the teams
    for t in teams:
      tourn.NewTeam(t)
      
    #build the weights
    for w_name in weights:
      w = tourn.NewWeightClass(w_name)

      #build the rounds
      for round in self.rounds:
        r = w.NewRound(round['name'], round['points'])
        
        #build the entries
        r.NewEntries(num_entries)

      #connect the rounds
      self.connectRounds(w)
    
    return tourn
  
  def connectRounds(self, weight):
    #cycle through all the rounds
    for round in self.rounds:
      #get the round
      this_round = weight.GetRound(round['name'])
      
      #get the win round
      win_round = weight.GetRound(round['next_win'])
      #and connect it
      this_round.SetNextWinRound(win_round, round['win_map'])
      
      #get the lose round
      lose_round = weight.GetRound(round['next_lose'])
      #and connect it
      this_round.SetNextWinRound(lose_round, round['lose_map'])    
    
class wnFactoryCTChamps(wnFactory):
  def Create(cls, weights, teams):
    pass
  
  Create = classmethod(Create)
  
if __name__ == '__main__':
  t = wnFactoryCTChamps.Create(['95', '103', '112'],
                               ['Bristol Central', 'Bristol Eastern', 'Southington'])
  pass
  
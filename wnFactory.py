from wnData import *

class wnFactory:
  def Create(cls):
    pass
  
  Create = classmethod(Create)
  
class wnFactoryCTChamps(wnFactory):
  def Create(cls, weights, teams):
    t = wnTournament()
    t.name = 'Bristol Central Invitational'
    t.description = 'The bracket format used in the Bristol Central Invitational tournaments. The outbracket has 32 seed slots, and double-elimination begins in the quarter finals.'
    t.teams = teams
    
    #build the rounds
    rounds = ['Rat-Tails', 'Sixteen Champion', 'Quarter-Finals Champion', 'Semi-Finals Champion',
              'Finals Champion', 'Champion', 'Quarter-Finals Consolation',
              'Semi-Finals Consolation', 'Finals Consolation', 'Third Place', 'Finals Fifth',
              'Fifth Place']    
  
    #build the weights
    for w_name in weights:
      w = t.NewWeightClass(w_name)

      #build the rounds
      for r_name in rounds:
        r = w.NewRound(r_name)
    
    return t
  
  Create = classmethod(Create)
  
class wnFactoryBCInvite(wnFactory):
  def Create(cls, weights, teams):
    pass
  
  Create = classmethod(Create)
  
if __name__ == '__main__':
  t = wnFactoryCTChamps.Create(['95', '103', '112'], ['Bristol Central', 'Bristol Eastern',
                                                      'Southington'])
  print vars(t)
  
from wnData import *

class wnFactory:
  def Create(cls):
    pass
  
  Create = classmethod(Create)
  
class wnFactoryCTChamps(wnFactory):
  def Create(cls, weights, teams):
    name = 'Bristol Central Invitational'
    description = 'The bracket format used in the Bristol Central Invitational tournaments. The outbracket has 32 seed slots, and double-elimination begins in the quarter finals.'
    tourn = wnTournament(name, description)
    
    #add the teams
    for t in teams:
      tourn.NewTeam(t)
    
    #build the rounds
    #round name, points (adv, place), entries
    rounds = [('Rat-Tails', wnPoints(0,0), 32),
              ('Sixteen Champion', wnPoints(2,0), 16),
              ('Quarter-Finals Champion', wnPoints(2,0), 8),
              ('Semi-Finals Champion', wnPoints(2,0), 4),
              ('Finals Champion', wnPoints(2,0), 2),
              ('First Place', wnPoints(0,0), 1),
              ('Quarter-Finals Consolation', wnPoints(1,0), 4),
              ('Semi-Finals Consolation', wnPoints(1,0), 4),
              ('Finals Consolation', wnPoints(1,0), 2),
              ('Third Place', wnPoints(0,0), 1),
              ('Finals Fifth', wnPoints(0,0), 2),
              ('Fifth Place', wnPoints(0,0), 1)]
  
    #build the weights
    for w_name in weights:
      w = tourn.NewWeightClass(w_name)

      #build the rounds
      for r_name, points, num_entries in rounds:
        r = w.NewRound(r_name, points)
        
        #build the entries
        r.NewEntries(num_entries)
        
    #connect the rounds
        
    
    return tourn
  
  Create = classmethod(Create)
  
class wnFactoryBCInvite(wnFactory):
  def Create(cls, weights, teams):
    pass
  
  Create = classmethod(Create)
  
if __name__ == '__main__':
  t = wnFactoryCTChamps.Create(['95', '103', '112'],
                               ['Bristol Central', 'Bristol Eastern', 'Southington'])
  print vars(t)
  
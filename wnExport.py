'''
The export module defines classes that support the export of tournament data to formats other than
the wrestling nerd format. This includes plain text files or HTML documents.'''

class wnExportPlainText(object):
  '''Class that exports team scores and place winners to a plain text file.'''
  def __init__(self, filename, tournament):
    self.file = file(filename, 'w')
    self.tournament = tournament
    
  def __del__(self):
    self.file.close()
    
  def Save(self):
    '''Save place winners, team scores, and fast fall winner.'''
    # write the name of the tournament
    self.file.write(self.tournament.Name+'\n\n')
    
    # save scores first
    self.file.write('--- Team Scores ---\n')
    scores = self.tournament.CalcScores()
    for i in range(len(scores)):
      text = '%d\t%.1f\t%s\n' % (i+1, scores[i][0], scores[i][1])
      self.file.write(text)
      
    self.file.write('\n')
      
    # now save all the place winners
    self.file.write('--- Place Winners ---\n')
    place_winners = self.tournament.GetPlaceWinners(self.tournament.Weights)
    for weight in place_winners:
      self.file.write(weight.Weight+'\n')
      for i in range(len(weight)):
        pw = weight[i]
        text = '%d %s, %s, %s\n' % (i+1, pw.Name, pw.Team, pw.Result)
        self.file.write(text)
        
      self.file.write('\n')
    
    # now save the fast fall leader
    self.file.write('--- Fastest Fall Winner ---\n')
    ff = self.tournament.CalcFastFall()
    try:
      leader = ff[0]
      text = '%s from %s\n%s lbs, %d pins, %s' % (leader.Name, leader.Team,
                                                  leader.Weight, leader.Pins, leader.TimeText)
      self.file.write(text)
    except:
      self.file.write('No winner')
'''
The printing module defines classes that manage dead-tree renderings of tournament data including
brackets, bouts, scores, and place winners.
'''

from wxPython.wx import *
from wnRenderer import *
import wnSettings
import time, math

class wnPrintFactory(object):
  def PrintPreview(cls, parent, tournament, type, weights, rounds=None, bracket_size=None):
    # make the proper printout object
    if type == 'Brackets':
      p1 = wnBracketPrintout(tournament, weights, bracket_size)
      p2 = wnBracketPrintout(tournament, weights, bracket_size)
    elif type == 'Scores':
      p1 = wnScorePrintout(tournament)
      p2 = wnScorePrintout(tournament)
    elif type == 'Bouts':
      p1 = wnBoutPrintout(tournament, weights, rounds)
      p2 = wnBoutPrintout(tournament, weights, rounds)
    elif type == 'Places':
      p1 = wnPlacesPrintout(tournament, weights)
      p2 = wnPlacesPrintout(tournament, weights)
    else:
      return

    # create the preview and make sure it's ok
    preview = wxPrintPreview(p1, p2)
    if not preview.Ok():
      return

    # create the preview frame and show the printout
    frame = wxPreviewFrame(preview, parent, 'Print preview')
    frame.Initialize()
    frame.Show(True)
    
  def Print(cls, parent, tournament, type, weights, rounds=None, bracket_size=None):
    # make the proper printout object
    if type == 'Brackets':
      po = wnBracketPrintout(tournament, weights, bracket_size)
    elif type == 'Scores':
      po = wnScorePrintout(tournament)
    elif type == 'Bouts':
      po = wnBoutPrintout(tournament, weights, rounds)
    elif type == 'Places':
      po = wnPlacesPrintout(tournament, weights)
    else:
      return
    
    # show the print dialog
    printer = wxPrinter()
    printer.Print(parent, po, True)
    
  PrintPreview = classmethod(PrintPreview)
  Print = classmethod(Print)

class wnBoutPrintout(wxPrintout):
  def __init__(self, tournament, weights, rounds):
    wxPrintout.__init__(self)
    
    # compute bouts and page length
    self.bouts = tournament.GetBouts(weights, rounds)
    self.pages = int(math.ceil(float(len(self.bouts))/2))
    
    # load the static bout bitmap
    self.bmp = wxBitmap(wnSettings.bout_bitmap_filename, wxBITMAP_TYPE_PNG)
    
  def HasPage(self, page):
    return (page <= self.pages)
  
  def GetPageInfo(self):
    return (1,self.pages,1,self.pages)
  
  def OnPrintPage(self, page):
    # get the  drawing context
    dc = self.GetDC()
    dc.SetUserScale(1.0, 1.0)    
    
    # add the margin to the bracket size
    max_w = self.bmp.GetWidth() + 2*wnSettings.print_margin_x
    max_h = self.bmp.GetHeight() + 2*wnSettings.print_margin_y
    
    # scale the drawing area to fit the page
    pw, ph = dc.GetSize()
    sx = float(pw)/float(max_w)
    sy = float(ph)/float(max_h)
    scale = min(sx, sy)
    dc.SetUserScale(scale, scale)
    
    # start the origin at the top and draw a line dividing the page
    dc.SetDeviceOrigin(wnSettings.print_margin_x, wnSettings.print_margin_y)    
    dc.DrawLine(0, self.bmp.GetHeight(), self.bmp.GetWidth(), self.bmp.GetHeight())
    dc.SetFont(wxFont(wnSettings.print_font_size, wxMODERN, wxNORMAL, wxNORMAL))
    
    # draw two bouts per page
    i = 0
    index = 2 * (page - 1)
    while(i < 2 and index < len(self.bouts)):
      # print the outline
      dc.DrawBitmap(self.bmp, 0, 0, False)
      
      # fill in the weight and round
      dc.DrawText(self.bouts[index].Weight, 220, 10)
      dc.DrawText(self.bouts[index].Round, 220, 40)
      
      # fill in the two wrestlers
      dc.DrawText(self.bouts[index].Wrestler1.Name, 3, 100)
      w, h = dc.GetTextExtent(self.bouts[index].Wrestler1.Name)
      dc.DrawText(self.bouts[index].Wrestler1.Team.Name, 3, 100+h)
      
      dc.DrawText(self.bouts[index].Wrestler2.Name, 3, 170)
      w, h = dc.GetTextExtent(self.bouts[index].Wrestler1.Name)
      dc.DrawText(self.bouts[index].Wrestler2.Team.Name, 3, 170+h)
      
      # increase the index and move to the bottom half of the page
      i += 1
      index += 1
      dc.SetDeviceOrigin(wnSettings.print_margin_x, wnSettings.print_margin_y+ph/2)
      
    
class wnPlacesPrintout(wxPrintout):
  def __init__(self, tournament, weights):
    wxPrintout.__init__(self)
    
    # store references
    self.tournament = tournament
    
    # get the place winners for the selected weights
    self.places = self.tournament.GetPlaceWinners(weights)
    
    # compute the number of pages
    self.pages = int(math.ceil(float(len(self.places))/wnSettings.print_place_weights_per_page))

  def HasPage(self, page):
    return (page <= self.pages)
  
  def GetPageInfo(self):
    return (1,self.pages,1,self.pages)
  
  def OnPrintPage(self, page):
    # get the  drawing context
    dc = self.GetDC()
    dc.SetUserScale(1.0, 1.0)
        
    # set the origin to incorporate the margin
    dc.SetDeviceOrigin(wnSettings.print_margin_x, wnSettings.print_margin_y)
    
    # print a header on each page
    title = self.tournament.Name + ' Place Winners'
    w, h = dc.GetTextExtent(title)
    dc.DrawText(title, 0, 0)
    
    # print the place winners for this page
    index = wnSettings.print_place_weights_per_page * (page-1)
    i = 0
    while (i < wnSettings.print_place_weights_per_page and index < len(self.places)):
      # print the weight info
      text = self.places[index].Weight
      dc.DrawText(text, 0, h)
      space = dc.GetTextExtent(text)
      h += space[1]
      
      # loop through the winners and print the results
      for j in range(len(self.places[index])):
        pw = self.places[index][j]
        text = str(j+1) + ' ' + pw.Name + ', ' + pw.Team + ', ' + str(pw.Result)
        dc.DrawText(text, 0, h)
        h += space[1]
      
      # increment position on the page, index, and counter
      h += space[1]
      index += 1
      i += 1
    
    return True

class wnScorePrintout(wxPrintout):
  def __init__(self, tournament):
    wxPrintout.__init__(self)
    
    # store references
    self.tournament = tournament
    
    # get the scores from the tournament
    self.scores = self.tournament.CalcScores()
    
    # compute the number of pages
    self.pages = int(math.ceil(float(len(self.scores))/wnSettings.print_scores_per_page))
    
  def HasPage(self, page):
    return (page <= self.pages)
  
  def GetPageInfo(self):
    return (1,self.pages,1,self.pages)
  
  def OnPrintPage(self, page):
    # get the  drawing context
    dc = self.GetDC()
    dc.SetUserScale(1.0, 1.0)
    
    # set the origin to incorporate the margin
    dc.SetDeviceOrigin(wnSettings.print_margin_x, wnSettings.print_margin_y)
    
    # print a header on each page
    title = self.tournament.Name + ' Team Scores'
    w, h = dc.GetTextExtent(title)
    dc.DrawText(title, 0, 0)
    
    # print the scores for this page
    index = wnSettings.print_scores_per_page * (page-1)
    i = 0
    while (i < wnSettings.print_scores_per_page and index < len(self.scores)):
      # get the team info      
      p = str(i+1)
      s = str(self.scores[i][0])
      t = str(self.scores[i][1])
      
      # print the team info
      text = p + ' '*(8-len(p)) + s + ' '*(8-len(s)) + t
      space = dc.GetTextExtent(text)
      dc.DrawText(text, 0, h)
      
      # increment position on page, counter, and index
      h += space[1]
      index += 1
      i += 1
    
    return True

class wnBracketPrintout(wxPrintout):
  def __init__(self, tournament, weights, bracket_size):
    wxPrintout.__init__(self)
    
    # store references
    self.tournament = tournament
    self.weights = weights
    self.bracket_size = bracket_size
    self.pages = len(self.weights)

  def HasPage(self, page):
    return (page <= self.pages)

  def GetPageInfo(self):
    return (1, self.pages, 1, self.pages)

  def OnPrintPage(self, page):
    # get the drawing context
    dc = self.GetDC()
    dc.SetUserScale(1.0, 1.0)
    
    # build a printer renderer
    printer = wnPrinter()
    printer.SetDC(dc)
    printer.ScaleToFit(self.bracket_size[0], self.bracket_size[1])
    
    # draw the header
    title = self.tournament.Name
    weight = self.weights[page-1]+' lbs'
    dc.SetFont(wxFont(wnSettings.print_heading_size, wxMODERN, wxNORMAL, wxBOLD))
    printer.DrawHeader(title, weight)
    dc.SetFont(wxFont(wnSettings.print_font_size, wxMODERN, wxNORMAL, wxNORMAL))
    
    # tell the tournament to print a bracket for the desired weight class
    self.tournament.Paint(printer, self.weights[page-1], True)
    
    return True
    
    
    # scale the drawing area to fit the page
    #pw, ph = dc.GetSize()
    #max_h = ph - wnSettings.print_margin_y*2
    #max_w = pw - wnSettings.print_margin_x*2
    #sx = float(pw)/float(max_w)
    #sy = float(ph)/float(max_h)
    #scale = min(sx, sy)
    #dc.SetUserScale(scale, scale)
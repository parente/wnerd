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
    #make the proper printout object
    if type == 'Brackets':
      po = wnBracketPrintout(tournament, weights, bracket_size)
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
    
    # add the margin to the bracket size
    max_w = 800 + 2*wnSettings.print_margin_x
    max_h = 500 + 2*wnSettings.print_margin_y
    
    # scale the drawing area to fit the page
    pw, ph = dc.GetSize()
    sx = float(pw)/float(max_w)
    sy = float(ph)/float(max_h)
    scale = min(sx, sy)
    dc.SetUserScale(scale, scale)
    
    # start the origin at the top and draw a line dividing the page
    dc.SetDeviceOrigin(wnSettings.print_margin_x, wnSettings.print_margin_y)    
    dc.DrawLine(0, 500, 800, 500)
    
    # draw two bouts per page
    i = 0
    index = 2 * (page - 1)
    while(i < 2 and index < len(self.bouts)):
      # print the outline
      dc.DrawBitmap(self.bmp, 0, 0, False)
      
      # fill in the weight and round
      
      # fill in the two wrestlers
      
      # increase the index and move to the bottom half of the page
      i += 1
      index += 1
      dc.SetDeviceOrigin(wnSettings.print_margin_x, wnSettings.print_margin_y+ph/2)
      
    
class wnPlacesPrintout(wxPrintout):
  pass

class wnScorePrintout(wxPrintout):
  def __init__(self, tournament):
    wxPrintout.__init__(self)
    
    # store references
    self.tournament = tournament
    
    # get the scores from the tournament
    self.scores = self.tournament.CalcScores()
    self.index = 0
    
    # store reusable fonts
    self.normal_font = wxFont(wnSettings.print_font_size, wxMODERN, wxNORMAL, wxNORMAL)
    self.heading_font = wxFont(wnSettings.print_heading_size, wxMODERN, wxNORMAL, wxBOLD)
  
  def HasPage(self, page):
    return (self.index != (len(self.scores)-1))
  
  def GetPageInfo(self):
    return (1,100,1,100)
  
  def OnPrintPage(self, page):
    # get the  drawing context
    dc = self.GetDC()
    
    # print the time
    dc.SetFont(self.normal_font)
    text = time.asctime()
    tw, th = dc.GetTextExtent(text)
    dc.DrawText(text, 0, 0)
    
    # set the origin properly
    pw, ph = dc.GetSize()
    ph -= wnSettings.print_margin_y*2
    pw -= wnSettings.print_margin_x*2
    dc.SetDeviceOrigin(wnSettings.print_margin_x, wnSettings.print_margin_y)
    
    # print a header on each page
    dc.SetFont(self.heading_font)
    title = self.tournament.Name + ' Team Scores'
    w, h = dc.GetTextExtent(title)
    dc.DrawText(title, 0, 0)
    dc.SetFont(self.normal_font)
    
    # print the scores in decending order all the way to the bottom of the page
    for i in range(self.index, len(self.scores)):
      if h >= ph: break
      
      p = str(i+1)
      s = str(self.scores[i][0])
      t = str(self.scores[i][1])
      
      text = p + ' '*(8-len(p)) + s + ' '*(8-len(s)) + t
      space = dc.GetTextExtent(text)
      dc.DrawText(text, 0, h)
      h += space[1]
      self.index += 1
    
    return True

class wnBracketPrintout(wxPrintout):
  def __init__(self, tournament, weights, bracket_size):
    wxPrintout.__init__(self)
    
    # store references
    self.tournament = tournament
    self.weights = weights
    self.bracket_size = bracket_size

    # create fonts    
    self.normal_font = wxFont(wnSettings.print_font_size, wxMODERN, wxNORMAL, wxNORMAL)
    self.heading_font = wxFont(wnSettings.print_heading_size, wxMODERN, wxNORMAL, wxBOLD)

  def HasPage(self, page):
    return (page <= len(self.weights))

  def GetPageInfo(self):
    return (1, len(self.weights), 1, len(self.weights))

  def OnPrintPage(self, page):
    # get the drawing context
    dc = self.GetDC()
    
    # print the time
    dc.SetFont(self.normal_font)
    text = time.asctime()
    tw, th = dc.GetTextExtent(text)
    dc.DrawText(text, 0, 0)
    
    # build a printer renderer
    printer = wnPrinter()
    printer.SetDC(dc)
    printer.ScaleToFit(self.bracket_size[0], self.bracket_size[1])
    
    # draw the header
    title = self.tournament.Name
    weight = self.weights[page-1]+' lbs'
    dc.SetFont(self.heading_font)
    printer.DrawHeader(title, weight)
    dc.SetFont(self.normal_font)
    
    # tell the tournament to print a bracket for the desired weight class
    self.tournament.Paint(printer, self.weights[page-1], True)
    
    return True
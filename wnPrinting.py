'''
The printing module defines classes that manage dead-tree renderings of tournament data including
brackets, bouts, scores, and place winners.
'''

from wxPython.wx import *
from wnRenderer import *
import wnSettings
import time

class wnPrintFactory(object):
  def PrintPreview(cls, parent, tournament, type, weights, rounds=None, bracket_size=None):
    # make the proper printout object
    if type == 'Brackets':
      p1 = wnBracketPrintout(tournament, weights, bracket_size)
      p2 = wnBracketPrintout(tournament, weights, bracket_size)
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
  pass

class wnPlacesPrintout(wxPrintout):
  pass

class wnScoresPrintout(wxPrintout):
  pass

class wnBracketPrintout(wxPrintout):
  def __init__(self, tournament, weights, bracket_size):
    wxPrintout.__init__(self)
    
    # store references
    self.tournament = tournament
    self.weights = weights
    self.bracket_size = bracket_size

  #def OnBeginDocument(self, start, end):
  #  return self.base_OnBeginDocument(start, end)
  #
  #def OnEndDocument(self):
  #  self.base_OnEndDocument()
  #
  #def OnBeginPrinting(self):
  #  self.base_OnBeginPrinting()
  #
  #def OnEndPrinting(self):
  #  self.base_OnEndPrinting()
  #
  #def OnPreparePrinting(self):
  #  self.base_OnPreparePrinting()

  def HasPage(self, page):
    return (page <= len(self.weights))

  def GetPageInfo(self):
    return (1, len(self.weights), 1, len(self.weights))

  def OnPrintPage(self, page):
    # get the drawing context
    dc = self.GetDC()
    
    # build a printer renderer
    printer = wnPrinter()
    printer.SetDC(dc)
    printer.ScaleToFit(self.bracket_size[0], self.bracket_size[1])
    
    # draw the header
    title = self.tournament.Name
    weight = self.weights[page-1]+' lbs'
    printer.DrawHeader(title, weight)
    
    # tell the tournament to print a bracket for the desired weight class
    self.tournament.Paint(printer, self.weights[page-1], True)
    
    return True
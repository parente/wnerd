# setup.py
from distutils.core import setup
import py2exe

setup(name="WrestlingNerd",
      author="Peter Parente",
      author_email="parente@cs.unc.edu",
      url="http://wnerd.sourceforge.net",
      description="Wrestling Nerd: Wrestling tournament management",
      scripts=["wnUI.py"],
      data_files=[("WrestlingNerd_wdr",
                   ["WrestlingNerd_wdr/bout.png", "WrestlingNerd_wdr/LogoBitmaps_0.png"]),
                  ("",
                   ["LICENSE.txt"])]
)

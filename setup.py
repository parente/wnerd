# setup.py
from distutils.core import setup
import py2exe

setup(name='WrestlingNerd',
      version='3.2',
      author='Peter Parente',
      author_email='parente@cs.unc.edu',
      url='http://wnerd.sourceforge.net',
      description='Wrestling Nerd: Wrestling tournament management software',
      options = {'py2exe': {'compressed': 1, 'optimize': 2}},      
      windows = [{'script': 'WrestlingNerd.py', 'icon_resources': [(1, 'WrestlingNerd_wdr/nerd.ico')]}],
      data_files=[('WrestlingNerd_wdr', ['WrestlingNerd_wdr/bout.png', 'WrestlingNerd_wdr/LogoBitmaps_0.png', 'WrestlingNerd_wdr/nerd16.ico']),
                  ('', ['LICENSE.txt']),
                  ('layouts', ['layouts/CTOpen.yml', 'layouts/CTStates.yml', 'layouts/BCInvite.yml'])]
)

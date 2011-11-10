#!/usr/bin/env python

from distutils2.core import setup, find_packages

setup(name='pyspread',
      version='0.1.3',
      summary='Python Spreadsheet',
      keywords=['spreadsheet', 'pyspread'],
      author='Martin Manns',
      author_email='mmanns@gmx.net',
      home_page='http://pyspread.sourceforge.net',
      license='GPL v3 :: GNU General Public License',
      packages=find_packages(),
      requires=['numpy (>=1.1)', 'wx (>=2.8.10)'],
      scripts=['pyspread'],
      package_dir={'': ''},
      package_data={'':
        ['share/icons/*.png',
         'share/icons/Tango/24x24/actions/*.png', 
         'share/icons/Tango/24x24/toggles/*.png', 
         'share/icons/Tango/24x24/toggles/*.xpm',
         'doc/help/*.html', 'doc/help/images/*.png',
         'COPYING', 'thanks', 'faq', 'authors']},
      data_files=[ \
        ('', ['examples/*.py']),
      ],
      classifiers=[ \
        'Development Status :: 4 - Beta',
        'Environment :: X11 Applications :: GTK',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Office/Business :: Financial :: Spreadsheet',
      ],
)

#!/usr/bin/env python

from distutils.core import setup

setup(name='SFTPKeyManager',
      version='0.1.1',
      description='SFTP Key Manager',
      long_description = "My SFTP Key Manager",
      author="Konstantin vz'One Enchant",
      author_email='sirkonst@gmail.com',
      url='http://wiki.enchtex.info',
      packages=[ 'src', ],
      scripts=['src/skeyctl.py'],
     )
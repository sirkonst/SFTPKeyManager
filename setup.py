      #!/usr/bin/env python

from setuptools import setup

setup(name='SFTPKeyManager',
      version='0.1.1',
      description='SFTP Key Manager',
      long_description = "My SFTP Key Manager",
      author="Konstantin vz'One Enchant",
      author_email='sirkonst@gmail.com',
      url='http://wiki.enchtex.info',
      packages = ['SFTPKeyManager'],
      package_dir = {'SFTPKeyManager': 'src'},
      entry_points = {
                      'console_scripts': ['skeyctl = SFTPKeyManager.cli:main']
                      },        
     )
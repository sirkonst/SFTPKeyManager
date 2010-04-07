# -*- coding: utf-8 -*-

import os
import re

class SFTPKey:
    """ Класс работы с sftp ключами """
    re_username = re.compile(r' (\S+@\S+)"$')
    
    def __init__(self, filekey):
        """ Файл с ключом (ключами) """
        self.filekey = os.path.abspath(filekey)
    
    def getusernames(self):
        """ Получить список имен пользователей из файла ключей """
        users = []
        with open(self.filekey, 'r') as f:
            new = False
            for line in f.readlines():
                if line == '---- BEGIN SSH2 PUBLIC KEY ----\n':
                    new = True
                    continue
                if new:
                    new = False
                    s = self.re_username.search(line)
                    if s:
                        users.append(str(s.groups()[0]))
        return users

    def getrawkey(self, username):
        """ Получить текст ключа для пользователя """
        with open(self.filekey, 'r') as f:
            new = False
            userfound = False
            for line in f.readlines():
                if line == '---- BEGIN SSH2 PUBLIC KEY ----\n':
                    new = True
                    continue
                if new:
                    new = False
                    s = self.re_username.search(line)
                    if s:
                        if str(s.groups()[0]) == username:
                            userfound = True
                            rawkey = '---- BEGIN SSH2 PUBLIC KEY ----\n'
                if userfound:
                    if not line == '---- END SSH2 PUBLIC KEY ----\n':
                        rawkey += line
                    else:
                        rawkey += '---- END SSH2 PUBLIC KEY ----\n'
                        userfound = False
                        new = False
            return rawkey

    def writekey(self, keytext):
            with open(self.filekey, 'a') as f:
                f.writelines(keytext)

        
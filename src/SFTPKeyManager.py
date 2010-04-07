# -*- coding: utf-8 -*-

'''
Created on 30.03.2010

@author: konst
'''

import os

from SFTPKey import SFTPKey

defaultkeypath = "/etc/proftpd/accounts/sftp/keys/"
defaultuserpath = "/etc/proftpd/accounts/sftp/users/"

# Иерархтя ошибок

class SFTPKeyManagerError (Exception):
    """ Общая неопределенная ошибка """
    pass
class E_KEY_NOT_FOUND (SFTPKeyManagerError):
    """ Ключ не найден """
    pass
class E_KEY_ALREADY_ASSIGNED (SFTPKeyManagerError):
    """ Ключ уже назначен """
    pass
class E_FILE_NOT_FOUND (SFTPKeyManagerError):
    """ Файл не найден """
    pass

def keylist():
    """"
    Возвращает словать в формате: имя пользователя ключа: файл ключа 
    """
    path = defaultkeypath
    files = os.listdir(path)
    users = {}
    for filename in files:
        sftp = SFTPKey(path+filename)
        for u in sftp.getusernames():
                users[u] = sftp.filekey
    return users

def useraccesslist():
    """
    Возращает словать в формате: имя пользователя: (список: ключей доступа)
    """
    path = defaultuserpath
    files = os.listdir(path)
    users = {}
    for filename in files:
        if os.path.isfile(path+filename):
            sftp = SFTPKey(path+filename)
            users[filename] = sftp.getusernames()
    return users

def addaccess(username, userkeyname):
    ''' Разрешает доступ к пользователю username по ключу userkeyname '''
    klist = keylist()
    kaccess = useraccesslist()
    if not klist.has_key(userkeyname):
        raise E_KEY_NOT_FOUND
    if kaccess.has_key(username):
        if userkeyname in kaccess[username]:
            raise E_KEY_ALREADY_ASSIGNED
    with open(defaultuserpath+'/'+username, 'a') as f:
        rawkey = SFTPKey(klist[userkeyname]).getrawkey(userkeyname)
        f.write(rawkey)
        return True
    
def removeaccess(username, userkeyname):
    ''' Удаления достопа к пользователю по ключу '''
    f_name = defaultuserpath+'/'+username
    if not os.path.isfile(f_name):
        raise E_FILE_NOT_FOUND
    sftp = SFTPKey(f_name)
    access = sftp.getusernames()
    if userkeyname in access:
        access.remove(userkeyname)
    else:
        raise E_KEY_NOT_FOUND
    if access:
        os.remove(f_name)
        for acc in access:
            addaccess(username, acc)
        return True
    else:
        open(f_name, 'w').close()
        return True

def addnewkey(keytext):
    """ Добавление нового ключа из keytext """
    name = ""
    for line in keytext.split('\n'):
        s = SFTPKey.re_username.search(line)
        if s:
            name = s.groups()[0]
            break
    if name != "":
        klist = keylist()
        if name in klist:
            raise E_KEY_ALREADY_ASSIGNED
        else:
            skey = SFTPKey( os.path.join(defaultkeypath, name) )
            skey.writekey(keytext)
            return {name: skey.filekey}
    else:
        raise E_KEY_NOT_FOUND

def zerokey(key):
    """ Оннулировать все доступы по ключу. Возвращает число отметенных доступов """
    keys = useraccesslist()
    count = 0
    for u in keys:
        if key in keys[u]:
            removeaccess(u, key)
            count += 1
    return count

if __name__ == '__main__':
    addaccess("test-site.kolos", "konst@gentoo-book")
    addaccess("test-site.kolos", "test@test")
    removeaccess("test-site.kolos", "test@test")

# -*- coding: utf-8 -*-

################ Общие модули ################

import os
import re

################ Переменные ################

defaultkeypath = "/etc/proftpd/accounts/sftp/keys/"
defaultuserpath = "/etc/proftpd/accounts/sftp/users/"

re_username = re.compile(r' (\S+@\S+)"$')

################ Ошибки ################ 

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

################ Логика ################ 

def read_sftp_names(file):
    """ Чтение из файла file списка имен sftp ключей """
    if not os.path.isfile(file):
        raise E_FILE_NOT_FOUND
    # Выделение имени
    _gcu = lambda text:  re_username.search(text).groups()[0]
    
    with open(file, 'r') as f:
        return [_gcu(f.next()) for line in f if line == '---- BEGIN SSH2 PUBLIC KEY ----\n']

def _get_key(name, i_text, ctext):
    key = ['---- BEGIN SSH2 PUBLIC KEY ----', ctext.strip('\n')]
    for line in i_text:
        line = line.strip('\n')
        if line != '---- END SSH2 PUBLIC KEY ----':
            key.append(line)
        else:
            break
    key.append('---- END SSH2 PUBLIC KEY ----\n')
    return (name, '\n'.join(key))

def read_sftp_key(file, keyname):
    """ Чтение SFTP ключа из файла file по имени keyname """
    if not os.path.isfile(file):
        raise E_FILE_NOT_FOUND
    # Выделение имени и исходнос строки (Comment)
    _gcu = lambda text:  (re_username.search(text).groups()[0], text)

    with open(file, 'r') as f:
        for name, text in (_gcu(f.next()) for line in f if line == '---- BEGIN SSH2 PUBLIC KEY ----\n'):
            if name == keyname:
                key = _get_key(name, f, text)
                break
    return key[1]

def read_sftp_key_old(file, keyname):
    """ Чтение SFTP ключа из файла file по имени keyname """
    # Выделение имени и исходнос строки (Comment)
    _gcu = lambda text:  (re_username.search(text).groups()[0], text)
    # Выделение ключа c Comment
    _grk = lambda f, text: text + ''.join(line for line in f if line != '---- END SSH2 PUBLIC KEY ----\n')
    with open(file, 'r') as f:
        key = [_grk(f, text) for name, text in (_gcu(f.next()) for line in f if line == '---- BEGIN SSH2 PUBLIC KEY ----\n') if name == keyname]
    return '---- BEGIN SSH2 PUBLIC KEY ----\n%s---- END SSH2 PUBLIC KEY ----\n' % key[0]

def keylist():
    """ Возвращает словать в формате: имя пользователя ключа -> файл ключа  """
    dict = {}
    for file in (file for file in os.listdir(defaultkeypath)
                 if os.path.isfile( os.path.join(defaultkeypath, file) )
                 ):
        filename = os.path.abspath(os.path.join(defaultkeypath, file))
        for name in read_sftp_names(filename):
            dict[name] = filename
    return dict

def ftpuseraccesslist():
    """ Возращает словать в формате: имя пользователя ftp -> (список ключей доступа) """
    dict = {}
    for file in (file for file in os.listdir(defaultuserpath)
                 if os.path.isfile(os.path.join(defaultuserpath, file))
                 ):
        filename = os.path.abspath(os.path.join(defaultuserpath, file))
        dict[file] = read_sftp_names(filename)
    return dict

def addaccess(ftpuser, keyname):
    """ Разрешает доступ к пользователю ftpuser по ключу keyname """
    keys = keylist()
    filename = os.path.join(defaultuserpath, ftpuser)
    if keyname not in keys:
        raise E_KEY_NOT_FOUND
    if os.path.isfile(filename) and keyname in read_sftp_names(filename):
        raise E_KEY_ALREADY_ASSIGNED
    with open(os.path.join(filename), 'a') as f:
        f.write(read_sftp_key(keys[keyname], keyname))
        return True

def removeaccess(ftpuser, keyname):
    """ Удаления достопа к пользователю по ключу """
    filename = os.path.join(defaultuserpath, ftpuser)
    keys = read_sftp_names(filename)
    if keyname not in keys:
        raise E_KEY_NOT_FOUND
    keys.remove(keyname)
    if keys:
        os.remove(filename)
        [addaccess(ftpuser, key) for key in keys]
        return True
    else:
        open(filename, 'w').close()
        return True

def zerokey(keyname):
    """ Оннулировать все доступы по ключу. Возвращает список пользователей где был удален ключ """
    keys = ftpuseraccesslist()
    return [uftp for ret, uftp in 
            ((removeaccess(uftp, keyname), uftp) 
                for uftp in keys if keyname in keys[uftp])
            ]

def safenewkeys(text):
    """ Сохраняет ключи в файлы. Возвращает словарь - 'имя ключа': 'путь к файлу' """
    dict = {}
    i_text = iter(text.splitlines())
    # Выделение имени и исходной строки (Comment)
    _gcu = lambda text: ((re_username.search(text).groups()[0]), text)

    for name, keytext in (_get_key(name, i_text, ctext) for name, ctext in 
                      (_gcu(i_text.next()) for line in i_text if line == '---- BEGIN SSH2 PUBLIC KEY ----')
                    ):
        filename = os.path.join(defaultkeypath, name)
        if os.path.isfile(filename):
            raise E_KEY_ALREADY_ASSIGNED, (name, filename)
        else:
            with open(filename, 'w') as f:
                f.write(keytext)
                dict[name] = filename
    return dict

if __name__ == '__main__':
    #addaccess('corp.kolos', 'new@test.my')
    #addaccess('corp.kolos', 'test@test')
    #addaccess('test-site', 'new@test.my')
    #addaccess('test-site', 'test@test')
    #removeaccess('corp.kolos', 'new@test.my')
    #print ftpuseraccesslist()
    #print zerokey('test@test')
    #print ftpuseraccesslist()
    print read_sftp_key('/home/konst/devel/eclipse/workspace/KeyManager/test/authorized_keys/rsa.pub/multitest', 'new@test.my')

#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 30.03.2010

@author: konst

CLI интерфейс
'''

from optparse import OptionParser
import SFTPKeyManager as SKM

#SKM.defaultkeypath = "../test/authorized_keys/rsa.pub/"
#SKM.defaultuserpath = "../test/authorized_keys/"

def opt_key_list(verbose=False):
    keys = SKM.keylist()
    print 'Список доступных ключей:'
    for k in keys:
        print verbose and '\t* %s (%s)' % (k, keys[k]) or '\t* ', k

def opt_user_list():
    users = SKM.useraccesslist()
    print 'Список пользователей (ключи):'
    for u in users:
        print '\t* %s (%s)' % (u, ", ".join(users[u]))

def opt_append_access(username, userkeynames):
    for key in userkeynames:
        try:
            if SKM.addaccess(username, key):
                print "Доступ к '%s' по ключу '%s добавлен." % (username, key)
        except SKM.E_KEY_NOT_FOUND:
            print "Ошибка: ключ '%s' не найден." % key
            exit(1)
        except SKM.E_KEY_ALREADY_ASSIGNED:
            print "Предупреждение: доступ по ключу '%s' уже предоставлен." % key

def opt_remove_access(username, userkeynames):
    for key in userkeynames:
        try:
            if SKM.removeaccess(username, key):
                print "Доступ по ключу '%s удален." % key
        except SKM.E_FILE_NOT_FOUND:
            print "Ошибка: файл пользователя '%s' не найден." % username
            exit(1)    
        except SKM.E_KEY_NOT_FOUND:
            print "Предупреждение: доступ по ключу '%s' отсутствует." % key

def opt_new_key(key, verbose=False):
    try:
        ret = SKM.addnewkey(key)
        if verbose:
            print '\n'.join( ["Добавлен новый ключ '%s' (%s)." % (name, file) for name, file in ret.items()] )
        else:
            print '\n'.join( ["Добавлен новый ключ '%s'." % name for name in ret.keys()] )
    except SKM.E_KEY_ALREADY_ASSIGNED:
        print 'Ошибка: ключ уже был добавлен.'
        exit(1) 
    except SKM.E_KEY_NOT_FOUND:
        print 'Ошибка: неправильный ключ.'
        exit(1)

def opt_zero_key(keys):
    for key in keys:
        if SKM.zerokey(key):
            print "Удалены все доступы по ключу '%s'." % key 

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-v', '--verbose', action='store_true', dest='verbose', default=False, help=u'Включить подробный вывод')
    parser.add_option('-k', '--key-list', action='store_true', dest='key_list', help=u'Список ключей')
    parser.add_option('-u', '--user-list', action='store_true', dest='user_list', help=u'Список пользователей')
    parser.add_option('-a', '--append-access', dest='append_access', metavar='USER', help=u'Добавить к пользователю доступ по ключу')
    parser.add_option('-r', '--remove-access', dest='remove_access', metavar='USER', help=u'Удалить доступ к пользователю по ключу')
    parser.add_option('-n', '--new-key', action='store_true', dest='new_key', help=u'Добавить новый ключ. Чтение с stdin.')
    parser.add_option('-z', '--zero', action='store_true', help=u'Оннулировать все доступы по ключу')
    (options, args) = parser.parse_args()
    
    import sys
    if len(sys.argv[1:]) == 0:
        parser.print_help()
    
    if options.zero:
        opt_zero_key(args)
        exit(0)
    if options.new_key:
        from sys import stdin
        s = stdin.readlines()
        opt_new_key("".join(s), options.verbose)
        exit()
    if options.append_access:
        opt_append_access(options.append_access, args)
        exit()
    if options.remove_access:
        opt_remove_access(options.remove_access, args)
        exit()
    if options.key_list:
        opt_key_list(options.verbose)
    if options.user_list:
        opt_user_list()

    
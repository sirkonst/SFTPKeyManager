#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 30.03.2010

@author: konst

CLI интерфейс
'''
################ Общие модули ################

import sys
import fileinput
from optparse import OptionParser
import SFTPKeyManager2 as skman

################ Переменные ################

# Отладка
skman.defaultkeypath = "../test/authorized_keys/rsa.pub/"
skman.defaultuserpath = "../test/authorized_keys/"

################ Логика ################

def opt_key_list(verbose=False):
    keys = skman.keylist()
    print 'Список доступных ключей:'
    for k in keys:
        print verbose and '\t* %s (%s)' % (k, keys[k]) or '\t* %s' % k

def opt_user_list():
    users = skman.ftpuseraccesslist()
    print 'Список пользователей (ключи):'
    for u in users:
        print '\t* %s (%s)' % (u, ", ".join(users[u]))

def opt_append_access(username, userkeynames):
    for key in userkeynames:
        try:
            if skman.addaccess(username, key):
                print "Доступ к '%s' по ключу '%s добавлен." % (username, key)
        except skman.E_KEY_NOT_FOUND:
            print "Ошибка: ключ '%s' не найден." % key
            exit(1)
        except skman.E_KEY_ALREADY_ASSIGNED:
            print "Предупреждение: доступ по ключу '%s' уже предоставлен." % key

def opt_remove_access(username, userkeynames):
    for key in userkeynames:
        try:
            if skman.removeaccess(username, key):
                print "Доступ по ключу '%s удален." % key
        except skman.E_FILE_NOT_FOUND:
            print "Ошибка: файл пользователя '%s' не найден." % username
            exit(1)    
        except skman.E_KEY_NOT_FOUND:
            print "Предупреждение: доступ по ключу '%s' отсутствует." % key

def opt_zero_key(keys):
    print '\n'.join("Доступ по ключу '%s' удален из %s" % (key, skman.zerokey(key)) for key in keys)

def opt_new_key(text):
    try:
        print '\n'.join("Ключ '%s' сохранен в файл '%s'." % (key, file) for key, file in skman.safenewkeys(text).items())
    except skman.E_KEY_ALREADY_ASSIGNED, (keyname, file):
        print "Ошибка: записи ключа '%s', файл '%s' уже существует." % (keyname, file)
        exit(1)

def main():
    parser = OptionParser()
    parser.add_option('-v', '--verbose', action='store_true', dest='verbose', default=False, help=u'Включить подробный вывод')
    parser.add_option('-k', '--key-list', action='store_true', dest='key_list', help=u'Список ключей')
    parser.add_option('-u', '--user-list', action='store_true', dest='user_list', help=u'Список пользователей')
    parser.add_option('-a', '--append-access', dest='append_access', metavar='USER', help=u'Добавить к пользователю доступ по ключу')
    parser.add_option('-r', '--remove-access', dest='remove_access', metavar='USER', help=u'Удалить доступ к пользователю по ключу')
    parser.add_option('-n', '--new-key', action='store_true', dest='new_key', help=u'Добавить новый ключ из файла(ов) или стандартного ввода')
    parser.add_option('-z', '--zero', action='store_true', help=u'Оннулировать все доступы по ключу(ам)')
    (options, args) = parser.parse_args()
    
    
    if len(sys.argv[1:]) == 0:
        parser.print_help()
    if options.zero:
        opt_zero_key(args)
        exit(0)
    if options.new_key:
        opt_new_key(''.join(line for line in fileinput.input(sys.argv[2:])))
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

if __name__ == '__main__':
    main()

    
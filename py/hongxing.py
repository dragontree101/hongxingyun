# -*- coding: utf-8 -*-
import md5
import requests
import json
import csv
import random
import time
import threading
import sys
import math


def readCsv(account_path):
    with open(account_path) as f:
        csv_reader = csv.reader(f)
        account_list = []
        for row in csv_reader:
            dict = {}
            dict['username'] = row[0]
            m1 = md5.new()
            m1.update(row[1])
            password = m1.hexdigest()
            print 'row 1 is %s, password is %s' % (
                row[1], password)
            dict['password'] = password
            account_list.append(dict)
        return account_list


def readResourceCsv(resource_path):
    with open(resource_path) as f:
        csv_reader = csv.reader(f)
        resource_list = []
        for row in csv_reader:
            dict = {}
            dict['word'] = row[0]
            dict['voice'] = row[1]
            dict['video'] = row[2]
            resource_list.append(dict)
        return resource_list


def login(username, password):
    try:
        payload = {'phoneNum': username,
                   'password': password}
        token = requests.post(
            'http://api.hxw.gov.cn/redstar-http/api/partyMember/login', params=payload).json()
        if token.has_key('token'):
            return token['token']
        return None
    except Exception as err:
        print(err)
        return None


def getUserInfo(token):
    try:
        payload = {'token': token}
        userInfo = requests.get(
            'http://api.hxw.gov.cn/redstar-http/api/partyMember/getCurrentLoginUser', params=payload).json()
        return userInfo
    except Exception as err:
        print(err)
        return None


def addMemberIntegral(token, userInfo, resource, resourceType):
    try:
        payload = {
            "memberId": userInfo['userId'],
            "orgCode": userInfo['organization']['orgCode'],
            "resourceId": resource,
            "configName": resourceType,
            "resourceType": resourceType
        }
        result = requests.post(
            'http://api.hxw.gov.cn/redstar-http/api/integral/addMemberIntegral?token=' + token, json=payload)
        print 'user id is %s result is %s' % (
            userInfo['userId'], result.text)
        return result.text
    except Exception as err:
        print 'add member integral has err, user id is %s result is %s' % (
            userInfo['userId'], result.text)
        print(err)
        return 'failure'


def notEmpty(s):
    return s and s.strip()


def chunks(arr, m):
    print 'arr size is %s m is %s ' % (len(arr), m)
    return [arr[i::m] for i in xrange(m)]


def mainRun(account_list, resource_list):
    for account in account_list:
        time.sleep(random.randint(1, 5))
        token = login(
            account['username'], account['password'])
        if token is None:
            print 'failure!! token is null, username is %s, password is %s' % (
                account['username'], account['password'])
            continue

        userInfo = getUserInfo(token)
        if userInfo is None:
            print 'failure!! user info is null, username is %s, password is %s' % (
                account['username'], account['password'])
            continue

        resource_word = filter(
            notEmpty, [d['word'] for d in resource_list])
        resource_word_slice = random.sample(
            resource_word, 20)
        # print resource_word_slice
        for resouce in resource_word_slice:
            time.sleep(30)
            result = addMemberIntegral(
                token, userInfo, resouce, 'mryd')
            if result == 'failure':
                print 'username is %s addMemberIntegral word failure' % account[
                    'username']
                break
            pass

        resource_voice = filter(
            notEmpty, [d['voice'] for d in resource_list])
        resource_voice_slice = random.sample(
            resource_voice, 10)
        # print resource_voice_slice
        for resouce in resource_voice_slice:
            time.sleep(10)
            result = addMemberIntegral(
                token, userInfo, resouce, 'hxyt')
            if result == 'failure':
                print 'username is %s addMemberIntegral voice failure' % account[
                    'username']
                break
            pass

        resource_video = filter(
            notEmpty, [d['video'] for d in resource_list])
        resource_video_slice = random.sample(
            resource_video, 10)
        # print resource_video_slice
        for resouce in resource_video_slice:
            time.sleep(10)
            result = addMemberIntegral(
                token, userInfo, resouce, 'wsp')
            if result == 'failure':
                print 'username is %s addMemberIntegral video failure' % account[
                    'username']
                break
            pass

        print 'username is %s is done' % account['username']


if __name__ == '__main__':
    if len(sys.argv) == 2:
        thread_num = sys.argv[1]
        account_path = 'account.csv'
        resource_path = 'resource.csv'
    elif len(sys.argv) == 4:
        thread_num = sys.argv[1]
        account_path = sys.argv[2]
        resource_path = sys.argv[3]
    else:
        print 'input num is not 2 and 4'
        exit(1)

    print 'hongxing program is begin ... thread num is %s, account path is %s, resource path is %s' % (
        thread_num, account_path, resource_path)

    account_list = readCsv(account_path)
    resource_list = readResourceCsv(resource_path)
    thread_account_list = chunks(
        account_list, int(thread_num))

    print 'start thread ....'

    thread_list = []
    for i in range(int(thread_num)):
        t = threading.Thread(target=mainRun, args=(
            thread_account_list[i], resource_list,))
        t.start()
        thread_list.append(t)
    print 'thread num is %d' % (len(thread_list))

    for t in thread_list:
        t.join()

    print 'python shell is done'

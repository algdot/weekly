#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random
import logging
import sys
from slackclient import SlackClient
import time

class WeeklyNote:

    def __init__(self, user):
        self.i = 0;
        self.projects = [];
        self.user = user;

    def write(self, text, message_channel) :
        print text;
        if self.i % 4 == 0 :
            if self.i /4 > 0 :
                client.rtm_send_message(message_channel, '还有其他项目吗？如果有项目是？')
                return True
            client.rtm_send_message(message_channel, 'Hi, 我是周报小助手: \n 请问你本周做的项目是？')
            self.i +=1
            return True
        if self.i % 4 == 1 :
            client.rtm_send_message(message_channel, '{} 的进度？【格式：开发/测试/上线阶段：80%】'.format(text))
            self.i +=1
            self.projects.append({'name' : text})
            return True
        if self.i % 4 == 2 :
            client.rtm_send_message(message_channel, '{} 的本周进展是？【格式：1：xx \n 2: xx \n 】'.format(self.projects[self.i/3]['name']));
            self.i +=1
            self.projects.append({'complate' : text});
            return True
        if self.i % 4 == 3 :
            client.rtm_send_message(message_channel, '{} 的下周计划是？【格式：1：xx \n 2: xx \n 】'.format(self.projects[self.i/3]['name']));
            self.i +=1
            self.projects.append({'plan' : text});

#get your personal token from https://api.slack.com/web, bottom of the page.
api_key = sys.argv[0]; 
client = SlackClient(api_key)

weeklyNote = None

if client.rtm_connect():
    while True:
        last_read = client.rtm_read()
        if last_read:
            try:
                print last_read

                for msg in last_read:
                    if msg['type'] == 'message' and not 'bot_id' in msg:
                        text = msg['text']
                        message_channel = msg['channel']
                        if weeklyNote is not None:
                            r = weeklyNote.write(text, message_channel)
                            if not r :
                                weeklyNote = None
                        if text and 'weeklyNote' in text:
                            weeklyNote = WeeklyNote('demo');
                            weeklyNote.write(text, message_channel)
            except :
                logging.exception('exception: ')
                pass
        time.sleep(1)



import sys
import re
from operator import attrgetter
import codecs
import datetime

import chat
from chat import Chat, Author, Message, SubjectChange, IconChange, Join, Leave

def parse_event(line):
    
    split = re.split('^.*?([0-9/]{8}\s+[0-9:]{8}):\s+?([^:]+):\s(.*)$', line, flags=re.DOTALL)
    if len(split) == 5:
        return chat.Message, split[1:4]
    
    split = re.split('^.*?([0-9/]{8}\s+[0-9:]{8}):\s+?(.+)\schanged\sthe\ssubject\sto\s(.*)$', line, flags=re.DOTALL)
    if len(split) == 5:
        return chat.SubjectChange, split[1:4]
    
    split = re.split('^.*?([0-9/]{8}\s+[0-9:]{8}):\s+?(.+)\schanged\sthe\sgroup\sicon.*$', line, flags=re.DOTALL)
    if len(split) == 4:
        return chat.IconChange, split[1:3]
    
    split = re.split('^.*?([0-9/]{8}\s+[0-9:]{8}):\s+?(.+)\sjoined.*$', line, flags=re.DOTALL)
    if len(split) == 4:
        return chat.Join, split[1:3]
    
    split = re.split('^.*?([0-9/]{8}\s+[0-9:]{8}):\s+?(.+)\sjoined.*$', line, flags=re.DOTALL)
    if len(split) == 4:
        return chat.Leave, split[1:3]
    
    return None, line

def parse(filename):
    events = []
    authors = {}
    with codecs.open(filename, encoding='utf-8') as f:
        
        last_event_type = None
        
        for line in f.readlines():
            
            event_type, fields = parse_event(line)
            
            if event_type is not None:
                
                dt = datetime.datetime.strptime(fields[0], '%d/%m/%y %H:%M:%S')
                
                # Create the author if it doesn't exist.
                if fields[1] not in authors:
                    authors[fields[1]] = Author(fields[1])
                author = authors[fields[1]]
                
                try:
                    params = dt, author, fields[2]
                except IndexError:
                    params = dt, author
                
                # This is horrible.
                if last_event_type == Message:
                    events[-1].text = events[-1].text.strip()
                
                newevent = event_type(*params)
                events.append(newevent)
                
            elif last_event_type == Message:
                events[-1].text += line
                event_type = Message
            
            last_event_type = event_type
    
    # This is horrible, again.
    if last_event_type == Message:
        events[-1].text = events[-1].text.strip()
    
    events = sorted(events, key=attrgetter('datetime'))
    return chat.Chat(events, authors.values())

def parse_words(filename):
    
    words = []
    with codecs.open(filename, encoding='utf-8') as f:
        for line in f.readlines():
            words.append(line.split()[0])
    return words

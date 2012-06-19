
import sys
import re
import codecs
import datetime

class Author(object):
    
    def __init__(self, name, alias=None):
        self.name = name
        self.alias = alias
    
    def __str__(self):
        return unicode(self.name).encode("utf-8")
    
    def __unicode__(self):
        return self.name

class Message(object):
    
    def __init__(self, datetime, author, text):
        self.datetime = datetime
        self.author = author
        self.text = text
    
    def __str__(self):
        return unicode(self).encode("utf-8")
    
    def __unicode__(self):
        return (u"{0}: {1}: {2}").format(self.datetime, self.author, self.text)

class SubjectChange(object):
    
    def __init__(self, datetime, author, text):
        self.datetime = datetime
        self.author = author
        self.text = text
    
    def __str__(self):
        return unicode(self).encode("utf-8")
    
    def __unicode__(self):
        return (u"{0}: {1}: changed the subject to {2}").format(self.datetime, self.author, self.text)
    

class IconChange(object):
    
    def __init__(self, datetime, author):
        self.datetime = datetime
        self.author = author
    
    def __str__(self):
        return unicode(self).encode("utf-8")
    
    def __unicode__(self):
        return (u"{0}: {1} changed the group icon").format(self.datetime, self.author)

def parse_event(line):
    
    split = re.split('^.*?([0-9/]{8}\s+[0-9:]{8}):\s+?(.+):\s(.*)$', line, flags=re.DOTALL)
    if len(split) == 5:
        return Message, split[1:4]
    
    split = re.split('^.*?([0-9/]{8}\s+[0-9:]{8}):\s+?(.+)\schanged\sthe\ssubject\sto\s(.*)$', line, flags=re.DOTALL)
    if len(split) == 5:
        return SubjectChange, split[1:4]
    
    split = re.split('^.*?([0-9/]{8}\s+[0-9:]{8}):\s+?(.+)\schanged\sthe\sgroup\sicon.*$', line, flags=re.DOTALL)
    if len(split) == 4:
        return IconChange, split[1:3]
    
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
                
                # This is horrible.
                if last_event_type == Message:
                    events[-1].text = events[-1].text.strip()
                
                if event_type == Message:
                    newevent = Message(dt, author, fields[2])
                elif event_type == SubjectChange:
                    newevent = SubjectChange(dt, author, fields[2])
                elif event_type == IconChange:
                    newevent = IconChange(dt, author)
                
                events.append(newevent)
                
            elif last_event_type == Message:
                events[-1].text += line
                event_type = Message
            
            last_event_type = event_type
    
    # This is horrible.
    if last_event_type == Message:
        events[-1].text = events[-1].text.strip()
    
    return events, authors

if __name__ == '__main__':
    events, authors = parse(sys.argv[1])
    for a in authors:
        print a

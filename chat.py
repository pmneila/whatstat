
import re
import datetime
from operator import attrgetter, methodcaller

class Chat(object):
    
    def __init__(self, events, authors):
        self.events = events
        self.authors = authors
        self.messages = filter(lambda x: isinstance(x, Message), self.events)
    
    def set_aliases(self, aliasdict):
        for author in self.authors:
            if author.name in aliasdict:
                author.alias = aliasdict[author.name]
    
    def get_author(self, name):
        if isinstance(name, Author):
            return name
        
        author = filter(lambda x: x.name.lower() == name.lower() or \
                    (name.lower() in x.alias_lower), self.authors)
        if len(author) > 0:
            return author[0]
        return None
    
    def filter_author(self, author):
        """Returns the events from an author."""
        author = self.get_author(author)
        if author is None:
            raise ValueError, "author unknown"
        events = filter(lambda x: x.author is author, self.events)
        return Chat(events, [author])
    
    def filter_messages(self, expression):
        messages = filter(lambda x: re.search(expression, x.text) is not None, self.messages)
        return Chat(messages, self.authors)
    
    def filter_datetime_range(self, begin, end):
        
        events = filter(lambda x: begin <= x.datetime < end, self.events)
        return Chat(events, self.authors)
    
    def filter_day(self, day):
        
        dt1 = datetime.datetime.combine(day, datetime.time())
        dt2 = dt1 + datetime.timedelta(1)
        return self.filter_datetime_range(dt1, dt2)
    
    def iterdays(self):
        dates = map(methodcaller("date"), self.get_datetime_range())
        day = dates[0]
        while day <= dates[1]:
            yield day, self.filter_day(day)
            day += datetime.timedelta(1)
    
    def iterweeks(self):
        
        dates = self.get_datetime_range()
        one_week = datetime.timedelta(7)
        
        aux =[]
        day = dates[1] - one_week
        while day + one_week > dates[0]:
            aux.append(day)
            day -= one_week
        
        for day in aux[::-1]:
            yield day, self.filter_datetime_range(day, day+one_week)
    
    def get_datetime_range(self):
        return self.events[0].datetime, self.events[-1].datetime
    
    def get_text(self):
        lines = map(attrgetter('text'), self.messages)
        return ' '.join(lines)
    
    def get_words(self, lowercase=False):
        text = self.get_text()
        if lowercase:
            text = text.lower()
        words = re.findall('\w+', text, flags=re.UNICODE)
        return words
    
    def get_subject(self):
        
        aux = filter(lambda x: isinstance(x, SubjectChange), self.events)
        if len(aux) > 0:
            return aux[-1].text[1:-2]
        return None
    

class Author(object):
    
    def __init__(self, name, alias=None):
        self.name = name
        if alias is None:
            alias = []
        self.alias = alias
    
    def __str__(self):
        return unicode(self).encode("utf-8")
    
    def __unicode__(self):
        if len(self.alias)>0:
            return self.alias[0]
        return self.name
    
    def __repr__(self):
        return "Author(%r, %r)" % (self.name, self.alias)
    
    def set_alias(self, alias):
        self._alias = alias
        self.alias_lower = map(methodcaller("lower"), self.alias)
    
    alias = property(lambda self: self._alias, set_alias)

class Message(object):
    
    def __init__(self, datetime, author, text):
        self.datetime = datetime
        self.author = author
        self.text = text
    
    def __str__(self):
        return unicode(self).encode("utf-8")
    
    def __unicode__(self):
        return (u"{0}: {1}: {2}").format(self.datetime, self.author, self.text)
    
    def __repr__(self):
        return "Message(%r, %r, %r)" % (self.datetime, self.author, self.text)

class SubjectChange(object):
    
    def __init__(self, datetime, author, text):
        self.datetime = datetime
        self.author = author
        self.text = text
    
    def __str__(self):
        return unicode(self).encode("utf-8")
    
    def __unicode__(self):
        return (u"{0}: {1}: changed the subject to {2}").format(self.datetime, self.author, self.text)
    
    def __repr__(self):
        return "SubjectChange(%r, %r, %r)" % (self.datetime, self.author, self.text)
    

class IconChange(object):
    
    def __init__(self, datetime, author):
        self.datetime = datetime
        self.author = author
    
    def __str__(self):
        return unicode(self).encode("utf-8")
    
    def __unicode__(self):
        return (u"{0}: {1} changed the group icon").format(self.datetime, self.author)
    
    def __repr__(self):
        return "IconChange(%r, %r)" % (self.datetime, self.author)
    

class Join(object):
    
    def __init__(self, datetime, author):
        self.datetime = datetime
        self.author = author
    
    def __str__(self):
        return unicode(self).encode("utf-8")
    
    def __unicode__(self):
        return (u"{0}: {1} joined").format(self.datetime, self.author)
    
    def __repr__(self):
        return "Join(%r, %r)" % (self.datetime, self.author)
    

class Leave(object):
    
    def __init__(self, datetime, author):
        self.datetime = datetime
        self.author = author
    
    def __str__(self):
        return unicode(self).encode("utf-8")
    
    def __unicode__(self):
        return (u"{0}: {1} left").format(self.datetime, self.author)
    
    def __repr__(self):
        return "Leave(%r, %r)" % (self.datetime, self.author)
    

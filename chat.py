
import re
from operator import attrgetter

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
                    (x.alias is not None and x.alias.lower() == name.lower()), self.authors)
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
    
    def get_text(self):
        lines = map(attrgetter('text'), self.messages)
        return ' '.join(lines)
    
    def get_words(self, lowercase=False):
        text = self.get_text()
        if lowercase:
            text = text.lower()
        words = re.findall('\w+', text, flags=re.UNICODE)
        return words
        

class Author(object):
    
    def __init__(self, name, alias=None):
        self.name = name
        self.alias = alias
    
    def __str__(self):
        return unicode(self).encode("utf-8")
    
    def __unicode__(self):
        if self.alias is not None:
            return self.alias
        return self.name
    
    def __repr__(self):
        return "Author(%r, %r)" % (self.name, self.alias)

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
    


import sys
import re
from collections import defaultdict, Counter
from operator import itemgetter
import math

import networkx as nx

import parser

def load_chat(filename, authors_file=None):
    
    chat = parser.parse(filename)
    if authors_file is not None:
        execfile(authors_file, globals(), locals())
        chat.set_aliases(authors)
    
    return chat

def count_words(chat):
    
    words = chat.get_words(True)
    count = Counter(words)
    return count

def most_common_uncommon_words(chat, common_words, n=100):
    
    count = count_words(chat)
    count = count.most_common()
    return filter(lambda x: x[0] not in common_words, count)[:n]

def messages_per_author(chat):
    
    res = dict((unicode(author),0) for author in chat.authors)
    
    for author in chat.authors:
        authorchat = chat.filter_author(author)
        res[unicode(author)] = len(authorchat.messages)
    
    res = sorted(res.iteritems(), key=itemgetter(1))
    return res

def characters_per_author(chat):
    
    res = dict((unicode(author),0) for author in chat.authors)
    
    for author in chat.authors:
        authorchat = chat.filter_author(author)
        res[unicode(author)] = len(authorchat.get_text())
    
    res = sorted(res.iteritems(), key=itemgetter(1))
    return res

def positives(chat):
    
    possent = dict((unicode(author),0) for author in chat.authors)
    posrecv = dict((unicode(author),0) for author in chat.authors)
    posdict = defaultdict(lambda : defaultdict(int))
    
    # Get the messages with positive marks.
    poschat = chat.filter_messages('(^|\s)[\w]+\++($|\s|\,)')
    for message in poschat.messages:
        giver = message.author
        # Get the votes in the current message.
        matches = re.findall('(^|\s)([\w]+)(\++)($|\s|\,)', message.text)
        for match in matches:
            # Get the receiver and sum the number of positives.
            receiver = chat.get_author(match[1])
            if receiver is None or giver is receiver:
                continue
            num = len(match[2])
            posdict[unicode(giver)][unicode(receiver)] += num
            possent[unicode(giver)] += num
            posrecv[unicode(receiver)] += num
    
    # Get the value of the maximum edge.
    maximum = max(map(lambda x: max(x.values()), posdict.values()))
    
    # Build the graph.
    g = nx.DiGraph()
    for name, number in posrecv.iteritems():
        if number == 0 and possent[name] == 0:
            continue
        g.add_node(name, positives=number,
                    label='%s (%s)' % (name, number),
                    color='lightblue2', style='filled',
                    fontsize=12)
    for giver, distr in posdict.iteritems():
        for receiver, number in distr.iteritems():
            relative = number/float(maximum)
            hue = 0.2 - 0.2 * relative
            g.add_edge(giver, receiver,
                    len = 2.0,
                    weight=number,
                    label=number,
                    penwidth=5*relative + 1.0,
                    color="%s 1.0 1.0"%hue,
                    fontsize=10)
    
    return g

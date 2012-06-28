
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
        aux = {}
        execfile(authors_file, globals(), aux)
        chat.set_aliases(aux["authors"])
    
    return chat

def trending_topics(chat, number=10):
    
    words = list(set(chat.get_words(True)))
    by_words = {w:[] for w in words}
    words_per_week = []
    
    for week, weekchat in chat.iterweeks():
        
        week_words = weekchat.get_words(True)
        week_words_count = Counter(week_words)
        words_per_week.append(len(week_words))
        
        for w, v in by_words.iteritems():
            v.append(0)
        
        for word, count in week_words_count.iteritems():
            by_words[word][-1] = count
    
    res = {}
    
    active_words = sum(words_per_week)
    for word in by_words:
        word_history = by_words[word]
        
        word_normal_freq = sum(word_history)/float(active_words)
        word_last_freq = word_history[-1]/float(words_per_week[-1])
        res[word] = (word_last_freq - word_normal_freq)/word_normal_freq * math.log(word_history[-1] + 1)
    
    res = sorted(res.iteritems(), key=itemgetter(1))[-number:]
    tt = map(itemgetter(0), res)
    #return res, by_words, words_per_week
    return tt

def tf_idf(chat):
    
    unique_words = list(set(chat.get_words(True)))
    df = dict([(w,0) for w in unique_words])
    tf = {}
    
    words = list(set(chat.get_words(True)))
    by_word = {w:[] for w in words}
    
    D = 0
    for day, daychat in chat.iterweeks():
        
        daywords = daychat.get_words(True)
        daywordscount = Counter(daywords)
        
        if len(daywords) > 0:
            D += 1
        
        for w in by_word:
            by_word[w].append(0)
        
        for word, count in daywordscount.iteritems():
            tf[(day,word)] = count #/float(len(daywords))
            df[word] += 1
    
    tf_idf = {}
    by_day = {}
    by_word = {}
    
    for (day,word), count in tf.iteritems():
        aux = count * math.log(float(D)/df[word])
        tf_idf[(day,word)] = aux
        if day not in by_day:
            by_day[day] = {}
        if word not in by_word:
            by_word[word] = {}
        by_day[day][word] = aux
        by_word[word][day] = aux
    
    return by_day, by_word, df

def messages_per_day_per_author(chat):
    
    by_day = {}
    
    for day, daychat in chat.iterdays():
        by_day[day] = {}
        for author in daychat.authors:
            by_day[day][author] = len(daychat.filter_author(author).messages)
    
    return by_day

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

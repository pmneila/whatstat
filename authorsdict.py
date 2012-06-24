
"""
Generate the authors dictionary from a chat history.
"""

import sys
import whatstat

def write_dict(infile, outfile):
    chat = whatstat.load_chat(sys.argv[1])
    res = {}
    for author in chat.authors:
        res[author.name] = []
    
    with open(outfile, "w") as f:
        f.write("authors = %r" % res)

if __name__ == '__main__':
    write_dict(sys.argv[1], sys.argv[2])

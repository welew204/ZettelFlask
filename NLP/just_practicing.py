
import nltk
from collections import defaultdict


title1 = "The Title of this post is..."
title2 = "TDay BS"

tokens = ['personal', 'trainer', 'coach', 'coach', 'often', 'asked', 'best', 'workout', 'coach', 'blank', 'abs', 'legs', 'person', 'personhood', 'lose', 'weight']
tokens2 = ['wherever', 'find', 'year', 'thanksgiving', 'train', 'able', 'move', 'workout', 'special', 'fitness', 'coach', 'workout', 'anywhere', 'made']

starter = [(title1, tokens), (title2, tokens2)]
ddicts = []

porter = nltk.PorterStemmer()

for l in starter:
    d = defaultdict(list)
    title, tokens = l
    for t in tokens:
        s = porter.stem(t)
        d[s].append(t)
    res = (title, d)
    ddicts.append(res)
    
baggy = defaultdict(list)
posts = defaultdict(list)

final = {}

for tup in ddicts:
    ## so each dty has a dict of stems, with each token
    title, dict = tup
    for s in dict.keys():
        ## the tkns extracted from THIS post, that are repr by this stem (s)
        tkns = dict[s]
        ## this updates (extends) the list of tokens for each stem (for all posts)
        baggy[s].extend(tkns)
        ## this records the tokens found IN this post (stem will be clear bc it's the parent of this)
        posts[s].append((title, tkns))

for s in baggy.keys():
    final[s] = {"count": len(baggy[s]), "tokens": baggy[s], "posts": posts[s]}

sort_final = sorted(final.items(), key=lambda x: x[1]["count"],reverse=True)

print(final, "\n \n")
print("sorted....................", sort_final)



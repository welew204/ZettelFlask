
import nltk
import json

import difflib as dl
import matplotlib

from parse import just_text
# this fnc takes string in html or md and turns it into raw text

from bs4 import BeautifulSoup
import bs4 as BS

import string
from collections import defaultdict

src_url = "/Users/williamhbelew/Hacking/ZetApp/ZettelApp/ZettelFlask/parsedXML/parsedBlogs.json"
corpus = {}

## this will be a list, to be handed into a TextCollection obj for similarity processing
corpus_tc = []

## for keeping track of stem::token incidence:
post_dicts = []

## this will be a BoW of STEMs (all found, duplicates included)
total_bow = []
stopwords = nltk.corpus.stopwords.words('english')

with open(src_url, "r") as blogs_json:
    blogs = json.load(blogs_json)
    
    for b in blogs:
        txt = b["formatted_content"]
        title = b["title"]
    
    # haha NLTK does this FOR me :/ via a function: nltk.clean_html() which takes an HTML string and returns raw text, 
    # BUT it does this useing BeutifulSoup, which just_text() uses anyway...
        txt = just_text(txt)

        ## I still want to preserve the meaning (and therefore) PUNCTUATION at this stage
        obj = {"text": txt}

        corpus[title] = obj

    ## b is the TITLE of each post (str)
    for b in list(corpus.keys()):
        data = corpus[b]["text"]
        
        tokens = nltk.word_tokenize(data)

        ## this takes care of digits and punctuation
        tokens = [w.lower() for w in tokens if w.isalpha()]

        ## 'text' is tokenized (and lower case, free of punct) but preserves context
        text = nltk.Text(tokens)
        corpus_tc.append(text)

        # taking out stopwords
        cl_text = []
        for w in text.tokens:
            if w in stopwords:
                continue
            else:
                cl_text.append(w)


        porter = nltk.PorterStemmer()

        d = defaultdict(list)

        for t in cl_text:
            s = porter.stem(t)
            d[s].append(t)
        res = (b, d)
        post_dicts.append(res)

baggy = defaultdict(list)
posts = defaultdict(list)

final = {}

for tup in post_dicts:
## so each dty has a dict of stems, with each token
    title, p_stems = tup
    for s in p_stems.keys():
        ## the tkns extracted from THIS post, that are repr by this stem (s)
        tkns = p_stems[s]
        ## this updates (extends) the list of tokens for each stem (for all posts)
        baggy[s].extend(tkns)
        ## this records the tokens found IN this post (stem will be clear bc it's the parent of this)
        posts[s].append((title, tkns))


for s in baggy.keys():
    freq = len(baggy[s])
    tokes = list(set(baggy[s]))
    final[s] = {"count": freq, "tokens": tokes, "posts": posts[s]}

## need to figure out how to sort my FINAL dict by value of "count"
sort_final = sorted(final.items(), key=lambda x: x[1]["count"],reverse=True)
final = dict(sort_final)

## this makes a collection, which can then be used for similarity processing
blogs_text_collection = nltk.text.TextCollection(corpus_tc)


## FOR EYEBALLING PURPS
    ## FROM RKB::::
    ## MAKE sorted version, sort by most_common ?
    ## find threshold for 'overly common' words (eyeball)
    ## find lower threshold (eyeball, around 2-3 incidence)
    ## everything in between are potential
with open("eyeball_stems.txt", "w") as txt:
    for stem in final.keys():
        count = final[stem]["count"]
        tokens = final[stem]["tokens"]
        to_write = f"{stem}: {count} // {tokens} \n"
        txt.write(to_write)

## 





#-------------------------BIGRAMS?--------------
    #bigrams = nltk.bigrams(total_bow)
    #bigrams_fd = nltk.FreqDist(bigrams)
    #print(bigrams_fd.most_common(20))


## dumping it back into a disk json >>> THIS NEEDS TO BECOME A PICKLE (or 2)
        ## flag file as "rb" (binary)

with open("blog_dump.json", "w") as write_file:
    json.dump(final, write_file, indent=2)
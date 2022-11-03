
import nltk
import json

import difflib as dl
import matplotlib

from parsedXML.parse import just_text
# this fnc takes string in html or md and turns it into raw text

from bs4 import BeautifulSoup
import bs4 as BS

import string

src_url = "/Users/williamhbelew/Hacking/ZetApp/ZettelApp/ZettelFlask/parsedXML/parsedBlogs.json"
corpus = {}
total_bow = []
stopwords = nltk.corpus.stopwords.words('english')
punct = [",", ".", "(", ")", "?", ":", "*", "'", "--", "!", "'s", "n't", "''", "``", "+", "="]
# ^ allllll the words

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

    # do something with corpus (dict with each blog in raw text strings inside dict value (obj), access w/ key "text")
    for b in list(corpus.keys()):
        ## TAKE OUT PUNCTUATION HERE!!!!!!!!! just replace w/ white space
        data = corpus[b]["text"]
        data = data.translate(str.maketrans('', '', string.punctuation))

        tokens = nltk.word_tokenize(data)
        tokens = [w.lower() for w in tokens]

        ## DO I EVEN NEED 'Text'?? ...
        text = nltk.Text(tokens)

        ## THIS SHOULDN"T BE NEEDED NOW trying to clean out allided words (on period); WHAT ABOUT WHITESPACE-ALLIDES?
        cl_fdist = nltk.FreqDist(text)
        to_remove = []
        for i in cl_fdist.hapaxes():
            if "." in i:
            ## this yields a list (2 items)
                to_add = i.split(".")
                to_add = [w for w in to_add if w != ""]
                tokens.extend(to_add)
                to_remove.append(i)
        
        for i in to_remove:
            tokens.remove(i)


        # taking out stopwords,{{{ punctuation}}} AND checking for if any characters are numbers/digits
        cl_text = []
        for w in tokens:
            if w in stopwords or w in punct:
                pass
            elif any(i.isdigit() for i in w):
                pass
            else:
                cl_text.append(w)

        porter = nltk.PorterStemmer()
        text_stems = [porter.stem(t) for t in cl_text]
        # ^ this seems ALMOST right, but the raw text has some missing white-space, which is effing *some* shit up

        ## MAKE THIS INTO A SET ... does that automagically keep track of dupes???
        total_bow = total_bow + text_stems

        ## COMPARE THIS TO FreqDist from .probablity.FreqDist
        fdist = nltk.FreqDist(text_stems)


        corpus[b]["stems"] = text_stems

        ##RKB SAYS THIS IS NOT NEEDED
        corpus[b]["fdist"] = fdist
        
    # FreqDist of the total BoW AND bigrams; trying to clean them up...
    #### IF I MAKE this into a set, won't I lose the number of incidences of the thing?
    bow_dist = nltk.FreqDist(total_bow)



    ## MAKE sorted version, sort by most_common ?
    ## find threshold for 'overly common' words (eyeball)
    ## find lower threshold (eyeball, around 2-3 incidence)
    ## everything in between are potential


    bigrams = nltk.bigrams(total_bow)
    bigrams_fd = nltk.FreqDist(bigrams)

    #print(bigrams_fd.most_common(20))
    b_o_w = {"words": total_bow, "w_fd": bow_dist}

    nlp_output = {"corpus": corpus, "BoW": b_o_w}

    #bigrams_fd.pprint()

    # dumping it back into a disk json

with open("blog_dump.json", "w") as write_file:
    json.dump(nlp_output, write_file, indent=2)
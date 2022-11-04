
import nltk
import json

import difflib as dl
import matplotlib

from NLP.parse import just_text
# this fnc takes string in html or md and turns it into raw text

from bs4 import BeautifulSoup
import bs4 as BS

src_url = "/Users/williamhbelew/Hacking/ZetApp/ZettelApp/ig_TFA_dump.json"
corpus = {}
total_bow = []
stopwords = nltk.corpus.stopwords.words('english')
punct = [",", ".", "(", ")", "?", ":", "*", "'", "--", "!", "'s", "n't", "''", "``", "+", "="]
# ^ allllll the words

with open(src_url, "r") as blogs_json:
    blogs = json.load(blogs_json)
    
    for b in blogs:
        txt = b["content"]
        for_title = b["date"]
        title = f"Post: {for_title}"
    
    # haha NLTK does this FOR me :/ via a function: nltk.clean_html() which takes an HTML string and returns raw text, 
    # BUT it does this useing BeutifulSoup, which just_text() uses anyway...
        txt = just_text(txt)

        obj = {"text": txt}

        corpus[title] = obj

    # do something with corpus (dict with each blog in raw text strings inside dict value (obj), access w/ key "text")
    for b in list(corpus.keys()):
        tokens = nltk.word_tokenize(corpus[b]["text"])
        tokens = [w.lower() for w in tokens]
        text = nltk.Text(tokens)

        ## trying to clean out allided words (on period); WHAT ABOUT WHITESPACE-ALLIDES?
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


        # taking out stopwords, punctuation AND checking for if any characters are numbers/digits
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

        total_bow = total_bow + text_stems

        fdist = nltk.FreqDist(text_stems)


        corpus[b]["stems"] = text_stems
        corpus[b]["fdist"] = fdist
        
    # FreqDist of the total BoW AND bigrams; trying to clean them up...

    bow_dist = nltk.FreqDist(total_bow)


    bigrams = nltk.bigrams(total_bow)
    bigrams_fd = nltk.FreqDist(bigrams)

    #print(bigrams_fd.most_common(20))
    b_o_w = {"words": total_bow, "w_fd": bow_dist}

    nlp_output = {"corpus": corpus, "BoW": b_o_w}

    #bigrams_fd.pprint()

    # dumping it back into a disk json

with open("blog_dump.json", "w") as write_file:
    json.dump(nlp_output, write_file, indent=2)
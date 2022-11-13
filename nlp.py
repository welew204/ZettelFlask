from datetime import datetime
import json
import numpy
import math
import nltk
import ZettelFlask.parse as parse# for just_text() function
import wordsegment

from collections import defaultdict

data_url ="/Users/williamhbelew/Hacking/ZetApp/ZettelApp/ZettelFlask/parsedXML/parsedBlogs.json" #update with url of json file
out_url = "" #optional, req'd if output_to_csv = True

ig_data = False #update if data coming from IG

title_weight = 3
hashtag_weight = 2
lowerKWthresh = 1

output_to_csv = False
nsimPairs = 50 # how many similarities you wanna see

## open // parse files (specify format)
## format: {"title": , --> string
#        "content": ,  --> string
#		**"author": ,  --> string
#		*"hashtags": , --> list of strings
#		"published": , --> string
#		*"media": } --> list of strings           
#       
#       ** only included if ig_data is FALSE
#       * only included if ig_data is True

### WRITE SEPERATE BLOCK TO HANDLE INCOMING parsedBlogs ("pubDate" to "published", "formatted_content" to "body_md")

def open_parse(data, ig_data=False):
    posts = data
    psd = {}
    if ig_data:
        for i,p in enumerate(posts):
            igidx = f"I{i:04d}"
            published = p["timestamp"]
            text = p["content"]
            text = parse.just_text(text)
            
            htags = p["hashtags"]
            media = p["uri"]
            psd[igidx] = {
                "id": igidx,
                "text": text,
                "date": published,
                "hashtags": htags,
                "media": media
            }
    else:
        for i,p in enumerate(posts):
            bidx = f"B{i:04d}"
            title = p["title"]
            published = p["published"]
            ## these aren't needed now that data is piped in from g.posts
            #published = datetime.strptime(published, "%a, %d %b %Y %H:%M:%S %z")
            #published = published.strftime("%Y-%m-%d")
            text = p["body_md"]
            text = parse.just_text(text)
            
            author = p["author"]
            psd[bidx] = {
                "id": bidx,
                "title": title,
                "text": text,
                "date": published,
                "author": author
            }
    return psd

## tokenize // fdist
def tok_fdist(data_dict, ig_data=False):
    all_stems = []
    stem_ddict = defaultdict(list)
    all_tokens = defaultdict(int)
    stopwords = nltk.corpus.stopwords.words('english')
    stemmer = nltk.SnowballStemmer("english")
    if ig_data:
        wordsegment.load()
    for p in data_dict.keys():
        post = data_dict[p]
        txt = post["text"]
        tokens = nltk.word_tokenize(txt)
        if ig_data:
             htags = post["hashtags"]
             ht_list = []
             for h in htags:
                if h in tokens:
                    tokens.remove(h)
                segm_h = wordsegment.segment(h)
                ht_list.extend(segm_h)
             h_tokens = nltk.word_tokenize(" ".join(ht_list))
             tokens += h_tokens * hashtag_weight
        else:
            title = post["title"]
            t_tokens = nltk.word_tokenize(title)
            tokens += t_tokens * title_weight
        tokens = [w.lower() for w in tokens if w.isalpha()]
        tokens = [w for w in tokens if w not in stopwords]
        for t in tokens:
            all_tokens[t] += 1
        stems = []
        for t in tokens:
            s = stemmer.stem(t)
            stem_ddict[s].append(t)
            stems.append(s)
        fdist = nltk.FreqDist(stems)
        post["fdist"] = fdist
        all_stems.extend(stems)
    all_stems = nltk.FreqDist(all_stems)
    for s in stem_ddict:
        tkns = set(stem_ddict[s])
        s_tkns = sorted(tkns, key=lambda x: all_tokens[x], reverse=True)
        stem_ddict[s] = s_tkns
    ###BASIC VOCAB (cutoff low incidence), finish as {} mapped to idx, reutnr w/ other vals
    basicVocab = [t for t in all_stems.keys() if all_stems[t] > lowerKWthresh]
    basicVocabIdx = {kwid:kw for kw, kwid in enumerate(basicVocab)}
    return data_dict, stem_ddict, all_stems, basicVocabIdx
    
## calc IDF (total docs / total no docs w/ kw in it)
def calc_idf(data, stem_ddict):
    docIDF = {}
    ndoc = len(data)
    for s in stem_ddict:
        kwdoc = 0
        for p in data.keys():
            post = data[p]
            if s in post["fdist"]:
                kwdoc += 1
        idf = math.log(ndoc/kwdoc)
        docIDF[s] = idf
    return docIDF

## calc weights (TF-IDF)
def calc_weights(data, basicVocabIdx, docIDF):
    basicVSet = set(list(basicVocabIdx.keys()))
    nkw = len(basicVSet)
    for pid, pkey in enumerate(sorted(list(data.keys()))):
        post = data[pkey]
        kwvec = [0 for i in range(nkw)]
        maxw = 0.
        bestKW = ""
        for kw in post['fdist']:
            if kw in basicVSet:
                w = post['fdist'][kw] * docIDF[kw]
                kwvec[ basicVocabIdx[kw] ] = w
                if w > maxw:
                    maxw = w
                    bestKW = kw
        
        total = sum(kwvec)

        if maxw == 0:
            print(f"Head's up: no basicVocab in post # {pkey}")
        else:
            norm = [w/total for w in kwvec]
        
        post['bestKW'] = bestKW
        post['kwvec'] = numpy.array(norm)
        data[pkey] = post

        ## don't USE pid?? just for printing progress?
    return data

## calc similarity -- gonna go thru each and every post and compare to every OTHER post, by calculating dot product of each's WEIGHTs
def comp_similarity(data):
    postSims = {}
    maxSim = 0.
    for id1,p1 in enumerate(data.keys()):
        post1 = data[p1]
        p1_kw = post1['kwvec']
        p1_fd = post1['fdist']
        for id2,p2 in enumerate(data.keys()):
            if id2 <= id1:
                continue
            post2 = data[p2]
            p2_kw = post2['kwvec']
            p2_fd = post2['fdist']
            sim = numpy.dot(p1_kw,p2_kw)
            if sim > maxSim:
                print(f"DING! we have a winner... SIMILARITY = {sim}\n >>> Post: {p1}, {p1_fd.most_common(8)} \n >>> Post: {p2}, {p2_fd.most_common(8)}")
                maxSim = sim
            postSims[ (p1, p2) ] = sim
    return postSims

## function for running this script as module (just send in json w/ form shown above)...
def run_nlp(data_from_g):
    data = open_parse(data_from_g)
    up_data1, stem_ddict, all_stems, basicVocabIdx = tok_fdist(data, ig_data=ig_data)
    docIDF = calc_idf(up_data1, stem_ddict)
    up_data_f = calc_weights(up_data1,basicVocabIdx,docIDF)
    return up_data_f, stem_ddict, basicVocabIdx, docIDF, all_stems

## out as csv OR dict (depending on use-case)

if __name__ == "__main__":
# this will run this file from URL provided at top of script
    data = open(data_url, "r")
    data_in = json.load(data)
    data_dict = open_parse(data_in, ig_data=ig_data)
    data.close()

    up_data1, stem_ddict, all_stems, basicVocabIdx = tok_fdist(data_dict, ig_data=ig_data)
    docIDF = calc_idf(up_data1, stem_ddict)
    up_data_f = calc_weights(up_data1,basicVocabIdx,docIDF)

    postSims = comp_similarity(up_data_f)
    sorted_postSim = sorted(postSims.keys(), key=lambda k: postSims[k], reverse=True)
    
    to_print=list(up_data_f.keys())
    for i in to_print[9:10]:
        post = up_data_f[i]
        print(post['kwvec'])

    if output_to_csv:
        with open(out_url, "w") as outs:
            outs.write("Post1,Post2,Sim\n")
            for s in sorted_postSim[:nsimPairs]:
                p1, p2 = s
                sim = postSims[s]
                outs.write(f"{p1},{p2},{sim}\n")
    

    
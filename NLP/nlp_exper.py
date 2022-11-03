import json
import sqlite3
import nltk

src_url = "/Users/williamhbelew/Hacking/ZetApp/ZettelApp/blog_dump.json"
db_path = "/Users/williamhbelew/Hacking/ZetApp/ZettelApp/instance/zettapp.sqlite"


## Singular Value Decmposition ideas

def svp_engine():
    pass

## similarity between texts

def similarity_engine():
    pass

def tag_in_post(blogs, tags_fd):
    tpcnxs = []
    for i in list(blogs["corpus"].keys()):
        for s in blogs["corpus"][i]["stems"]:
            if s in tags_fd:
                tpcnxs.append((s, i))
                ## this tuple is the tag that is found (s) AND the title of the post where it is found (i)
    return tpcnxs

with open(src_url, "r") as blogs_dump:
    blogs = json.load(blogs_dump)

    currentDB = sqlite3.connect(db_path)
    cursorDB = currentDB.cursor()

    cursorDB.execute('DELETE FROM tags;')
    currentDB.commit()
    
    tags_fd = nltk.FreqDist(blogs["BoW"]["words"])

    ## top 100 incidence tags (after cleaning) >>>> this will be KEYWORDS
    tags_fd = tags_fd.most_common(100)
    
    for i in tags_fd:
        ## 'i' comes in as a tuple (tag, count) so just pass that
        cursorDB.execute("INSERT INTO tags (tag, count) VALUES (?, ?)", i)
        currentDB.commit()

    tpcnxs = tag_in_post(blogs, tags_fd)

    for c in tpcnxs:
        ## 'c' comes in as a tuple (tag, post_title) so just pass that but need to JOIN
        cursorDB.execute("INSERT INTO tpcnx (tag_id, post_id) VALUES (?, ?) INNER JOIN post, tags ON ", i)
        currentDB.commit()


    print("Done")

    
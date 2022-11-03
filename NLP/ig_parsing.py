import json
import datetime as dt

finished_data = []
## ^^ this is a LIST of OBJECTs, with each having:
## - "content" which has NOT been cleaned in any way
## - "date"
## - "uri" which is a LIST of 1+ relative URIs, will need to join with the actual filespace uri when needed


tfa_com_str = "TFA Community Agreement #"


with open("/Users/williamhbelew/Hacking/ZetApp/ZettelApp/nltk_learning/IG_tfa_posts.json", "r") as ig_data:
    ig = json.load(ig_data)    
    for p in ig:
        media = []
        hashtags = []
        post = {}
        if len(p["media"]) > 1:
            for m in p["media"]:
                media.append(m["uri"])
            content = p["title"]
            post["content"] = content
            while len(content) > 0:
                (first, hsh, after) = content.partition("#")
                if hsh == "":
                    break
                pointer = 0
                while len(after) > 0:
                    i = after[pointer]
                    if i.isalnum() == False or i == r"\\" or i == "â":
                        brk_ind = after.index(i)
                        break
                    if pointer == len(after) - 1:
                        brk_ind = None
                        break
                    pointer += 1

                htag = after[:brk_ind]
                hashtags.append(htag)
                if brk_ind is not None:
                    brk_ind += 1            
                    content = after[brk_ind:]
                else:
                    break

            post["hashtags"] = hashtags
            post["uri"] = media
            c_ts = p["creation_timestamp"]
            post["timestamp"] = dt.datetime.fromtimestamp(c_ts).strftime('%Y-%m-%d')
        else:
            if tfa_com_str in p["media"][0]["title"]:
                continue
            content = p["media"][0]["title"]
            post["content"] = content
            while len(content) > 0:
                (first, hsh, after) = content.partition("#")
                if hsh == "":
                    break
                pointer = 0
                while len(after) > 0:
                    i = after[pointer]
                    if i.isalnum() == False or i == r"\\" or i == "â":
                        brk_ind = after.index(i)
                        break
                    if pointer == len(after) - 1:
                        brk_ind = None
                        break
                    pointer += 1

                htag = after[:brk_ind]
                hashtags.append(htag)
                if brk_ind is not None:
                    brk_ind += 1            
                    content = after[brk_ind:]
                else:
                    break

            post["hashtags"] = hashtags
            post["uri"] = [p["media"][0]["uri"]]
            c_ts = p["media"][0]["creation_timestamp"]
            post["timestamp"] = dt.datetime.fromtimestamp(c_ts).strftime('%Y-%m-%d')
        finished_data.append(post)

with open("ig_TFA_dump.json", "w") as write_file:
    json.dump(finished_data, write_file, indent=2)

        #print("\n<------------------------------------->\n")
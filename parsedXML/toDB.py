import parse
import json
import os

def main(path):

    blogs = parse.main()

    blogs_json = json.dump(blogs, open(path,"w"), indent=4)
    print("json dumped!")

    return blogs_json

if __name__ == "__main__":
    path = "/Users/williamhbelew/Hacking/ZetApp/parsedBlogs.json"
    
    main(path)
    if os.path.exists(path):
        print("yay")
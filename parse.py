""" requires input file in XML (no get URL fnc)

on import, this returns a list of blog posts, each blog is a dict:

{
    "title": ...
    "author": ...
    "formatted_content": ...
    "raw_content": ...
    "pubDate": ...
}

"""


import csv
from typing import final
import xml.etree.ElementTree as ET
import os
import sys

import re

from bs4 import BeautifulSoup
import bs4 as BS


inp_xml = '/Users/williamhbelew/Hacking/ZetApp/ZettelApp/ZettelFlask/parsedXML/Squarespace-Wordpress-Export-09-21-2022.xml'


def parse_xml(file):

    tree = ET.parse(file)

    root = tree.getroot()

    return(root)

def convertXML(file):

    excerpt="http://wordpress.org/export/1.2/excerpt/"
    content="http://purl.org/rss/1.0/modules/content/"
    wfw="http://wellformedweb.org/CommentAPI/"
    dc="http://purl.org/dc/elements/1.1/"
    wp="http://wordpress.org/export/1.2/"

    blogs_root = parse_xml(file)

    blog_list = []

    for item in blogs_root.findall('./channel/item'):

        blog = {}

        for child in item:
            
            if child.tag == "{http://wordpress.org/export/1.2/}post_type":
                if child.text == "post":
                    cont = item.find("{http://purl.org/rss/1.0/modules/content/}encoded")
                    tit = item.find("title")
                    if tit.text == None:
                        break
                    date = item.find("pubDate")
                    creator = item.find("{http://purl.org/dc/elements/1.1/}creator")
                    if "will" in creator.text:
                        author = "WB"
                    elif "hannah" in creator.text:
                        author = "HH"
                    blog["title"] = tit.text
                    blog["author"] = author
                    blog["formatted_content"] = cont.text
                    blog["raw_content"] = just_text(cont.text)
                    blog["pubDate"] = date.text
                    blog_list.append(blog)
                else:
                    break
        
    
    return blog_list

def just_text(file):
    # takes out new lines
    no_nlines = re.sub('\n', ' ', file)
    no_bullets = re.sub('\u00a0', ' - ', no_nlines)
    no_nbsp = re.sub("&nbsp;", " ", no_bullets)
    """ soup = unicodedata.normalize("NFKD", soup) """
    # makes a BeautifulSoup object >>> we lose SOME whitespace, especially around punctuation (fixed by passing " " arg to get_text (telling it how to combine individual strings of html))
    soup = BS.BeautifulSoup(no_nbsp, 'html.parser')
    # beautiful soup method that spits out just text >>>>> 
    gtext = soup.get_text(" ")
    # takes out bullet points (\xa0) and nbsp (\u00a0) >>> NOT NEEDED??
    #encoding_text = gtext.encode('ascii', 'ignore')
    # get it back to being string (not a byte-string) >>>> NOT NEEDED?? 
    #final = encoding_text.decode()
    return gtext

"""with open(os.path.join(sys.path[0], inp_xml), 'r') as f:
    data = f.read() """

def main():
    blogs = convertXML(inp_xml)

    return blogs

if __name__ == "__main__":
    print(main())
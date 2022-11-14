# ZettelFlask

This is the back-end framework for running the Zettel app. 

It is set-up w/ an app-factory in runZettel.py that pulls in the blueprint outlined in blog.py.

## Dependencies

- **flask_cors**: to work around CORS issues
- **bs4**: BeautifulSoup to convert html into text
- **nltk**: this library is used extensively for the Natural Language Processing (NLP) components

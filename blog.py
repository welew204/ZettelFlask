from cgitb import reset
import imp
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
)
import sys

from bs4 import BeautifulSoup
import bs4 as BS
from sqlalchemy import null

from werkzeug.exceptions import abort

from ZettelFlask.db import get_db

bp = Blueprint('notes', __name__)

@bp.route('/')
def index():
    print(f"Got this far (to {index})", file=sys.stderr)
    db=get_db()
    posts = db.execute(
        'SELECT * FROM post JOIN author ON post.author_id = author.id'
    ).fetchall()

    #print(f"length of DB is currently {len(posts)}", flush=True)

    # need to fix how the RENDER is happening!    
    # render_template('blog/index.html', posts=posts)

    # need to put this into a json file? make it available on the filespacE?!
    return 'Done', 201

@bp.route('/api_json')
def api_json():
    db=get_db()

    posts = []
    #print(f"{db}", file=sys.stderr)

    curs = db.cursor()

    res = curs.execute('SELECT post.id,title,body_formatted,published,name FROM post INNER JOIN author ON author.id=post.author_id')

    all_res = res.fetchall()
    # because of how get_db() makes the Rows into special objects, this fetchall() returns a set of Row objects (which are indexed, attribute callable, etc)
    
    for note in all_res:
        id = note["id"]
        title = note["title"]
        author = note["name"]
        body_md = note["body_formatted"]
        published = note["published"]
        res = {"id": id, "title": title, "body_md": body_md, "author":author, "published": published}

        posts.append(res)

    return jsonify({"posts": posts}), 200

""" commenting out the below (from the Flaskr tutorial)

@bp.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None
        
        if not title:
            error  = 'Title is required'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id)'
                ' VALUES (?, ?, ?)',
                (title, body, g.author['id'])
            )
            db.commit()
            return redirect(url_for('blog.index'))

    #return render_template(?*?*?*?*?)
    return 'Post created!', 201

... bc I'm trying to refactor create() with JSON inputs (see below)"""

@bp.route('/create', methods=('POST',))
def create():
    req_data = request.get_json()
    
    for post in req_data:
        title = post['title']
        body = post['body']
        author = post['author']
        published = post['published']



    error = None
    
    if not title:
        title = "<no title>"

    if error is not None:
        flash(error)
    else:
        db = get_db()
        g.author = db.execute(
            'SELECT name FROM author'
        )
        print(g.author, flush=True)
        db.execute(
            'INSERT INTO post (title, body_formatted, body_raw, published, author_id)'
            ' VALUES (?, ?, ?, ?, ?)',
            (title, body, published, g.author['id'])
        )
                # I think the issue is HERE ^^^

        db.commit()
        return redirect(url_for('hello'))

    #return render_template(?*?*?*?*?)
    return 'Post created!', 201

"""get_post() fnc that can be called to update and delete entries in db"""

def get_post(id):
    """just gives the post (a single ROW) as the result of looking up the id (if it exists)"""
    post = get_db().execute(
        'SELECT p.id, title, body_formatted, published, author_id'
        ' FROM post p JOIN author u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    return post

# this is currently not needed, since nothing is stored in html right now
def just_text(html_file):
    # takes out new lines
    soup = html_file.replace('\n', ' ')

    """ soup = unicodedata.normalize("NFKD", soup) """
    # makes a BeautifulSoup object
    soup = BS.BeautifulSoup(soup, 'html.parser')
    # beautiful soup method that spits out just text
    soup = soup.get_text()
    # takes out bullet points (\xa0) and nbsp (\u00a0)
    soup = soup.encode('ascii', 'ignore')
    # get it back to being string (not a byte-string) 
    soup = soup.decode()
    return soup


@bp.route('/update', methods=('POST',))
def update():
    db = get_db()


    req_data = request.get_json()
    print(f"Request recieved...", file=sys.stderr)
    for p in req_data:
        id = p["id"]
        title = p['title']
        # body should come in as HTML (grab converted version from Showdown)
        body = p['body_md']
        # gets converted into raw text via `just_text()` function that i c/p'd from `parse.py`
        author = p['author']
        if author == "WB":
            author = 1
        else:
            author = 2
        published = p['published']
    
        error = None

        if not title:
            title = "<no title>"

        if error is not None:
            flash(error)

        curs = db.cursor()
        check_id = curs.execute('SELECT id FROM post WHERE post.id = ?', (id,))
        result = check_id.fetchone()
        #print(f"DB ID: {result[0]} V. Note ID: {id}", file=sys.stderr)

        if result != None:
            print(f"UPDATING)", file=sys.stderr)
            db.execute(
                'UPDATE post SET title = ?, body_formatted = ? WHERE id = ?',
                (title, body, id)
            )
            db.commit()

        else:
            print(f"CREATING", file=sys.stderr)
            decision = 'Created'
            db.execute('INSERT INTO post (title, body_formatted, published, author_id)'
            ' VALUES (?, ?, ?, ?)',
            (title, body, published, author)
            )
            db.commit()
    
    posts = []

    curs = db.cursor()
    res = curs.execute('SELECT post.id,title,body_formatted,published,name FROM post INNER JOIN author ON author.id=post.author_id')
    all_res = res.fetchall()

    for note in all_res:
        id = note["id"]
        title = note["title"]
        author = note["name"]
        body_md = note["body_formatted"]
        published = note["published"]
        res = {"id": id, "title": title, "body_md": body_md, "author":author, "published": published}

        posts.append(res)

    return jsonify({"posts": posts}), 200

"""DON"T THINK this is needed:
    posts = []
    res = db.execute('SELECT * FROM post').fetchall()
    for note in res:
        id = note["id"]
        title = note["title"]
        body_html = note["body_formatted"]
        body_raw = note["body_raw"]
        published = note["published"]
        res = {"id": id, "title": title, "body_html": body_html, "body_raw": body_raw, "published": published}

        posts.append(res)
    
    return {"message": "Sucessfully POSTed!"}, 200"""

@bp.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('.api_json'))


if __name__ == "__main__":
    api_json()
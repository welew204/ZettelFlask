from cgitb import reset
import imp
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
)
import sys

from bs4 import BeautifulSoup
import bs4 as BS
import ZettelFlask.nlp as nlp

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
    
    g.posts = posts

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


@bp.route('/<id>/delete', methods=('POST',))
def delete(id):
    if id[0] == 'u':
        print(f"This note is not yet saved into the system...id = {id}", file=sys.stderr)
        pass
    else:
        id = int(id)
        get_post(id)
        db = get_db()
        db.execute('DELETE FROM post WHERE id = ?', (id,))
        db.commit()
    return redirect(url_for('.api_json'))


@bp.route('/weights', methods=('GET',))
def weights():
    if 'posts' not in g:
        api_json()

    data = g.posts

    print(f"DATA len: {len(data)}\n -------------------------------", file=sys.stderr)

    db = get_db()
    curs = db.cursor()
    
    wtd_data, stem_ddict, basicVocabIdx, docIDF, all_stems = nlp.run_nlp(data)
    
    wts = {}

    init = True
    for p in wtd_data.keys():
        post = wtd_data[p]

        ## WHAT SHOULD BE THE FORMAT OF THE OUTGOING wts DICT? ie WHAT would be most useful in React?

        curs.execute(f'ALTER TABLE weights ADD COLUMN {p} REAL')
        db.commit()
        print(f"Added column: {p}\n -------------------------------", file=sys.stderr)

        wts[post['title']] = {}
        for s in basicVocabIdx.keys():
            
            w = post['kwvec'][basicVocabIdx[s]]
            
            wts[post['title']][s] = w

            ## ??refactor so that loop generates a tuple of tuples (fmt: (s, docIDF[s], stem_ddict[s][0], w))
            ## ??that can be passed to executemany('INSERT...')
            ## ??for NOT init==True, make tuple of tuples

            #print(f"Column: {p}\nStem: {s}\nWeight: {w} -------------------------------", file=sys.stderr)
            if init == True:
                curs.execute(f'INSERT INTO weights (tag, IDF, best_token, {p}) VALUES (?,?,?,?)', (s, docIDF[s], stem_ddict[s][0], w))
                db.commit()
            else:
                curs.execute(f'UPDATE weights SET {p} = ? WHERE tag="{s}"', (w,))
                db.commit()
              
        init = False

        ## after going through all kwvec for a given P, sort the passed wts so that MOST wtd are first, then pass back into 'wts'
        p_wts_sorted = dict(sorted(wts[post['title']].items(), key=lambda k: k[1], reverse=True))
        wts[post['title']] = p_wts_sorted
    

    
    return jsonify({"weights": wts}), 200

if __name__ == "__main__":
    weights()
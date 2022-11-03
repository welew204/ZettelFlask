import json
import sqlite3
from datetime import datetime
import markdownify as md


blogs_path = "/Users/williamhbelew/Hacking/ZetApp/ZettelApp/ZettelFlask/parsedXML/parsedBlogs.json"
db_path = "/Users/williamhbelew/Hacking/ZetApp/ZettelApp/instance/zettapp.sqlite"

def md_tester_fnc():
    blogs = json.load(open(blogs_path))
    for i in blogs[:1]:
        html = i["formatted_content"]
        to_md = md.markdownify(html, heading_style="ATX")
        print(to_md)

def add_to_DB():
    # create connection and 'cursor' object
    currentDB = sqlite3.connect(db_path)
    cursorDB = currentDB.cursor()

    # Handle DELETE sql query, to clear current DBs, and replace with newer/fresher values :)

    cursorDB.execute('DELETE FROM post;')
    cursorDB.execute('DELETE FROM author;')
    currentDB.commit()

    # define the specific json fields ('fields_list') and db fields [THESE MUST MATCH IN LENGTH ORDER]
    fields_list = ["title", "author", "formatted_content", "raw_content", "pubDate"]
    db_fields = ["title", "author_id", "body_formatted", "published"]

    
    # note sure WHY I need 'fields' (it isn't used)
    fields = ",".join(fields_list)

    # this creates a single comma-seperated string of DB fields
    dbs = ",".join(db_fields)
    # this adds the right length of question marks for the SQL query
    qmrks = ",".join(len(db_fields) * "?")
    # this composes the string with proper formatting to talk to SQL (don't forget the () around the passed-in values!!)
    sql = f'insert into post ({dbs}) values ({qmrks})'

    # opening the json file
    blogs = json.load(open(blogs_path))
    
    # for... loop that:
    # - walks through each blog in json (enumerating an index for me)
    # - list comprehension to grab the defined fields ('fields_list') from each post and stash in `values`
    # - points the cursor to execute the string (`sql`) with the correct parameters (`values`)
    # - simple % checker to see when each 100 posts are written
    for i,post in enumerate(blogs):

        values = [post[f] for f in fields_list]
        if values[1] == "WB":
            values[1] = 1
        else:
            values[1] = 2

        # make date string into proper date timestamp format
        date = values[-1]
        format_str = "%a, %d %b %Y %H:%M:%S %z"
        res = str(datetime.strptime(date, format_str))
        res = res[:10]
        values[-1] = res

        # change html to markdown
        html = values[2]
        to_md = to_md = md.markdownify(html, heading_style="ATX")
        values[2] = to_md
        values.pop(3)


        cursorDB.execute(sql, tuple(values))

        currentDB.commit()

        if i%100 == 0:
            print(i)

    # add the authors
    wb = "WHB"
    hh = "HH"
    cursorDB.execute('INSERT INTO author (name) VALUES (?)', (wb,))
    cursorDB.execute('INSERT INTO author (name) VALUES (?)', (hh,))
    currentDB.commit()


    # this jsut checks how many things got added, and returns a `res` that is printed

    sql2 = "SELECT Count (*) FROM post"
    cursorDB.execute(sql2)
    res = cursorDB.fetchall()

    print(f"done; number of posts = {res}")

# these fncs corrected the dates, but aren't neccessary once I incorporated them into add_to_db()

def format_dates():
    # get the `published` string from DB
    cnxion = sqlite3.connect(db_path)
    curs = cnxion.cursor()

    # first, get the `published` vals; cursor.fetchone() [...which gets me the first one] v cursor.fetchall()
    select_sql_query_str = "SELECT published FROM post"
    curs.execute(select_sql_query_str)
    pub_records = curs.fetchall()

    # update fields in DB

    upd_sql_query_str = "UPDATE post SET published = ?"
    format_str = "%a, %d %b %Y %H:%M:%S %z"

    for d in pub_records:
        date = d[0]
        res = str(datetime.strptime(date, format_str))
        res = res[:10]
        curs.execute(upd_sql_query_str, [res])
        cnxion.commit()
    
    curs.close()

def fix_dates():
    # get the `published` string from DB
    cnxion = sqlite3.connect(db_path)
    curs = cnxion.cursor()
    blogs = json.load(open(blogs_path))

    # first, get the `published` vals; cursor.fetchone() [...which gets me the first one] v cursor.fetchall()
    select_sql_query_str = "SELECT published, title FROM post"
    curs.execute(select_sql_query_str)
    pub_records = curs.fetchall()

    upd_sql_query_str = "UPDATE post SET published = ? WHERE title = ?"
    format_str = "%a, %d %b %Y %H:%M:%S %z"

    for post in blogs:
        title = post["title"]
        date = post["pubDate"]
        res = str(datetime.strptime(date, format_str))
        res = res[:10]
        curs.execute(upd_sql_query_str, (res, title))
        cnxion.commit()
        print(f"updated {title}!")


    # update fields in DB

    
    curs.close()


if __name__ == "__main__":
    add_to_DB()


"""
SQL format of 'published' field:

INSERT INTO "main"."post" ("published") VALUES ('Mon, 20 Jun 2016 13:00:00 +0000');

"""
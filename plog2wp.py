#!/usr/bin/python
# -*- coding: utf-8 -*-

import MySQLdb
import sys

def getconfig():
    config = {}
    config["plogdb"] = {}
    config["plogdb"]["host"] = '127.0.0.1'
    #config["plogdb"]["port"] = '3306'
    config["plogdb"]["user"] = 'root'
    config["plogdb"]["pass"] = 'XXXXX'
    config["plogdb"]["db"] = 'plog'
    config["plogdb"]["charset"] = 'utf8'
    config["wpdb"] = {}
    config["wpdb"]["host"] = '127.0.0.1'
    #config["wpdb"]["port"] = '3306'
    config["wpdb"]["user"] = 'root'
    config["wpdb"]["pass"] = 'XXXXX'
    config["wpdb"]["db"] = 'wp'
    config["wpdb"]["charset"] = 'utf8'
    return config
    
class article:
    pass

def printarc(arc):
    print (arc.pid)
    print (arc.date)
    print (arc.status)
    print (arc.topic)
    print (len(arc.text))
    for cat in arc.categories:
        print ("\t%d" % cat)

def plogsql(sql):
    print("plog: %s" % sql)
    return executesql("plogdb", sql)
    
def wpsql(sql):
    print ("wpdb: %s" % sql)
    return executesql("wpdb", sql)

def executesql(db, sql):
    cfg = getconfig()
    con = MySQLdb.connect(host=cfg[db]["host"], user=cfg[db]["user"], passwd=cfg[db]["pass"], db=cfg[db]["db"], charset=cfg[db]["charset"])
    cs = con.cursor()
    cs.execute(sql)
    if sql.find('select')==0:
        r = cs.fetchall()
    elif sql.find('insert')==0:
        r = cs.lastrowid
    cs.close()
    con.close()
    return r
        
def run():
    r = plogsql("select id, name from plog_articles_categories")
    r1 = wpsql("select term_id, name from wp_terms")
    c1dict = {}
    for c1 in r1:
        c1dict[c1[1]] = c1[0]
    categories = {}
    for c in r:
        if c[1] in c1dict:
            categories[c[0]] = c1dict[c[1]]
    #print categories
    users = ['alex']
    for user in users:
        r = plogsql("select id from plog_users where user='%s'" % user)
        if len(r)==0:
            print ('%s not existed in plog' % user)
            continue
        puid = r[0][0]
        r = wpsql("select id from wp_users where user_login='%s'" % user)
        wuid = r[0][0]
        r = plogsql("select id, date, status from plog_articles where user_id=%s" % puid)
        articlelist = []
        for row in r:
            arc = article()
            arc.pid = row[0]
            arc.date = row[1]
            if row[2]==1:
                arc.status = "publish"
            else:
                arc.status = "private"
            arc.categories = []
            cats = plogsql("select category_id from plog_article_categories_link where article_id=%s" % row[0])
            for cat in cats:
                if not cat[0] in categories:
                    continue
                arc.categories.append(categories[cat[0]])
            r1 = plogsql("select text, topic, normalized_text from plog_articles_text where id=%s" % arc.pid)
            if len(r1)==0:
                print ("blog %s no text" % arc.pid)
                arc.text = ''
                arc.topic = ''
                arc.textfiltered = ''
            else:
                arc.text = r1[0][0]
                arc.text = arc.text.replace("'", "\\'")
                arc.topic = r1[0][1]
                arc.topic = arc.topic.replace("'", "\\'")
                arc.textfiltered = r1[0][2]
                arc.textfiltered = arc.textfiltered.replace("'", "\\'")
            #printarc(arc)
            id = wpsql("insert into wp_posts(post_author,post_date,post_date_gmt,post_content,post_title,post_status,post_name,post_excerpt,to_ping,pinged,post_content_filtered) values(%s,'%s','%s','%s','%s','%s','%s','','','','%s')" % (wuid,arc.date,arc.date,arc.text,arc.topic,arc.status,arc.topic,arc.textfiltered))
            for catid in arc.categories:
                wpsql("insert into wp_term_relationships(object_id, term_taxonomy_id)values(%s,%s)"%(id,catid))

if __name__=="__main__":
    run()

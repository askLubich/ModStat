# -*- coding: utf-8 -*-

import datetime
import time
import requests
import json
import sys
import codecs
import numpy as np

_chuncksize_ = 3600 # use chuncksized of 1h, assuming that there are always fewer than 1000 objects within this period of time
_timeformat_ = '%d.%m.%Y %H:%M:%S'

def _getPushshiftData_(before, after, kind='submission', subreddit='de', size=1000):
    """
    Fetches reddit data via the pushshift api:
        between "before" and "after" given as linux timestamps
        of "kind" submission or comment
        from "subreddit"
        of size "size" (maximum 1000)
    """
    if kind not in ['submission', 'comment']:
        sys.exit('kind must either be submission or comment.')
    url = "https://api.pushshift.io/reddit/search/%s?&size=%i&before=%i&after=%i&subreddit=%s" %(kind,size,before,after,subreddit)
    print url
    req = requests.get(url)
    data = json.loads(req.text)
    data = data['data']
    if len(data) == 1000:
        print 'Warning: Data request reached maximum of 1000 entries.'
    return data
    
def _get_status_(contribution):
    if contribution.removed:
        return 'removed'
    elif contribution.approved:
         return 'approved'
    elif contribution.approved_by != None:  
    #elif contribution.approved_by not in [None, 'MarktpLatz']:  
        # for some reason, the API does always return 'None', 
        # regardless of true status for requests earlier than 01.17.
        # For approved stuff, this can be fixed by looking at approved_by,
        # for the other statuses, this cannot be fixed.
        return 'approved'
    elif contribution.spam:
        return 'spam'
    else:
        return 'none'

def _cleanPushshiftData_(r, data):
    """
    Clean up pushshift data: throw out deleted and removed comments and submissions.
    """
    if len(data) == 0:
        return []
    try:
        # is submission if has title field, otherwise is comment
        data[0]['title']
        prefix = 't3_'
    except KeyError:
        prefix = 't1_'
    
    IDs = [prefix + d['id'] for d in data]
    content = r.info(fullnames = IDs)
    D = []
    i = 0
    for c in content:
        if c.author != None:  # author is none if content was removed or deleted
            data[i]['author'] = unicode(c.author)  # update author
            data[i]['score'] = c.ups  # update score
            data[i]['status'] = _get_status_(c)
            if   prefix == 't1_':
                data[i]['body'] = c.body  # update body of comment
            elif prefix == 't3_':
                if data[i]['is_self']:
                    data[i]['selftext'] = c.selftext  # update text for selfposts
                else:
                    data[i]['url'] = c.url  # update link for linkposts
                data[i]['link_flair_text'] =  c.link_flair_text # update flair
                data[i]['link_flair_css_class'] = c.link_flair_css_class
                data[i]['num_comments'] = c.num_comments  # update number of comments
            D.append(data[i])
        i = i + 1            
    return D

def _str2timestamp_(string):
    t = time.mktime(datetime.datetime.strptime(string, _timeformat_).timetuple())
    return int(t)

def _timestamp2str_(timestamp):
    return datetime.datetime.fromtimestamp(timestamp).strftime(_timeformat_)

def get_data(r, start, end, kind='submission', subreddit='de'):
    """
    Fetches reddit data:
        between "start" and "end" hours ago (specified as per __timeformat)
        of "kind" submission or comment
        from "subreddit"
    Makes multiple calls until all data is produced.
    """  
    # convert start and end to timestamps
    start = _str2timestamp_(start)
    end   = _str2timestamp_(end)
    
    D = []
    current = start      
    while current < end:
        print 'Fetching %s' %_timestamp2str_(current)
        d = _getPushshiftData_(min(end,current+_chuncksize_), current,
                               kind=kind, subreddit=subreddit, size=1000)
        d = _cleanPushshiftData_(r, d)
        D = D + d
        current = current + _chuncksize_
    return D

def _get_post_content_(post):
    if post['is_self']:
        try:
            content = post['selftext'].replace('\n',' ').replace('\t',' ').replace('\r',' ')
        except KeyError:
            content = ' '
    else:
        content = post['url'].split()[0]
    return content

def _get_comment_content_(comment):
    if comment['body'] != '':
        return comment['body'].replace('\n',' ').replace('\t',' ').replace('\r',' ') 
    else:
        return ' '

def _get_post_flair_(post):
    try:
        flair = post['link_flair_css_class']
        if flair != None:
            return flair
        else:
            return ' '
    except KeyError:
        return ' '
    
def _get_author_flair_(post):
    flair = post['author_flair_css_class']
    if flair != None:
        return flair
    else:
        return ' '
    
def data2file(D, filename, kind='submission'):
    """
    Takes a data-dict and converts in to a string that can then be saved
    to a file.
    """
    
    f = codecs.open(filename,'w',"utf-8")    
    
    # write header line
    if kind == 'submission':
        header = "# time \t id \t score \t num_comments \t author \t author_flair \t title \t flair \t content \t status \n"
    elif kind == 'comment':
        header = '# time \t id \t link_id \t parent_id \t score \t author \t author_flair \t content \t status \n'
    f.write(header)
    
    for d in D:
        post = d
        pid = post['id']
        ptime = _timestamp2str_(post['created_utc'])
        pauthor = post['author']
        pups = str(post['score'])
        pauthor_flair = _get_author_flair_(post)
        pstatus = post['status']
        
        if kind == 'submission':
            pcomm = str(post['num_comments'])
            pflair = _get_post_flair_(post)
            ptitle = post['title'].replace('\n',' ').replace('\t',' ').replace('\r',' ') 
            pcontent = _get_post_content_(post)
            ptitle = post['title'].replace('\n',' ').replace('\t',' ').replace('\r',' ') 
            line = ptime + '\t' + pid + '\t' + pups + '\t' + pcomm + '\t' + pauthor \
                    + '\t' + pauthor_flair + '\t' + ptitle + '\t' + pflair + '\t' + pcontent \
                    + '\t' + pstatus + '\n'
        elif kind == 'comment':
            pcontent = _get_comment_content_(post)
            pparent = post['parent_id']
            plinkid = post['link_id']
            line = ptime + '\t' + pid + '\t' + plinkid + '\t' + pparent + '\t' + pups + '\t' + pauthor \
                    + '\t' + pauthor_flair + '\t' + pcontent + '\t' + pstatus + '\n'
        f.write(line)
    f.close()
    
_datatypes_ = {
        'time': str,
        'id': str,
        'score': int,
        'num_comments': int,
        'author': unicode,
        'author_flair': unicode,
        'title': unicode,
        'flair': str,
        'content': unicode,
        'link_id': str,
        'parent_id': str,
        'created_utc': int,
        'status': str,
        }
    
def file2data(filename):
    """
    Reads a data file into a dict.
    """
    f = codecs.open(filename,'r',"utf-8")
    
    header = f.readline()
    if header[0] == '#':
        header = header[1:]
    keys = [ k.strip() for k in header.split('\t') ]
    
    D = []
    lines = f.read().split('\n')
    for line in lines:
        if line == '':
            continue
        cols = [ l.strip() for l in line.split('\t') ]
        d = {}
        for c,k in zip(cols,keys):
            d[k] = _datatypes_[k](c)
        D.append(d)
        
    f.close()
    return D

def _percentiles_(array):
    l = np.percentile(array,  5)
    m = np.percentile(array, 50)
    r = np.percentile(array, 95)
    return l,m,r
    
def keynumbers(A, kind='submission'):
    D = {}
    
    D['N'] = len([1 for d in A if d['status'] in ['none','approved']])
    D['scores'] = np.array([ d['score'] for d in A  if d['status'] in ['none','approved']])
    D['scores_percentiles'] = _percentiles_(D['scores'])
    Users = [ d['author'] for d in A if d['status'] in ['none','approved']]
    D['users'] = Users
    D['N_users_unique'] = len(list(set(Users)))
    D['N_approved'] = len([1 for d in A if d['status'] == 'approved'])
    
    if kind == 'submission':
        D['comments'] = np.array([ d['num_comments'] for d in A if d['status'] in ['none','approved']])
        D['comments_percentiles'] = _percentiles_(D['comments'])
        D['length'] = np.array([ len(d['title']) for d in A if d['status'] in ['none','approved']])
    elif kind == 'comment':
        D['length'] = np.array([ len(d['content']) for d in A if d['status'] in ['none','approved']])
        
    D['length_percentiles'] = _percentiles_(D['length'])
    
    ndx_top = np.argmax(D['scores'])
    IDs = [ d['id'] for d in A if d['status'] in ['none','approved']]
    D['top_contribution'] = IDs[ndx_top], Users[ndx_top], D['scores'][ndx_top]
    
    return D
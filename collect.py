# -*- coding: utf-8 -*-

import fetch_content
import logon

start = '01.06.2017 00:00:00'
end   = '30.06.2017 23:59:59'
name  = '1706.dat'

user_agent = 'askLubich collecting some statistics about /r/de'

r = logon.login(user_agent)

#%%
# collecting submissions
D = fetch_content.get_data(r, start, end, kind='submission', subreddit='de')
fetch_content.data2file(D, 'data/user_data/submission/%s' %name, kind='submission')

#%% collecting comments
D = fetch_content.get_data(r, start, end, kind='comment', subreddit='de')
fetch_content.data2file(D, 'data/user_data/comment/%s' %name, kind='comment')
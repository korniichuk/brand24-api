#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# Version 0.1a1

import os
import time

from fbi import getpassword
from requestium import Session

username = 'info@korniichuk.com'
passwd = getpassword('~/.key/brand24.enc')
sid = '250201232'

driver = '/usr/lib/chromium-browser/chromedriver'
s = Session(webdriver_path=driver,
            browser='chrome',
            default_timeout=15,
            webdriver_options={'arguments': ['headless']})

def download_xlsx(s, username, passwd, sid, download_path=None):
    """Export data from www.brand24.com website as xlsx file (Excel) to
       download path and return session.
    Input:
        s -- Requestium session (required |
             type: requestium.requestium.Session);
        username -- username on www.brand24.com (required | type: str);
        passwd -- password for username on www.brand24.com (required |
                  type: str);
        sid -- sid on www.brand24.com (required | type: str);
        download_path -- download path (not required | type: str).
    Output:
        s -- Requestium session (type: requestium.requestium.Session).
    """

    s = login(s, username, passwd)
    s.driver.command_executor._commands['send_command'] = ('POST',
            '/session/$sessionId/chromium/send_command')
    if download_path == None:
        download_path = os.getcwd()
    params = {'cmd': 'Page.setDownloadBehavior',
              'params': {'behavior': 'allow', 'downloadPath': download_path}}
    s.driver.execute('send_command', params)
    url = 'https://app.brand24.com/panel/results/?sid=%s' % sid
    s.driver.get(url)
    s.driver.ensure_element_by_id('results_download').click()
    return s

def login(s, username, passwd):
    """Login to www.brand24.com with username/passwd pair and return session.
    Input:
        s -- Requestium session (required |
             type: requestium.requestium.Session);
        username -- username on www.brand24.com (required | type: str);
        passwd -- password for username on www.brand24.com (required |
                  type: str).
    Output:
        s -- Requestium session (type: requestium.requestium.Session).
    """

    url = 'https://app.brand24.com/user/login/'
    s.driver.get(url)
    s.driver.ensure_element_by_name('login').send_keys(username)
    s.driver.ensure_element_by_name('password').send_keys(passwd)
    s.driver.ensure_element_by_id('login_button').click()
    time.sleep(3)
    return s

# Example. Export data from www.brand24.com website as xlsx file (Excel) to
# current directory
#download_xlsx(s, username, passwd, sid)

# Example. Export data from www.brand24.com website as xlsx file (Excel) to
# '/tmp' directory
#download_xlsx(s, username, passwd, sid, download_path='/tmp')

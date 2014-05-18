#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import socket
import sys
import traceback

import paramiko
import re

# setup logging
# paramiko.util.log_to_file('demo.log')


def getOnlineUserNumber():
    username = 'bbs'
    hostname = 'ptt.cc'
    port = 22

    # now connect

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((hostname, port))
    except Exception, e:
        print '*** Connect failed: ' + str(e)
        traceback.print_exc()
        sys.exit(1)

    try:
        t = paramiko.Transport(sock)
        try:
            t.start_client()
        except paramiko.SSHException:
            print '*** SSH negotiation failed.'
            sys.exit(1)

        # check server's host key -- this is important.

        # should be 85:72:37:b1:6d:98:c8:0c:80:97:6a:9f:eb:1c:4e:3b. ??
        key = t.get_remote_server_key()
        #print key.get_fingerprint()

        # get username
        t.auth_password(username, '')
        if not t.is_authenticated():
            t.close()
            sys.exit(1)

        chan = t.open_session()
        chan.get_pty()
        chan.invoke_shell()
        p = re.compile('\[[\d+;]*[mH]')
        chan.settimeout(3.0)
        screen = ''
        while True:
            try:
                text = chan.recv(102400)
                if not text:
                    break
                screen += text
            except:
                break
        chan.close()
        t.close()

        screen = screen.decode('big5','replace')

        # remove colar code

        screen = re.sub('\[[\d+;]*[mH]', '', screen)

        # remove escape characters

        screen = re.sub(r'[\r]', '', screen)

        # remove escape characters

        screen = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]', '',
                screen)

        return int((re.findall(r'【\d+】', screen.encode('utf-8'))[-1])[3:-3])
    except Exception, e:

        print '*** Caught exception: ' + str(e.__class__) + ': ' + str(e)
        traceback.print_exc()
        try:
            t.close()
        except:
            pass
        sys.exit(1)

if __name__ == '__main__':
    print getOnlineUserNumber()

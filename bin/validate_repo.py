#!/usr/bin/env python3
#
# check that the repo branch and path are valid
#

import argparse
import datetime
import json
import os
import pathlib
import re
import sh
import shutil
import sys
import tempfile
import time
import unidecode
import urllib.request
import yaml

#
# Hack since urllib always follows redirects
#
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        #LATER: pass the error up instead of reporting it here
        sys.stdout.write("DEBUG: redirect url is %s\n" % (newurl))
        return None
opener = urllib.request.build_opener(NoRedirect)
urllib.request.install_opener(opener)

parser = argparse.ArgumentParser()
parser.add_argument("-q", "--quiet", help="hide status messages", default=True, dest='verbose', action="store_false")
parser.add_argument("--input", help="YAML of potential repos", action="store", default="data/sources.yaml")
parser.add_argument("--provider", help="only do specific provider", action="store", default="*", dest="provider")
parser.add_argument('repos', help='repos (all if none specified)', metavar='repos', nargs='*')

args = parser.parse_args()

if args.verbose:
    print("INFO: validate_repo starting at %s" % datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))

fdata = open(args.input, "r")
rawdata = yaml.safe_load(fdata)
fdata.close()

repolist = {}
for data in rawdata:
    repolist[data['handle']] = data
if args.verbose:
    print("INFO: %d repo definitions loaded from %s" % (len(rawdata), args.input))

if len(args.repos) == 0:
    args.repos = repolist.keys()
if args.verbose:
    print("INFO: will process %d repo(s)" % (len(args.repos)))

origdir = os.getcwd()

failCount = 0

for repo_handle in args.repos:

    if repo_handle not in repolist:
        sys.stdout.write("ERROR: no repository info for handle '%s'\n" % (repo_handle))
        sys.exit(1)

    repodata = repolist[repo_handle]

    if args.provider != '*' and args.provider != repodata['provider']:
        sys.stdout.write("INFO: skipping %s (provider is %s, not %s)\n" % (repo_handle, repodata['provider'], args.provider))
        continue

    if args.verbose:
        sys.stdout.write("INFO: processing %s (%s)\n" % (repo_handle, repodata["repo"]))

    if repodata['provider'] == 'github':
        giturl = "https://github.com/%s/tree/%s/%s" % (repodata['repo'], repodata['branch'], urllib.parse.quote(repodata['directory']))
    elif repodata['provider'] == 'gitlab':
        giturl = "https://gitlab.com/%s/-/tree/%s/%s" % (repodata['repo'], repodata['branch'], urllib.parse.quote(repodata['directory']))
    else:
        sys.stderr.write("ERROR: unknown or missing provider '%s'\n" % repodata['provider'])
        sys.exit(3)

    if args.verbose:
        sys.stdout.write("INFO: url is %s\n" % (giturl))

    try:
        response = urllib.request.urlopen(giturl) #, {}, {'User-Agent': 'VectorLogoZone (https://github.com/vectorlogozone/git-svg-icons)' })
        if response.status != 200:
            failCount += 1
            sys.stdout.write("FAILURE: %s (%d: %s)\n" % (repodata['repo'], response.status, giturl))
            continue
        if args.verbose:
            sys.stdout.write("PASS: %s (%d)\n" % (repodata['repo'], response.status))
    except urllib.error.HTTPError as e:
        failCount += 1
        sys.stdout.write("FAILURE: %s (%s: %s)\n" % (repodata['repo'], e.reason, giturl))

    time.sleep(1)

os.chdir(origdir)

sys.stdout.write("INFO: validate_repo complete: %d errors found at %s\n" % (failCount, datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')))

if failCount > 0:
    sys.exit(2)


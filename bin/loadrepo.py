#!/usr/bin/env python3
#
# get the list of svg images from a repo
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
import yaml

default_branch = "master"

parser = argparse.ArgumentParser()
parser.add_argument("-q", "--quiet", help="hide status messages", default=True, dest='verbose', action="store_false")
parser.add_argument("--always", help="always process", default=False, dest='always', action="store_true")
parser.add_argument("--branch", help="git branch (default='%s')" % default_branch, action="store", default=default_branch)
parser.add_argument("--cache", help="location of previously downloaded repo", action="store", default="./cache")
parser.add_argument("--cdnprefix", help="prefix for CDN URLs", action="store", default="")
parser.add_argument("--input", help="YAML of potential repos", action="store", default="data/sources.yaml")
parser.add_argument("--output", help="output directory", action="store", default="./local")
parser.add_argument("--nocleanup", help="do not erase temporary files", default=True, dest='cleanup', action="store_false")
parser.add_argument("--nocopy", help="do not copy files", action="store_false", default=True, dest='copy')
parser.add_argument("--nosparse", help="do not do a sparse checkout", action="store_false", default=True, dest='sparse')
parser.add_argument("--provider", help="only do specific provider", action="store", default="*", dest="provider")
parser.add_argument('repos', help='repos (all if none specified)', metavar='repos', nargs='*')

args = parser.parse_args()

if args.verbose:
    print("INFO: loadrepo starting at %s" % datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))

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

total = 0
origdir = os.getcwd()
cachedir = os.path.abspath(args.cache)
outputdir = os.path.abspath(args.output)

pathlib.Path(cachedir).mkdir(parents=True, exist_ok=True)
pathlib.Path(outputdir).mkdir(parents=True, exist_ok=True)

for repo_handle in args.repos:

    if repo_handle not in repolist:
        sys.stdout.write("ERROR: no repository info for handle '%s'\n" % (repo_handle))
        sys.exit(1)

    repodata = repolist[repo_handle]

    if args.provider != '*' and args.provider != repodata['provider']:
        sys.stdout.write("INFO: skipping %s (provider is %s, not %s)\n" % (repo_handle, repodata['provider'], args.provider))
        continue

    sys.stdout.write("OUTPUT: processing %s (%s)\n" % (repo_handle, repodata["repo"]))

    gitdir = os.path.join(cachedir, repo_handle)
    if args.verbose:
        sys.stdout.write("INFO: git repo directory %s\n" % gitdir)

    if repodata['provider'] == 'github':
        giturl = "https://github.com/" + repodata['repo']
    elif repodata['provider'] == 'gitlab':
        giturl = "https://gitlab.com/" + repodata['repo'] + ".git/"
    else:
        sys.stderr.write("ERROR: unknown or missing provider '%s'\n" % repodata['provider'])
        sys.exit(3)

    if os.path.isdir(gitdir):
        os.chdir(gitdir)

        cached_commit = sh.git("rev-parse", "HEAD", "--", _err_to_out=True)

        if args.verbose:
            sys.stdout.write("INFO: pulling changes from git repo %s\n" % giturl)
        sh.git.pull("--ff-only", "origin", repodata["branch"], _err_to_out=True, _out=sys.stdout)
        if args.verbose:
            sys.stdout.write("INFO: pull complete\n")

        current_commit = sh.git("rev-parse", "HEAD", _err_to_out=True)
        if cached_commit == current_commit:
            if args.always:
                sys.stdout.write("INFO: no changes to repo since last run but processing anyway\n")
            else:
                sys.stdout.write("INFO: no changes to repo since last run so skipping\n")
                continue
    else:
        if args.verbose:
            sys.stdout.write("INFO: retrieving git repo %s (sparse=%s)\n" % (giturl, args.sparse))

        if args.sparse:
            # full clone takes too long
            #
            os.mkdir(gitdir)
            os.chdir(gitdir)
            sh.git.init(_err_to_out=True, _out=sys.stdout)
            sh.git.remote('add', 'origin', giturl, _err_to_out=True, _out=sys.stdout)
            if len(repodata["directory"]) > 0:
                sparse_dir = '\\' + repodata["directory"] if repodata["directory"][0] == '!' else repodata["directory"]
                sh.git.config('core.sparsecheckout', 'true', _err_to_out=True, _out=sys.stdout)
                fsc = open(".git/info/sparse-checkout", "a")
                fsc.write("%s/*\n" % sparse_dir)
                fsc.close()
            sh.git.pull("--ff-only", "--depth=1", "origin", repodata["branch"], _err_to_out=True, _out=sys.stdout)
            if args.verbose:
                sys.stdout.write("INFO: sparse pull complete\n")
        else:
            sh.git.clone(giturl, gitdir, _err_to_out=True, _out=sys.stdout)
            os.chdir(gitdir)

            if args.verbose:
                sys.stdout.write("INFO: clone complete\n")

    if args.verbose:
        sys.stdout.write("INFO: switching to branch '%s'\n" % (repodata['branch']))
    sh.git.checkout(repodata['branch'], _err_to_out=True, _out=sys.stdout)

    current_commit = sh.git("rev-parse", "HEAD", _err_to_out=True)
    last_mod = ("%s" % sh.git.log("-1", "--format=%cd", "--date=iso", _tty_out=False)).strip()
    sys.stdout.write("INFO: last modified on %s\n" % last_mod)

    logodir = os.path.join(gitdir, repodata['directory'])
    if args.verbose:
        sys.stdout.write("INFO: copying svgs from %s\n" % logodir)

    images = []

    pathfix = re.compile(repodata["rename"][0]) if "rename" in repodata else None
    include_pattern = re.compile(repodata["include"]) if "include" in repodata else None
    exclude_pattern = re.compile(repodata["exclude"]) if "exclude" in repodata else None

    srcpaths = []
    for srcpath in pathlib.Path(logodir).glob("**/*.svg"):
        s = str(srcpath)
        try:
            s.encode("utf-8")
        except UnicodeEncodeError:
            filtered = [ch if ord(ch) < 128 else '.' for ch in s]
            sys.stdout.write("WARNING: skipping invalid unicode filename %s\n" % ''.join(filtered))
            continue

        srcpaths.append(s)

    srcpaths.sort()
    for srcpath in srcpaths:

        if (os.path.islink(srcpath)):
            sys.stdout.write("WARNING: skipping symlink %s\n" % srcpath)
            continue

        shortpath = os.path.join(repo_handle, srcpath[len(logodir)+1:] if len(repodata["directory"]) > 0 else srcpath[len(logodir):])

        fixdir, fixname = os.path.split(shortpath)

        if include_pattern:
            includepath = os.path.join(srcpath[len(logodir)+1:] if len(repodata["directory"]) > 0 else srcpath[len(logodir):])
            if include_pattern.match(includepath) == None:
                if args.verbose:
                    sys.stdout.write("INFO: include filter is skipping '%s'\n" % (includepath))
                continue
            else:
                if args.verbose:
                    sys.stdout.write("INFO: include filter okay for '%s'\n" % (includepath))

        if exclude_pattern:
            excludepath = os.path.join(srcpath[len(logodir)+1:] if len(repodata["directory"]) > 0 else srcpath[len(logodir):])
            if exclude_pattern.match(excludepath) != None:
                if args.verbose:
                    sys.stdout.write("INFO: exclude filter is skipping '%s'\n" % (excludepath))
                continue
            else:
                if args.verbose:
                    sys.stdout.write("INFO: exclude filter okay for '%s'\n" % (excludepath))

        if pathfix is not None:
            fixname = pathfix.sub(repodata["rename"][1], fixname)

        fixname = unidecode.unidecode(fixname)

        name = os.path.splitext(fixname)[0]

        fixname = re.sub(r"[^a-z0-9]+", "-", name.lower()) + ".svg"
        fixdir = re.sub(r"[^/a-z0-9]+", "-", fixdir.lower())

        shortpath = os.path.join(fixdir, fixname)

        dstpath = os.path.join(outputdir, shortpath)

        #if (pathlib.Path(dstpath).exists()):
        #	continue

        dstdir, dstname = os.path.split(dstpath)

        if args.copy:
            pathlib.Path(dstdir).mkdir(parents=True, exist_ok=True)
            shutil.copyfile(srcpath, dstpath)

            if args.verbose:
                sys.stdout.write("DEBUG: repo %s copy from '%s' to '%s' (%s)\n" % (repo_handle, str(srcpath), dstpath, shortpath))

            imgurl = args.cdnprefix + shortpath
        elif repodata['provider'] == 'github':
            imgurl = "https://raw.githubusercontent.com/" + repodata["repo"] + "/" + repodata["branch"] + srcpath[len(gitdir):]
        elif repodata['provider'] == 'gitlab':
            imgurl = "https://gitlab.svg.zone/" + repodata["repo"] + "/raw/" + repodata["branch"] + srcpath[len(gitdir):]

        images.append({
            'name': name,
            'src': giturl + "/blob/" + repodata['branch'] + srcpath[len(gitdir):],
            'img': imgurl
            })

    sys.stdout.write("OUTPUT: %d svg files found for %s (%s)\n" % (len(images), repo_handle, repodata['repo']))
    total += len(images)

    if len(images) == 0:
        continue

    repodata['commit'] = str(current_commit).strip()

    data = {
        'data': repodata,
        'handle': repo_handle,
        'lastmodified': last_mod,
        'name': repodata['name'] if 'name' in repodata else repo_handle,
        'provider': repodata['provider'],
        'provider_icon': 'https://www.vectorlogo.zone/logos/' + repodata['provider'] + '/' + repodata['provider'] + '-icon.svg',
        'url': giturl,
        'images': images
    }
    if 'logo' in repodata:
        data['logo'] = repodata['logo']
    if 'website' in repodata:
        data['website'] = repodata['website']

    pathlib.Path(os.path.join(outputdir, repo_handle)).mkdir(parents=True, exist_ok=True)
    outputpath = os.path.join(outputdir, repo_handle, "sourceData.json")

    outputfile = open(outputpath, 'w')
    json.dump(data, outputfile, sort_keys=True, indent=2)
    outputfile.close()

os.chdir(origdir)

if args.verbose:
    sys.stdout.write("INFO: loadrepo complete: %d logos found at %s\n" % (total, datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')))

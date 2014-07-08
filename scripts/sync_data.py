#!/usr/bin/env python
# **************************************************************************
# *
# * Authors:     I. Foche Perez (ifoche@cnb.csic.es)
# *              J. Burguet Castell (jburguet@cnb.csic.es)
# *
# * Unidad de  Bioinformatica of Centro Nacional de Biotecnologia , CSIC
# *
# * This program is free software; you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation; either version 2 of the License, or
# * (at your option) any later version.
# *
# * This program is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# * GNU General Public License for more details.
# *
# * You should have received a copy of the GNU General Public License
# * along with this program; if not, write to the Free Software
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
# * 02111-1307  USA
# *
# *  All comments concerning this program package may be sent to the
# *  e-mail address 'ifoche@cnb.csic.es'
# *
# **************************************************************************

"""
Scipion data synchronization.
"""

from __future__ import division

import sys
import os
from os.path import join, isdir, exists, relpath, dirname
from subprocess import call
import time
import argparse
import hashlib
from urllib2 import urlopen
import getpass


scipion_logo = """
QQQQQQQQQT!^'::""?$QQQQQQ  S   S   S
QQQQQQQY`          ]4QQQQ  C   C   C
QQQQQD'              "$QQ  I   I   I
QQQQP                 "4Q  P   P   P
QQQP        :.,        -$  I   I   I
QQD       awQQQQwp      )  O   O   O
QQ'     qmQQQWQQQQg,   jm  N   N   N
Qf     QQQD^   -?$QQp jQQ ################################################
Q`    qQQ!        4WQmQQQ # Integrating image processing packages for EM #
F     QQ[          ~)WQQQ ################################################
[    ]QP             4WQQ
f    dQ(             -$QQ Data synchronization script
'    QQ              qQQQ
.   )QW            _jQQQQ
-   =QQ           jmQQQQQ
/   -QQ           QQQQQQQ
f    4Qr    jQk   )WQQQQQ
[    ]Qm    ]QW    "QQQQQ
h     $Qc   jQQ     ]$QQQ
Q,  :aQQf qyQQQL    _yQQQ
QL jmQQQgmQQQQQQmaaaQWQQQ
"""


def main():
    # Arguments parsing
    parser = argparse.ArgumentParser(description=__doc__)
    g = parser.add_mutually_exclusive_group()
    g.add_argument('--download', action='store_true', help="Download dataset.")
    g.add_argument(
        '--upload', action='store_true',
        help=("Upload local dataset to the scipion server. The dataset name must"
              "be the name of its folder relative to the SCIPION_TESTS folder."))
    g.add_argument(
        '--list', action='store_true',
        help=('List local datasets (from $SCIPION_TESTS) and remote ones '
              '(remote url can be specified with --url).'))
    g.add_argument(
        '--format', action='store_true',
        help='Create a MANIFEST file with checksums in the datasets folders.')
    add = parser.add_argument  # shortcut
    add('datasets', metavar='DATASET', nargs='*', help='Name of a dataset.')
    add('--delete', action='store_true',
        help=('When uploading, delete any remote files in the dataset not'
              'present in local. It leaves the remote scipion data directory '
              'as it is in the local one. Dangerous, use with caution.'))
    add('-u', '--url',
        default='http://scipionwiki.cnb.csic.es/files/scipion/data/tests',
        help='URL where remote datasets will be looked for.')
    add('--check-all', action='store_true',
        help='See if there is any remote dataset not in sync with locals.')
    add('-v', '--verbose', action='store_true', help='Print more details.')
    args = parser.parse_args()

    #print scipion_logo

    # Dispatch the easy cases first (list and check), and then take care of
    # the more complex ones.
    if args.list:
        listDatasets(args.url)
        sys.exit(0)

    if args.check_all:
        datasets = [x.strip('./') for x in
                    urlopen('%s/MANIFEST' % args.url).read().splitlines()]
        if args.verbose:
            print 'Datasets: %s' % ' '.join(datasets)

        all_uptodate = True
        for dataset in datasets:
            all_uptodate &= check(dataset, url=args.url, verbose=args.verbose)
        sys.exit(0 if all_uptodate else 1)

    if not args.datasets:
        sys.exit('At least --list, --check-all or datasets needed.\n'
                 'Run with --help for more info.')

    print 'Selected datasets: %s' % ' '.join(args.datasets)

    if args.format:
        for dataset in args.datasets:
            print 'Formatting %s' % dataset
            if not exists(join(os.environ['SCIPION_TESTS'], dataset)):
                sys.exit('ERROR: %s folder does not exist in datasets folder %s.' %
                         (dataset, os.environ['SCIPION_TESTS']))
            createMANIFEST(join(os.environ['SCIPION_TESTS'], dataset))
        sys.exit(0)

    if args.download:
        # Download datasets.
        for dataset in args.datasets:
            if exists(join(os.environ['SCIPION_TESTS'], dataset)):
                print 'Local copy of dataset %s detected.' % dataset
                print 'Checking for updates...'
                update(dataset, url=args.url, verbose=args.verbose)
            else:
                print 'Dataset %s not in local machine. Downloading...' % dataset
                download(dataset, url=args.url, verbose=args.verbose)
        sys.exit(0)

    if args.upload:
        # Upload datasets.
        for dataset in args.datasets:
            try:
                upload(dataset, delete=args.delete)
            except Exception as e:
                print 'Error when uploading dataset %s: %s' % (dataset, e)
                if ask() != 'y':
                    sys.exit(1)
        sys.exit(0)

    # If we get here, we did not use the right arguments. Show a little help.
    parser.print_usage()


def listDatasets(url):
    """ Print a list of local and remote datasets """

    tdir = os.environ['SCIPION_TESTS']
    print "Local datasets in %s" % tdir
    for folder in sorted(os.listdir(tdir)):
        if isdir(join(tdir, folder)):
            if exists(join(tdir, folder, 'MANIFEST')):
                print "  * " + folder
            else:
                print "  * " + folder + ' (not in dataset format)'

    try:
        print "\nRemote datasets in %s" % url
        data = urlopen(url + '/MANIFEST').read()
        for line in sorted(data.splitlines()):
            print "  * " + line.strip('./')
    except Exception as e:
        print 'Error reading %s (%s)' % (url, e)


def check(dataset, url, verbose=False):
    """ See if our local copy of dataset is the same as the remote one.
    Return True if it is (if all the checksums are equal), False if not.
    """
    def vlog(txt): sys.stdout.write(txt) if verbose else None  # verbose log

    vlog('Checking dataset %s ... ' % dataset)
    try:
        md5sRemote = dict(x.split() for x in
                          urlopen('%s/%s/MANIFEST' %
                                  (url, dataset)).read().splitlines())

        md5sLocal = dict(x.split() for x in
                         open('%s/MANIFEST' %
                              join(os.environ['SCIPION_TESTS'], dataset)))
        if md5sRemote == md5sLocal:
            vlog('\tlooks up-to-date\n')
            return True
        else:
            vlog('\thas differences\n')
            return False
    except Exception as e:
        vlog('\terror: %s\n' % e)
        return False


def download(dataset, destination=None, url=None, verbose=False):
    """ Download all the data files mentioned in url/datasetName/MANIFEST """

    destination = destination if destination else os.environ['SCIPION_TESTS']

    # First make sure that we ask for a known dataset.
    datasetsAvailable = [x.strip('./') for x in
                         urlopen('%s/MANIFEST' % url).read().splitlines()]
    if dataset not in datasetsAvailable:
        print 'Unknown dataset "%s".' % dataset
        print 'Use --list to see the available datasets.'
        return

    # Retrieve the dataset's MANIFEST file.
    # It contains a list of "file md5sum" of all files included in the dataset.
    datasetFolder = join(destination, dataset)
    os.makedirs(datasetFolder)
    manifest = join(destination, dataset, 'MANIFEST')
    try:
        if verbose:
            print "Retrieving MANIFEST file"
        data = urlopen('%s/%s/MANIFEST' % (url, dataset)).read()
        open(manifest, 'w').write(data)
    except Exception as e:
        print "ERROR reading %s/%s/MANIFEST (%s)" % (url, dataset, e)
        return

    # Now retrieve all of the files mentioned in MANIFEST, and check their md5.
    print 'Fetching files of dataset "%s"...' % dataset
    manifestLines = open(manifest).readlines()
    totalNumber = len(manifestLines)
    prevPercent = 0
    for number, line in enumerate(manifestLines):
        fname, md5InLine = line.strip().split()
        fpath = join(datasetFolder, fname)
        try:
            # Create file with downloaded content
            data = urlopen('%s/%s/%s' % (url, dataset, fname)).read()
            if not isdir(dirname(fpath)):
                os.makedirs(dirname(fpath))
            open(fpath, 'w').write(data)

            percent = ((number+1)/(totalNumber*1.0))*100
            if verbose:
                sys.stdout.write('\t( %3d %% )\t%s' % (percent, fname))
            else:
                progress = percent - prevPercent
                sys.stdout.write("#" * int(1 + progress))
                sys.stdout.flush()
            prevPercent = percent

            md5 = md5sum(fpath)
            assert md5 == md5InLine, \
                'Bad md5. Expected: %s Computed: %s' % (md5InLine, md5)
            if verbose:
                sys.stdout.write('    \tMD5 OK\n')
        except Exception as e:
            print "\nError in %s (%s)" % (fname, e)
            print "URL: %s/%s/%s" % (url, dataset, fname)
            print "Destination: %s" % fpath
            if ask('Continue downloading? (y/[n]): ', ['y', 'n', '']) != 'y':
                return
    print


def update(dataset, workingCopy=None, url=None, verbose=False):
    """ Update local dataset with the contents of the remote one.
    It compares the md5 of remote files in url/dataset/MANIFEST with the
    ones in workingCopy/dataset/MANIFEST, and downloads only when necessary.
    """
    # Get default values for variables if we got none
    workingCopy = workingCopy or os.environ['SCIPION_TESTS']

    # Verbose log
    def vlog(txt): sys.stdout.write(txt) if verbose else None

    # Read contents of *remote* MANIFEST file, and create a dict {fname: md5}
    manifestRaw = urlopen('%s/%s/MANIFEST' % (url, dataset)).read()
    md5sRemote = dict(x.split() for x in manifestRaw.splitlines())

    # Update and read contents of *local* MANIFEST file, and create a dict
    datasetFolder = join(workingCopy, dataset)
    try:
        last = max(os.stat(join(datasetFolder, x)).st_mtime for x in md5sRemote)
        t_manifest = os.stat(join(datasetFolder, 'MANIFEST')).st_mtime
        assert t_manifest > last and time.time() - t_manifest < 60*60*24*7
    except (OSError, IOError, AssertionError) as e:
        print 'Regenerating local MANIFEST...'
        createMANIFEST(datasetFolder)
    md5sLocal = dict(x.split() for x in open(join(datasetFolder, 'MANIFEST')))

    # Check that all the files mentioned in MANIFEST are up-to-date
    print "Verifying MD5s..."

    filesUpdated = 0  # number of files that have been updated
    taintedMANIFEST = False  # can MANIFEST be out of sync?

    for fname in md5sRemote:
        vlog('\t%s' % fname)
        fpath = join(datasetFolder, fname)
        try:
            if exists(fpath) and md5sLocal[fname] == md5sRemote[fname]:
                vlog('\r\tOK  %s\n' % fname)
                pass  # just to emphasize that we do nothing in this case
            else:
                vlog('\r\tXX  %s  (downloading... ' % fname)
                data = urlopen('%s/%s/%s' % (url, dataset, fname)).read()
                if not isdir(dirname(fpath)):
                    os.makedirs(dirname(fpath))
                open(fpath, 'w').write(data)
                vlog('done)\n')
                filesUpdated += 1
        except Exception as e:
            print '\nError while updating %s: %s' % (fname, e)
            taintedMANIFEST = True  # if we don't update, it can be wrong

    print '...done. Updated files: %d' % filesUpdated

    # Save the new MANIFEST file in the folder of the downloaded dataset
    if filesUpdated > 0:
        open(join(datasetFolder, 'MANIFEST'), 'w').write(manifestRaw)

    if taintedMANIFEST:
        print 'Some files could not be updated. Regenerating local MANIFEST ...'
        createMANIFEST(datasetFolder)


def upload(dataset, delete=False):
    """ Upload a dataset to our repository """

    localFolder = join(os.environ['SCIPION_TESTS'], dataset)
    remoteLoc = 'scipion@ramanujan.cnb.csic.es'
    remoteFolder = '/home/twiki/public_html/files/scipion/data/tests'

    if not exists(localFolder):
        sys.exit('ERROR: local folder %s does not exist.' % localFolder)

    print 'Warning: Uploading, please BE CAREFUL! This can be dangerous.'
    print ('You are going to be connected to "%s" to write in folder '
           '"%s" the dataset "%s".' % (remoteLoc, remoteFolder, dataset))
    if ask() == 'n':
        return

    # First make sure we have our MANIFEST file up-to-date
    print 'Updating local MANIFEST file with MD5 info...'
    createMANIFEST(localFolder)

    # Upload the dataset files (with rsync)
    print 'Uploading files...'
    call(['rsync', '-av', localFolder, '%s:%s' % (remoteLoc, remoteFolder)] +
         (['--delete'] if delete else []))

    # Regenerate remote MANIFEST (which contains a list of datasets)
    print 'Regenerating remote MANIFEST file...'
    call(['ssh', remoteLoc,
          'cd %s && find -type d -mindepth 1 -maxdepth 1 > MANIFEST' % remoteFolder])
    # This is a file that just contains the name of the directories
    # in remoteFolder. Nothing to do with the MANIFEST files in
    # the datasets, which contain file names and md5s.

    # Leave a register (log file)
    print 'Logging modification attempt in modifications.log ...'
    log = """++++
Modification to %s dataset made at
%s
by %s at %s
----""" % (dataset, time.asctime(), getpass.getuser(), ' '.join(os.uname()))
    call(['ssh', remoteLoc,
          'echo "%s" >> %s' % (log, join(remoteFolder, 'modifications.log'))])
    print "...done."


def createMANIFEST(path):
    """ Create a MANIFEST file in path with the md5 of all files below """

    with open(join(path, 'MANIFEST'), 'w') as manifest:
        for root, dirs, files in os.walk(path):
            for filename in files:
                if filename != 'MANIFEST':  # do not include ourselves
                    fn = join(root, filename)  # file to check
                    manifest.write('%s %s\n' % (relpath(fn, path), md5sum(fn)))


def md5sum(fname):
    """ Return the md5 hash of file fname """

    mhash = hashlib.md5()
    with open(fname) as f:
        for chunk in iter(lambda: f.read(128 * mhash.block_size), ''):
            mhash.update(chunk)
    return mhash.hexdigest()


def ask(question='Continue? (y/n): ', allowed=None):
    """ Ask the question until it returns one of the allowed responses """

    while True:
        ans = raw_input(question)
        if ans.lower() in (allowed if allowed else ['y', 'n']):
            return ans



if __name__ == "__main__":
    main()

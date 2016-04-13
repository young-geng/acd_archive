#!/usr/bin/env python
import subprocess
import os.path
import tempfile
import shutil
import sys
import signal
import datetime
import re
import argparse


TEMP_FOLDER = '/temp/acd_archive'
ARCHIVE_HOME = '/AutoArchive'



class TempDir(object):

    def __init__(self):
        self._dir = tempfile.mkdtemp()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.clean_up()

    def __del__(self):
        self.clean_up()


    def clean_up(self):
        if self._dir != None:
            shutil.rmtree(self._dir, ignore_errors=True)
            self._dir = None

    @property
    def path(self):
        return self._dir


def SigKillHandler(signum, frame):
    print 'Archive process interrupted with signal {}'.format(signum)
    raise Exception('interrupted')


def GenerateZipFileName(dir_name, name):
    filename = name + datetime.datetime.now().strftime('.%Y_%m_%d__%H_%M_%S.7z')
    return os.path.join(dir_name, filename)


def ZipFile(input_path, output_path):
    args = ['7za', 'a', '-mmt', '-mx9', '-t7z', output_path, input_path]
    if subprocess.call(args) != 0:
        raise Exception('Cannot create 7zip archive')


def AcdSync():
    args = ['acdcli', 'sync']
    if subprocess.call(args, stdout=subprocess.PIPE) != 0:
        raise Exception('Cannot sync with Amazon cloud drive')


def UploadFile(path, dest_path):
    args = ['acdcli', 'upload', path, dest_path]
    if subprocess.call(args, shell=False) != 0:
        raise Exception('Cannot upload file')


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Process some integers.')

    parser.add_argument('path', metavar='path', type=str,
                       help='file path to archive')
    parser.add_argument('--name', type=str, help='prefix name for archived file')
    parser.add_argument('--dest', type=str, default=ARCHIVE_HOME, help='destination dir')

    args = parser.parse_args()

    signal.signal(signal.SIGINT, SigKillHandler)

    input_path = args.path

    if args.name:
        name = args.name
    else:
        name = re.findall('/*([^/]+)/*$', input_path)[0]

    AcdSync()

    with TempDir() as temp_dir:
        output_path = GenerateZipFileName(temp_dir.path, name)
        ZipFile(input_path, output_path)
        UploadFile(output_path, args.dest)
















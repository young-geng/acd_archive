#!/usr/bin/env python
import subprocess
import os.path
import tempfile
import shutil
import sys
import signal
import datetime
import re


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
    args = ['7za', 'a', '-t7z', output_path, input_path]
    if subprocess.call(args, stdout=subprocess.PIPE) != 0:
        raise Exception('Cannot create 7zip archive')


def AcdSync():
    args = ['acdcli', 'sync']
    if subprocess.call(args, stdout=subprocess.PIPE) != 0:
        raise Exception('Cannot sync with Amazon cloud drive')


def UploadFile(path):
    args = ['acdcli', 'upload', path, ARCHIVE_HOME]
    if subprocess.call(args, shell=False) != 0:
        raise Exception('Cannot upload file')


if __name__ == '__main__':
    if len(sys.argv) != 2 and len(sys.argv) != 3:
        print 'Invalid argument!'
        print 'Usage: python acd_archive.py input_file [output_name]'
        sys.exit(1)

    signal.signal(signal.SIGINT, SigKillHandler)

    input_path = sys.argv[1]

    if len(sys.argv) == 3:
        name = sys.argv[2]
    else:
        name = re.findall('/*([^/]+)/*$', input_path)[0]

    AcdSync()

    with TempDir() as temp_dir:
        output_path = GenerateZipFileName(temp_dir.path, name)
        ZipFile(input_path, output_path)
        UploadFile(output_path)
















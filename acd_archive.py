#!/usr/bin/env python
import subprocess
import os.path
import tempfile
import shutil
import sys
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



def GenerateZipFileName(dir_name, name, no_prefix=False):
    if no_prefix:
        filename = name + '.7z'
    else:
        filename = name + datetime.datetime.now().strftime('.%Y_%m_%d__%H_%M_%S.7z')
    return os.path.join(dir_name, filename)


def ZipFile(input_path, output_path):
    args = ['7za', 'a', '-m0=lzma2', '-mmt=4', '-mx9', '-t7z', output_path, input_path]
    if subprocess.call(args) != 0:
        raise Exception('Cannot create 7zip archive')


def AcdSync():
    args = ['acdcli', 'sync']
    if subprocess.call(args, stdout=subprocess.PIPE) != 0:
        raise Exception('Cannot sync with Amazon cloud drive')


def UploadFile(path, dest_path, n_retry=5):
    args = ['acdcli', 'upload', path, dest_path]
    for _ in xrange(n_retry):
        if subprocess.call(args, shell=False) == 0:
            return
    raise Exception('Cannot upload file')


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Process some integers.')

    parser.add_argument('path', metavar='path', type=str,
                       help='file path to archive')
    parser.add_argument('--name', type=str, help='prefix name for archived file')
    parser.add_argument('--dest', type=str, default=ARCHIVE_HOME, help='destination dir')
    parser.add_argument('--retry', type=int, default=5, help='number of times to retry uploading')
    parser.add_argument('--no_prefix', action='store_true',
                        help='disable auto prefix for archive name')

    args = parser.parse_args()


    input_path = args.path

    if args.name:
        name = args.name
    else:
        name = re.findall('/*([^/]+)/*$', input_path)[0]

    AcdSync()

    with TempDir() as temp_dir:
        try:
            output_path = GenerateZipFileName(temp_dir.path, name, args.no_prefix)
            ZipFile(input_path, output_path)
            UploadFile(output_path, args.dest, args.retry)
        except:
            # We need to clean up the temp dir in case of any exceptions.
            pass
















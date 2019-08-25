# -*- coding: UTF-8 -*-
# !/user/bin/python3
# +++++++++++++++++++++++++++++++++++++++++++++++++++
# @File Name: download_demo.py
# @Author: Jiang.QY
# @Mail: qyjiang24@gmail.com
# @Date: 19-8-22
# +++++++++++++++++++++++++++++++++++++++++++++++++++
import os
import argparse
import time
import shutil
import warnings
import requests
import hashlib

import multiprocessing as mp

parser = argparse.ArgumentParser()

parser.add_argument('--dst-path', type=str, required=True, help='destination to store videos')
parser.add_argument('--urls-path', type=str, required=True, help='path to urls file')
parser.add_argument('--num-procs', type=int, default=10, help='number of process')
parser.add_argument('--num-retries', type=int, default=3, help='number of retries')
parser.add_argument('--checksum-path', type=str, help='path to checksum files')
parser.add_argument('--verbose', action='store_true', default=False)
args = parser.parse_args()

failed_log = mp.Manager()
failed_log = failed_log.list()

check_failed_log = mp.Manager()
check_failed_log = check_failed_log.list()


def check_integrity(videopath, md5):
    if not os.path.isfile(videopath):
        return False
    md5o = hashlib.md5()
    with open(videopath, 'rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            md5o.update(chunk)
    md5c = md5o.hexdigest()
    if md5c != md5:
        return False
    return True


def worker(idx, mpq):
    while True:
        line = mpq.get()
        if line is None:
            mpq.put(None)
            break
        try:
            index, video, url, checksum = line[0], line[1], line[2], line[3]
            videopath = os.path.join(args.dst_path, video)
            if os.path.exists(videopath):
                if args.verbose or index % 10000 == 0:
                    print('{:6d} video: {} is downloaded already.'.format(index, video))
                continue
            start_t = time.time()
            succ = False
            failed_cnt = 0
            for ind in range(args.num_retries):
                try:
                    r = requests.get(url)
                    with open(videopath, 'wb') as fp:
                        fp.write(r.content)
                except Exception as e:
                    failed_cnt += 1
                if checksum is not None:
                    succ = check_integrity(videopath, checksum)
                    if not succ:
                        check_failed_log.append(video)
                    continue
                else:
                    succ = True
                    continue
            if failed_cnt == args.num_retries:
                failed_log.append(video)
            end_t = time.time() - start_t
            if succ:
                if args.verbose or index % 10000 == 0:
                    print('{:6d} video: {} is downloaded successfully. Time: {:.3f}(s)'.format(index, video, end_t))
        except Exception as e:
            print('Exception: {}'.format(e))
    print('process: {} done'.format(idx))


def read_urls(filepath):
    urls = {}
    with open(filepath, 'r') as fp:
        for lines in fp:
            tmps = lines.strip().split(' ')
            urls[tmps[0]] = tmps[1]
    return urls


def read_checksum(filepath):
    checksums = {}
    with open(filepath, 'r') as fp:
        for lines in fp:
            tmps = lines.strip().split(' ')
            checksums[tmps[0]] = tmps[1]
    return checksums


if __name__ == "__main__":
    total, used, free = shutil.disk_usage(args.dst_path)
    print('#total space: {} GB'.format(total // (2**30)))
    print('#used space: {} GB'.format(used // (2**30)))
    print('#free space: {} GB'.format(free // (2**30)))
    if free < 500:
        warnings.warn('Warning: the SVD requires over 500 GB space to store videos.')
    mpq = mp.Queue()

    procs = []
    for idx in range(args.num_procs):
        p = mp.Process(target=worker, args=(idx, mpq))
        p.start()
        procs.append(p)

    urls = read_urls(args.urls_path)
    print('{} videos will be download.'.format(len(urls)))
    checksums = None
    if args.checksum_path is not None and os.path.exists(args.checksum_path):
        checksums = read_checksum(args.checksum_path)

    print('downloading starts...')
    for idx, video in enumerate(urls):
        checksum = checksums[video] if checksums is not None else None
        mpq.put([idx, video, urls[video], checksum])
    mpq.put(None)

    for idx, p in enumerate(procs):
        p.join()
        print('process: {} done'.format(idx))

    print('downloading ends...')
    failed_log = list(failed_log)
    if len(failed_log) > 0:
        with open('log/failed-log.log', 'w') as fp:
            for lines in failed_log:
                fp.write(lines + '\n')
        print('failed videos are store in log/failed-log.log')

    check_failed_log = list(check_failed_log)
    if len(check_failed_log) > 0:
        with open('log/check-failed-log.log', 'w') as fp:
            for lines in check_failed_log:
                fp.write(lines + '\n')
        print('checksum failed videos are store in log/check-failed-log.log')

    print('all done')

'''bash
python download_demo.py --dst-path /data1/jiangqy/dataset/svd/videos --urls-path data/urls
'''



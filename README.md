# SVD-download
### 0. About the paper
This repo is the source code for download the original videos in the paper "SVD: A Large-Scale Short Video Dataset for Near-Duplicate Video Retrieval" on ICCV-2019. The authors are: [Qing-Yuan Jiang](http://lamda.nju.edu.cn/jiangqy) , Yi He, Gen Li, Jian Li, Lei Li and [Wu-Jun Li](http://cs.nju.edu.cn/lwj). If you have any questions about the source code, please contact: jiangqy#lamda.nju.edu.cn or heyi#bytedance.com.

### 1. Usage
```bash
python download_demo.py --help
usage: download_demo.py [-h] --dst-path DST_PATH --urls-path URLS_PATH
                        [--num-procs NUM_PROCS] [--num-retries NUM_RETRIES]
                        [--checksum-path CHECKSUM_PATH] [--verbose]

optional arguments:
  -h, --help            show this help message and exit
  --dst-path DST_PATH   destination to store videos
  --urls-path URLS_PATH
                        path to urls file
  --num-procs NUM_PROCS
                        number of process
  --num-retries NUM_RETRIES
                        number of retries
  --checksum-path CHECKSUM_PATH
                        path to checksum files
  --verbose
```

#!/usr/bin/env python3
"""Add the existing Douglas vendor compatible to pinned upstream Goodix only."""
import argparse,hashlib
from pathlib import Path
SHA='03379465564da73d041e207c9cd83b2466085595a51f42682f87d64968a275dc'


def apply(root):
    p=root/'drivers/input/touchscreen/goodix.c';data=p.read_bytes()
    if hashlib.sha256(data).hexdigest()!=SHA:raise ValueError('Pinned ACK Goodix source required')
    before=b'\t{ .compatible = "goodix,gt911" },'
    if data.count(before)!=1:raise ValueError('Unique Goodix compatible table required')
    p.write_bytes(data.replace(before,b'\t{ .compatible = "goodix,gt9xx" },\n'+before))
    return {'compatible_alias_added':True,'driver_algorithm_changed':False,'device_enabled':False}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path)
    print(apply(p.parse_args().source))

#!/usr/bin/env python3
"""Translate the exact working TPV command function, preserving DSI packet types."""
import argparse
import hashlib
import json
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'evidence/display-pipeline-source/working-panel.c'
OUTPUT=ROOT/'projects/firetabs-android/kernel/display-port/panel/douglas_tpv_sequence.h'


def function(text):
    start=text.index('static void init_douglas_tpv_lcm(void)')
    start=text.index('{',start)+1
    return text[start:text.index('\n}',start)]


def translate(body):
    body=re.sub(r'/\*.*?\*/|//[^\n]*','',body,flags=re.S)
    declaration=re.match(r'\s*unsigned int data_array\[64\];',body)
    if not declaration:
        raise ValueError('Unexpected TPV declaration')
    at=declaration.end();words={};steps=[]
    expression=re.compile(r'\s*(?:data_array\[(\d+)\]\s*=\s*(0x[0-9a-fA-F]+|[0-9]+);|dsi_set_cmdq\(data_array,\s*(\d+),\s*1\);|MDELAY\((\d+)\);)')
    while body[at:].strip():
        match=expression.match(body,at)
        if not match:
            raise ValueError('Unreviewed TPV source statement')
        at=match.end()
        if match[1] is not None:
            index=int(match[1]);value=int(match[2],0)
            if index>=64 or not 0<=value<=0xffffffff:
                raise ValueError('Invalid legacy queue assignment')
            words[index]=value
        elif match[4] is not None:
            delay=int(match[4])
            if not 0<delay<=500:
                raise ValueError('Unbounded panel delay')
            steps.append((0,delay,b''))
        else:
            count=int(match[3])
            if not 0<count<=63 or any(i not in words for i in range(count)):
                raise ValueError('Uninitialized or oversized command queue')
            header=words[0];kind=header&65535
            if kind==0x1500 and count==1:
                packet_type=0x15;data=bytes([(header>>16)&255,header>>24])
            elif kind==0x0500 and count==1 and header>>24==0:
                packet_type=0x05;data=bytes([(header>>16)&255])
            elif kind==0x3902:
                size=header>>16
                if not 1<=size<=248 or count!=1+(size+3)//4:
                    raise ValueError('Invalid long packet extent')
                packet_type=0x39;data=b''.join(words[i].to_bytes(4,'little') for i in range(1,count))[:size]
            else:
                raise ValueError('Unreviewed legacy packet type')
            steps.append((packet_type,0,data))
    if not steps or len(steps)>512:
        raise ValueError('Bounded nonempty sequence required')
    return steps


def render(steps):
    rows=['/* SPDX-License-Identifier: GPL-2.0-only */',
          '/* Generated from the pinned working kernel TPV function. Do not hand edit. */',
          '#ifndef DOUGLAS_TPV_SEQUENCE_H','#define DOUGLAS_TPV_SEQUENCE_H',
          'struct douglas_tpv_command { unsigned char type, length; unsigned short delay_ms; unsigned char data[32]; };',
          'static const struct douglas_tpv_command douglas_tpv_sequence[] = {']
    for kind,delay,data in steps:
        if len(data)>32:
            raise ValueError('Panel command exceeds reviewed table capacity')
        rows.append(' {0x%02x,%d,%d,{%s}},'%(kind,len(data),delay,','.join('0x%02x'%v for v in data) if data else '0'))
    rows+=['};','#endif','']
    return '\n'.join(rows)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args()
    steps=translate(function(SOURCE.read_text()));content=render(steps)
    if args.check:
        if OUTPUT.read_text()!=content:raise ValueError('Panel sequence drift')
    else:OUTPUT.write_text(content)
    print(json.dumps({'scope':'Offline exact TPV packet translation; no hardware commands',
                      'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                      'steps':len(steps),'commands':sum(bool(x[0]) for x in steps),
                      'delay_ms':sum(x[1] for x in steps),'generated_sha256':hashlib.sha256(content.encode()).hexdigest()}))

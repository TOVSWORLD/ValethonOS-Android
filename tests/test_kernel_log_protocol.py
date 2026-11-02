from pathlib import Path
import io
import fcntl
import os
import pty
import struct
import subprocess
import sys
import tempfile
import termios
import time
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import kernel_log_protocol as protocol

NONCE = bytes(range(32))


def wire(records):
    return protocol.MAGIC + NONCE + b''.join(
        struct.pack('>II', i, len(record)) + record for i, record in enumerate(records)
    ) + struct.pack('>II', len(records), 0)


class KernelLogProtocol(unittest.TestCase):
    def receive(self, data, split=1):
        incoming = io.BytesIO(data)
        acknowledgments = []
        with tempfile.TemporaryFile() as raw:
            result = protocol.receive(lambda n: incoming.read(min(n, split)),
                                      acknowledgments.append, raw.fileno(), NONCE,
                                      time.monotonic() + 10)
            raw.seek(0)
            return result, raw.read(), acknowledgments

    def test_split_binary_records_are_exact_and_durable_before_ack(self):
        encoded = wire([b'6,1,0,-;kernel start\n', bytes(range(256))])
        calls = []
        original_sync = os.fsync
        def sync(fd):
            calls.append('sync')
            original_sync(fd)
        with patch.object(protocol.os, 'fsync', sync):
            stream = io.BytesIO(encoded)
            with tempfile.TemporaryFile() as raw:
                result = protocol.receive(stream.read, lambda data: calls.append(data), raw.fileno(),
                                          NONCE, time.monotonic() + 10)
                raw.seek(0)
                self.assertEqual(raw.read(), encoded)
        self.assertEqual(calls[:2], ['sync', protocol.ACK + NONCE])
        self.assertTrue(result['complete'])
        self.assertEqual(result['records'], 2)
        result, captured, ack = self.receive(encoded)
        self.assertEqual(captured, encoded)
        self.assertEqual(ack, [protocol.ACK + NONCE])

    def test_wrong_identity_never_acknowledged(self):
        incoming = io.BytesIO(protocol.MAGIC + bytes(32))
        ack = []
        with tempfile.TemporaryFile() as raw, self.assertRaises(ValueError):
            protocol.receive(incoming.read, ack.append, raw.fileno(), NONCE, time.monotonic() + 10)
        self.assertEqual(ack, [])

    def test_truncation_bad_sequence_and_oversize_do_not_complete(self):
        for data in [wire([b'one'])[:-1], protocol.MAGIC + NONCE + struct.pack('>II', 1, 0),
                     protocol.MAGIC + NONCE + struct.pack('>II', 0, protocol.MAX_RECORD + 1)]:
            with self.subTest(data=data[-8:]), self.assertRaises(ValueError):
                self.receive(data)

    def test_deadline_and_sync_failure_never_acknowledge(self):
        for expired in [True, False]:
            ack = []
            data = io.BytesIO(wire([]))
            with tempfile.TemporaryFile() as raw, self.assertRaises((ValueError, OSError)):
                with patch.object(protocol.os, 'fsync', side_effect=OSError('disk full')):
                    protocol.receive(data.read, ack.append, raw.fileno(), NONCE,
                                     time.monotonic() - 1 if expired else time.monotonic() + 10)
            self.assertEqual(ack, [])

    def test_actual_nonblocking_pty_adapter_without_device_access(self):
        master, slave = pty.openpty()
        try:
            attributes = termios.tcgetattr(slave)
            attributes[:4] = [0, 0, termios.CS8 | termios.CREAD | termios.CLOCAL, 0]
            attributes[4:6] = [termios.B9600, termios.B9600]
            termios.tcsetattr(slave, termios.TCSANOW, attributes)
            fcntl.fcntl(slave, fcntl.F_SETFL, fcntl.fcntl(slave, fcntl.F_GETFL) | os.O_NONBLOCK)
            encoded = wire([bytes(range(256))])
            self.assertEqual(os.write(master, encoded), len(encoded))
            with tempfile.TemporaryFile() as raw:
                result = protocol.receive_fd(slave, raw.fileno(), NONCE, time.monotonic() + 5)
                raw.seek(0)
                self.assertEqual(raw.read(), encoded)
            self.assertTrue(result['complete'])
            self.assertEqual(os.read(master, 40), protocol.ACK + NONCE)
            # Empty input must expire rather than block on a TTY read.
            with tempfile.TemporaryFile() as raw, self.assertRaises(ValueError):
                protocol.receive_fd(slave, raw.fileno(), NONCE, time.monotonic() + .01)
        finally:
            os.close(master)
            os.close(slave)

    def test_real_c_producer_interoperates_with_durable_receiver(self):
        source = r'''
#include <stdio.h>
#include <string.h>
#include "kernel_log_stream.h"
static int reads;
static long read_log(void *ctx,unsigned char *out,unsigned long cap) {
 (void)ctx;(void)cap;
 if(reads++==0){const char record[]="6,1,0,-;kernel start\n";memcpy(out,record,sizeof(record)-1);return sizeof(record)-1;}
 return 0;
}
static int send_all(void *ctx,const unsigned char *p,unsigned long n) {
 (void)ctx;return fwrite(p,1,n,stdout)==n&&fflush(stdout)==0?0:-1;
}
static int ack(void *ctx,unsigned char *p,unsigned long n) {
 (void)ctx;return fread(p,1,n,stdin)==n?0:-1;
}
static int deadline(void *ctx){(void)ctx;return 1;}
int main(void){unsigned char nonce[32];for(int i=0;i<32;i++)nonce[i]=(unsigned char)i;
 struct vl_io io={read_log,send_all,ack,deadline,0};return vl_stream(&io,nonce)?1:0;}
'''
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            (folder / 'producer.c').write_text(source)
            subprocess.run(['cc', '-std=c11', '-Wall', '-Wextra', '-Werror',
                            '-fsanitize=address,undefined', '-I', str(ROOT / 'projects/firetabs-android/diagnostic-usb'),
                            str(folder / 'producer.c'), '-o', str(folder / 'producer')], check=True)
            process = subprocess.Popen([str(folder / 'producer')], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
            try:
                with tempfile.TemporaryFile() as raw:
                    def acknowledge(data):
                        process.stdin.write(data)
                        process.stdin.flush()
                    result = protocol.receive(lambda n: os.read(process.stdout.fileno(), n),
                                              acknowledge, raw.fileno(), NONCE, time.monotonic() + 10)
                    raw.seek(0)
                    self.assertEqual(raw.read(), wire([b'6,1,0,-;kernel start\n']))
                self.assertEqual(process.wait(timeout=10), 0)
                self.assertEqual(result['records'], 1)
            finally:
                if process.poll() is None:
                    process.kill()
                    process.wait()
                for stream in [process.stdin, process.stdout, process.stderr]:
                    stream.close()


if __name__ == '__main__':
    unittest.main()

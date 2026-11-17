import os
import struct
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from inspect_ack_native_capture import inspect
from kernel_log_protocol import MAGIC
from capture_lab_kernel_log import capture
from prepare_ack_native_bundle import RELEASE, bootargs, reserve_union, reservation_map

NONCE = b'N' * 32


def wire(release=RELEASE, nonce=NONCE, terminal=True, facility=6, cmdline=True):
    records = [(str(facility) + ',0,1,-;Linux version ' + release + ' build\n').encode()]
    if cmdline:
        records.append(b'6,1,2,-;Kernel command line: valethon.native_trial=' + nonce.hex().encode() + b'\n')
    data = MAGIC + nonce + b''.join(struct.pack('>II', i, len(b)) + b for i, b in enumerate(records))
    return data + (struct.pack('>II', len(records), 0) if terminal else b'')


class WireProof(unittest.TestCase):
    def test_complete_and_interrupted_stream_prove_exact_kernel_and_pid1(self):
        for terminal in [True, False]:
            r = inspect(wire(terminal=terminal), NONCE, RELEASE)
            self.assertTrue(r['target_pid1_proven'])
            self.assertEqual(r['terminal_frame'], terminal)

    def test_header_or_handoff_marker_alone_does_not_prove_linux(self):
        for data in [b'', MAGIC + NONCE, b'FIRETABS_ACK_HANDOFF_V1 nonce=anything\n']:
            if len(data) >= 40 and not data.startswith(MAGIC):
                with self.assertRaises(ValueError): inspect(data, NONCE, RELEASE)
            else:
                self.assertFalse(inspect(data, NONCE, RELEASE)['target_kernel_boot_proven'])

    def test_wrong_release_or_nonce_refused(self):
        for data in [wire(release='4.9.337'), wire(nonce=b'X' * 32)]:
            with self.assertRaises(ValueError): inspect(data, NONCE, RELEASE)

    def test_userspace_echo_is_not_a_kernel_boot_record(self):
        self.assertFalse(inspect(wire(facility=14), NONCE, RELEASE)['target_kernel_boot_proven'])

    def test_missing_cmdline_identity_is_not_full_boot_proof(self):
        self.assertFalse(inspect(wire(cmdline=False), NONCE, RELEASE)['target_pid1_proven'])

    def test_truncated_last_frame_preserves_completed_record_evidence(self):
        data = wire(terminal=False) + struct.pack('>II', 2, 100) + b'partial'
        r = inspect(data, NONCE, RELEASE)
        self.assertTrue(r['target_pid1_proven']); self.assertFalse(r['terminal_frame'])
        self.assertGreater(r['interrupted_tail_bytes'], 0)

    def test_out_of_sequence_or_trailing_data_refused(self):
        data = bytearray(wire()); struct.pack_into('>I', data, 40, 5)
        for b in [bytes(data), wire() + b'extra']:
            with self.assertRaises(ValueError): inspect(b, NONCE, RELEASE)


class ReadyAndMemory(unittest.TestCase):
    def test_receiver_ready_only_after_private_capture_files_exist(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'capture'
            observed = []
            def ready():
                p = out / 'raw.bin'
                observed.append(p.exists() and p.stat().st_mode & 0o777 == 0o600)
            r = capture({'wait_seconds': 0}, NONCE, out, ready=ready)
            self.assertEqual(observed, [True]); self.assertFalse(r['complete'])

    def test_reservation_union_preserves_fdt_payload_and_updates_offsets(self):
        # Valid structural extents; property parsing is independently exercised
        # by fdtget readback of the real prepared board package.
        header = struct.pack('>10I', 0xd00dfeed, 68, 56, 64, 40, 17, 16, 0, 4, 8)
        data = header + bytes(16) + b'ABCDEFGH' + b'name'
        new, ranges = reserve_union(data, [(100, 200), (150, 300), (400, 500)])
        self.assertEqual(ranges, [(100, 300), (400, 500)])
        h = struct.unpack_from('>10I', new)
        self.assertEqual(new[h[2]:h[2] + 8], b'ABCDEFGH')
        self.assertEqual(new[h[3]:h[3] + 4], b'name')
        self.assertEqual(reservation_map(new)[2], ranges)

    def test_target_bootargs_pin_console_geometry_and_exclude_disk_log_optin(self):
        args = bootargs(NONCE.hex())
        for s in ['ramoops.mem_address=0x444bf000', 'ramoops.mem_size=0x10000',
                  'ramoops.record_size=0', 'ramoops.ftrace_size=0', 'nr_cpus=1']:
            self.assertIn(s, args)
        self.assertNotIn('valethon,trial-nonce', args)
        with self.assertRaises(ValueError): bootargs('not a nonce')


if __name__ == '__main__':
    unittest.main()

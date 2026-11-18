import ctypes
import errno
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class Result(ctypes.Structure):
    _fields_ = [('error', ctypes.c_int)] + [(n, ctypes.c_uint) for n in
        ['phase', 'steps', 'writes', 'off', 'reads', 'fw', 'locks', 'unlocks', 'held']] + [
        ('log_reg', ctypes.c_uint * 32), ('log_value', ctypes.c_uint * 32)]


class SecondaryOff(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cc = shutil.which('cc')
        if not cc: raise unittest.SkipTest('C compiler required')
        cls.temp = tempfile.TemporaryDirectory()
        lib = Path(cls.temp.name)/'off.so'
        subprocess.run([cc, '-dynamiclib' if sys.platform == 'darwin' else '-shared',
                        '-fPIC', '-std=c99', '-Wall', '-Wextra', '-Werror',
                        '-I', str(ROOT/'projects/firetabs-android/kexec-stage'),
                        str(ROOT/'tests/kexec_cpu_off_harness.c'), '-o', str(lib)],
                       check=True, capture_output=True)
        cls.lib = ctypes.CDLL(str(lib))
        cls.lib.run.argtypes = [ctypes.c_uint]*4 + [ctypes.c_ulonglong, ctypes.POINTER(Result)]
        cls.lib.gate.argtypes = [ctypes.c_uint]*5 + [ctypes.POINTER(Result)]

    @classmethod
    def tearDownClass(cls): cls.temp.cleanup()

    def run_case(self, cpu=1, mode=0, fail_at=0, limit=80, timeout=100000):
        r = Result(); self.lib.run(cpu, mode, fail_at, limit, timeout, ctypes.byref(r))
        self.assertLessEqual(r.steps, limit)
        self.assertEqual(r.held, 0)
        if r.error: self.assertFalse(r.off)
        return r

    def test_exact_vendor_power_down_writes_for_all_secondaries(self):
        for cpu, con, l1 in [(1,0x218,0x264),(2,0x21c,0x26c),(3,0x220,0x274)]:
            r = self.run_case(cpu)
            self.assertEqual((r.error, r.off, r.phase, r.unlocks), (0,1,8,1))
            self.assertEqual(list(r.log_reg)[:r.writes], [0,con,con,con,l1,con,con,con,con])
            self.assertEqual(list(r.log_value)[:r.writes],
                             [0x0b160001,0x8000004f,0x8000006f,0x8000002f,1,
                              0x8000002e,0x8000003e,0x8000003a,0x80000032])

    def test_invalid_cpu_or_missing_firmware_backend_never_touches_io(self):
        for cpu, mode in [(0,0),(4,0),(0xffffffff,0),(1,13)]:
            r = self.run_case(cpu,mode)
            self.assertEqual(r.error,-errno.EINVAL)
            self.assertEqual((r.reads,r.writes,r.fw,r.locks), (0,0,0,0))

    def test_firmware_errors_propagate_without_register_access(self):
        for mode, error in [(2,errno.EOPNOTSUPP),(12,errno.EIO)]:
            r=self.run_case(mode=mode)
            self.assertEqual(r.error,-error)
            self.assertEqual((r.reads,r.writes,r.locks), (0,0,0))

    def test_frozen_clock_cannot_extend_firmware_wfi_or_lock_waits(self):
        for mode, phase in [(1,1),(3,2),(4,3)]:
            r=self.run_case(mode=mode,limit=32)
            self.assertEqual((r.error,r.steps,r.phase),(-errno.ETIMEDOUT,32,phase))
            self.assertEqual(r.writes,0)

    def test_wfi_lost_while_waiting_for_lock_aborts_before_writes(self):
        r=self.run_case(mode=9)
        self.assertEqual((r.error,r.writes,r.unlocks),(-errno.EBUSY,0,1))

    def test_sram_timeout_does_not_attempt_reset_or_power_cut(self):
        r=self.run_case(mode=5)
        self.assertEqual((r.error,r.phase,r.writes,r.unlocks),(-errno.ETIMEDOUT,6,5,1))

    def test_both_power_status_registers_must_agree_off(self):
        for mode in [6,10]:
            r=self.run_case(mode=mode)
            self.assertEqual((r.error,r.phase,r.writes,r.unlocks),(-errno.ETIMEDOUT,7,9,1))
        self.assertEqual(self.run_case(mode=11).error,0)

    def test_every_read_write_failure_aborts_and_releases_owned_lock(self):
        good=self.run_case()
        count=good.reads+good.writes
        for fail in range(1,count+1):
            r=self.run_case(fail_at=fail)
            self.assertEqual(r.error,-errno.EIO,fail)
            self.assertLessEqual(r.reads+r.writes,fail)
            self.assertEqual(r.unlocks,1 if fail>1 else 0)

    def test_deadline_or_clock_regression_aborts(self):
        for mode, timeout in [(7,2500),(8,100000)]:
            r=self.run_case(mode=mode,timeout=timeout)
            self.assertEqual(r.error,-errno.ETIMEDOUT)
            self.assertEqual(r.writes,0)

    def test_zero_budgets_rejected_without_io(self):
        for limit,timeout in [(0,100),(100,0)]:
            r=self.run_case(limit=limit,timeout=timeout)
            self.assertEqual(r.error,-errno.EINVAL)
            self.assertEqual(r.reads+r.writes,0)

    def test_step_budget_exhaustion_at_every_success_boundary_never_passes(self):
        good=self.run_case()
        for limit in range(1,good.steps):
            r=self.run_case(limit=limit)
            self.assertEqual(r.error,-errno.ETIMEDOUT)

    def gate_case(self, mode=0, possible=15, online=1, failures=0, fail_at=0):
        r=Result();self.lib.gate(mode,possible,online,failures,fail_at,ctypes.byref(r))
        self.assertEqual(r.writes,0)
        self.assertEqual(r.held,0)
        return r

    def test_final_gate_requires_exact_topology_and_survivor(self):
        for possible,online in [(7,1),(15,2),(15,3),(31,1),(15,0)]:
            r=self.gate_case(possible=possible,online=online)
            self.assertEqual((r.error,r.reads,r.fw),(-errno.EINVAL,0,0))

    def test_final_gate_requires_all_three_firmware_states_and_two_power_banks(self):
        good=self.gate_case()
        self.assertEqual((good.error,good.off,good.fw,good.reads,good.unlocks),(0,1,3,2,1))
        for mode in [6,10,14]:
            r=self.gate_case(mode=mode)
            self.assertNotEqual(r.error,0)
            self.assertFalse(r.off)

    def test_final_gate_sticky_errors_cannot_be_overridden_by_off_hardware(self):
        for failures in [1,2,4,8,0xffffffff]:
            r=self.gate_case(failures=failures)
            self.assertEqual((r.error,r.reads,r.fw),(-errno.EIO,0,0))

    def test_final_gate_read_errors_and_frozen_lock_release_without_pass(self):
        for fail_at in [1,2]:
            r=self.gate_case(fail_at=fail_at)
            self.assertEqual((r.error,r.off,r.unlocks),(-errno.EIO,0,1))
        r=self.gate_case(mode=4)
        self.assertEqual((r.error,r.steps,r.unlocks),(-errno.ETIMEDOUT,32,0))


if __name__=='__main__': unittest.main()

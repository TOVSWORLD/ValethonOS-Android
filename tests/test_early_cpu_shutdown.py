"""Execute the actual generated C sequence against hotplug/order controls."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from prepare_early_cpu_shutdown import NEW, prepare

HARNESS = r'''
#include <stdbool.h>
#include <setjmp.h>
#include <stdio.h>
#include <stdlib.h>
#define CONFIG_MACH_MT8163 1
#define KEXEC_TYPE_DEFAULT 0
static struct { int type; } image;
static typeof(image) *kexec_image = &image;
static void *current;
static int pid = 1, board = 1, error, off_error, gate_error;
static int online = 4, survivor, cpu0 = 1, frozen, kexec_in_progress;
static int events[16], n;
static jmp_buf fatal;
static void event(int value) { events[n++] = value; }
static int task_tgid_nr(void *unused) { (void)unused; return pid; }
static int of_machine_is_compatible(const char *unused) { (void)unused; return board; }
static void migrate_to_reboot_cpu(void) { frozen++; event(1); }
static void cpu_hotplug_enable(void) { if (--frozen != 0) abort(); event(2); }
static int disable_nonboot_cpus(void) { frozen++; event(3); online = 1; return off_error; }
static int raw_smp_processor_id(void) { return survivor; }
static int num_online_cpus(void) { return online; }
static int cpu_online(int cpu) { return cpu == 0 && cpu0; }
static int mt_kexec_secondary_off_gate(void) { event(4); return gate_error; }
#define panic(...) longjmp(fatal, 1)
#define pr_emerg(...) ((void)0)
static void msleep(int ms) { if(ms != 1000) abort(); event(5); }
static void kernel_restart_prepare(void *unused) { (void)unused; event(6); }
static void machine_shutdown(void) { event(7); frozen++; }
static void sequence(void) {
__SEQUENCE__
 event(8); /* subsequent machine_kexec call, whose final gate is retained */
}
int main(int argc, char **argv) {
 int test = argc > 1 ? atoi(argv[1]) : 0;
 if (test == 1) pid = 2;
 if (test == 2) board = 0;
 if (test == 3) image.type = 1;
 if (test == 4) off_error = -5;
 if (test == 5) gate_error = -5;
 if (test == 6) survivor = 1;
 if (test == 7) cpu0 = 0;
 int failed = setjmp(fatal);
 if (!failed) sequence();
 printf("%d %d", failed, frozen);
 for (int i=0;i<n;i++) printf(" %d", events[i]);
 puts("");
 return 0;
}
'''


class EarlyCPUShutdown(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        root = Path(cls.tmp.name)
        source = root / 'control.c'
        source.write_text(HARNESS.replace('__SEQUENCE__', NEW))
        cls.binary = root / 'control'
        subprocess.run(['cc', '-std=gnu11', '-Wall', '-Wextra', '-Werror',
                        str(source), '-o', str(cls.binary)], check=True)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def result(self, case):
        return list(map(int, subprocess.check_output([str(self.binary), str(case)]).split()))

    def test_cpu_off_precedes_devices_and_hotplug_stays_frozen(self):
        self.assertEqual(self.result(0), [0, 1, 1, 2, 3, 4, 5, 6, 8])

    def test_other_routes_retain_original_order_and_balance(self):
        for case in [1, 2, 3]:
            with self.subTest(case=case):
                self.assertEqual(self.result(case), [0, 1, 6, 1, 2, 7, 8])

    def test_cpu_off_failure_cannot_shutdown_devices_or_jump(self):
        self.assertEqual(self.result(4), [1, 1, 1, 2, 3])

    def test_hardware_gate_failure_cannot_shutdown_devices_or_jump(self):
        self.assertEqual(self.result(5), [1, 1, 1, 2, 3, 4])

    def test_wrong_survivor_refuses(self):
        self.assertEqual(self.result(6), [1, 1, 1, 2, 3])

    def test_cpu0_offline_refuses(self):
        self.assertEqual(self.result(7), [1, 1, 1, 2, 3])

    def test_unknown_source_refused(self):
        with self.assertRaises(ValueError):
            prepare('unreviewed source')


if __name__ == '__main__':
    unittest.main()

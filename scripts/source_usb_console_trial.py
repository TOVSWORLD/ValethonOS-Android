"""Source-side USB console proof and capture for one bounded handoff trial."""
import hashlib,json,os,selectors,shlex,subprocess
from pathlib import Path
from capture_source_usb_console import marker

def digest(b):return hashlib.sha256(b).hexdigest()

class SourceCapture:
    def __init__(self,device,package,report,trial,physical,output):
        marker(trial) # Reject an unbound/nonhex token before any shell command.
        self.d=device;self.package=package;self.report=report;self.trial=trial
        self.physical=physical;self.output=output;self.process=None;self.folder=None
        self.remote=package+'/source-capture-'+trial
        self.helper_maybe_started=False
        self.ffs_hold_armed=False;self.saved_printk=None

    def arm_ffs_hold(self):
        base='/sys/module/usb_f_fs/parameters/'
        if self.d.shell('cat '+base+'ft_hold_adb').strip()!=b'N' or self.d.shell('cat '+base+'ft_hold_trial').strip():
            raise ValueError('FunctionFS hold is not in its unowned default state')
        levels=self.d.shell('cat /proc/sys/kernel/printk').split()
        if len(levels)!=4 or any(not value.isdigit() for value in levels):raise ValueError('Unreviewed printk state')
        self.saved_printk=' '.join(str(int(x)) for x in levels)
        # Mark ownership before either write so a partial arm is cleaned up.
        self.ffs_hold_armed=True
        self.d.shell('printf %s '+self.trial+' > '+base+'ft_hold_trial')
        self.d.shell('printf 1 > '+base+'ft_hold_adb')
        if self.d.shell('cat '+base+'ft_hold_adb').strip()!=b'Y' or self.d.shell('cat '+base+'ft_hold_trial').strip()!=self.trial.encode():
            raise ValueError('FunctionFS hold did not read back exactly')
        quiet='1 '+' '.join(str(int(x)) for x in levels[1:])
        self.d.shell('printf %s '+shlex.quote(quiet)+' > /proc/sys/kernel/printk')
        if self.d.shell('cat /proc/sys/kernel/printk').split()!=quiet.encode().split():raise ValueError('Quiet console did not read back')

    def restore_settings(self):
        if self.ffs_hold_armed:
            base='/sys/module/usb_f_fs/parameters/'
            if self.d.shell('cat '+base+'ft_hold_trial').strip() not in [b'',self.trial.encode()]:
                raise ValueError('FunctionFS hold ownership changed; refuse to overwrite')
            self.d.shell('printf 0 > '+base+'ft_hold_adb')
            self.d.shell("printf '\\n' > "+base+'ft_hold_trial')
            if self.d.shell('cat '+base+'ft_hold_adb').strip()!=b'N' or self.d.shell('cat '+base+'ft_hold_trial').strip():raise ValueError('FunctionFS hold not cleared on abort')
            self.ffs_hold_armed=False
        if self.saved_printk is not None:
            self.d.shell('printf %s '+shlex.quote(self.saved_printk)+' > /proc/sys/kernel/printk')
            if self.d.shell('cat /proc/sys/kernel/printk').split()!=self.saved_printk.encode().split():raise ValueError('Printk state not restored')
            self.saved_printk=None

    def line(self,expected,seconds):
        with selectors.DefaultSelector() as s:
            s.register(self.process.stdout,selectors.EVENT_READ)
            if not s.select(seconds) or self.process.stdout.readline()!=expected+b'\n':
                raise RuntimeError('Source console handshake failed: '+expected.decode())

    def start(self):
        for name,key in [('source-acm-hold','helper_sha256'),('capture_source_usb_console.py','receiver_sha256')]:
            if self.d.host(['sha256sum',self.package+'/'+name]).stdout.split()[0].decode()!=self.report[key]:
                raise ValueError('Source capture artifact differs')
        consoles=self.d.shell('cat /proc/consoles').splitlines()
        if not any(line.startswith(b'ttyGS0 ') and b'E' in line.split(b'(')[-1] for line in consoles):
            raise ValueError('Source ttyGS0 kernel console is not enabled')
        if self.report.get('functionfs_hold') is True:self.arm_ffs_hold()
        self.folder='/dev/kxusb-acm-'+self.trial
        self.d.shell('mkdir -m 700 '+self.folder)
        self.d.adb('push',self.package+'/source-acm-hold',self.folder+'/hold')
        self.d.shell('chmod 700 '+self.folder+'/hold')
        if self.d.shell('sha256sum '+self.folder+'/hold').split()[0].decode()!=self.report['helper_sha256']:
            raise ValueError('RAM helper differs')
        profile={'trial':self.trial,'physical_path':self.physical,'vendor':'1949','product':'0338'}
        code='import sys,pathlib,json;sys.path.insert(0,'+repr(self.package)+');from capture_source_usb_console import capture;print(json.dumps(capture('+repr(profile)+',pathlib.Path('+repr(self.remote)+'))))'
        self.process=subprocess.Popen(self.d.args+['python3 -c '+shlex.quote(code)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,bufsize=0)
        self.line(b'SOURCE_RECEIVER_READY',15)
        self.helper_maybe_started=True
        self.d.shell(self.folder+'/hold '+self.trial)
        self.line(b'SOURCE_USB_OPEN',30)
        self.d.adb('wait-for-device',timeout=30)
        payload=b'<0>'+marker(self.trial)+b'\n'
        self.d.shell('printf %s '+shlex.quote(payload.decode())+' > /dev/kmsg')
        self.line(b'SOURCE_CONSOLE_PROVEN',15)

    def intent(self):
        self.d.shell('umask 077; printf %s '+self.trial+' > '+self.folder+'/handoff-intent')
        # The helper acknowledges that it will perform no more configfs writes.
        # Require this acknowledgement before setting the jump-request counter.
        self.d.shell('i=0; while [ "$i" -lt 30 ]; do if grep -q handoff_intent_no_further_usb_writes '+self.folder+'/receipt; then exit 0; fi; i=$((i+1)); sleep 0.1; done; exit 1')

    def collect(self):
        if self.process is None:return {'source_console_proven':False}
        stdout,stderr=self.process.communicate(timeout=255)
        lines=stdout.splitlines()
        result=json.loads(lines[-1]) if lines else {'collector_receipt_missing':True}
        if result.get('capture_bytes',0) or result.get('collector_receipt_missing'):
            raw=self.d.host(['cat',self.remote+'/source-console-private.bin'],timeout=30).stdout
            if result.get('collector_receipt_missing'):
                expected=marker(self.trial);phases=raw.split(expected,1)[1] if expected in raw else b''
                result.update(capture_bytes=len(raw),capture_sha256=digest(raw),source_console_proven=expected in raw,
                              init_reboot_route_seen=b'KXHANDOFF init_reboot_route=1 kexec_requested=1' in phases,
                              native_entry_seen=b'KXHANDOFF native_entry=1 image_present=1' in phases,
                              starting_new_kernel_seen=b'Starting new kernel' in phases,
                              final_cpu_gate_seen=b'KXHANDOFF final_cpu_gate=passed survivor=0' in phases)
                result['ffs_last_close_retained']=('KXUSB_FFS trial='+self.trial+' adb_last_close=retained').encode() in phases
                # Obtain an independent host digest before accepting a salvaged copy.
                code='import hashlib,pathlib;print(hashlib.sha256(pathlib.Path('+repr(self.remote+'/source-console-private.bin')+').read_bytes()).hexdigest())'
                if self.d.host(['python3','-c',code],timeout=30).stdout.strip().decode()!=digest(raw):raise ValueError('Salvaged source capture copy differs')
            if digest(raw)!=result['capture_sha256']:raise ValueError('Source capture copy differs')
            with (self.output/'source-console-private.bin').open('xb') as f:
                os.fchmod(f.fileno(),0o600);f.write(raw);f.flush();os.fsync(f.fileno())
        return result

    def abort(self):
        # Before jump intent only, helper restores ADB-only at its fixed deadline.
        # Never force unbind an uncertain owner or issue commands after a jump.
        try:
            if self.folder and self.helper_maybe_started:
                self.d.adb('wait-for-device',timeout=195)
                self.d.shell('i=0; while [ "$i" -lt 190 ]; do if grep -q finished '+self.folder+'/receipt; then break; fi; i=$((i+1)); sleep 1; done; test ! -e /config/usb_gadget/g1/configs/b.1/f2; test "$(cat /config/usb_gadget/g1/UDC)" = musb-hdrc',timeout=195)
        finally:
            try:self.restore_settings()
            finally:
                if self.process and self.process.poll() is None:
                    self.process.terminate();self.process.communicate(timeout=10)

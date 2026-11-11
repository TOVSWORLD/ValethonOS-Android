"""Source-side USB console proof and capture for one bounded handoff trial."""
import hashlib,json,selectors,shlex,subprocess
from pathlib import Path
from capture_source_usb_console import marker

def digest(b):return hashlib.sha256(b).hexdigest()

class SourceCapture:
    def __init__(self,device,package,report,trial,physical,output):
        self.d=device;self.package=package;self.report=report;self.trial=trial
        self.physical=physical;self.output=output;self.process=None;self.folder=None
        self.remote=package+'/source-capture-'+trial
        self.helper_maybe_started=False

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
        result=json.loads(stdout.splitlines()[-1])
        if result.get('capture_bytes',0):
            raw=self.d.host(['cat',self.remote+'/source-console-private.bin'],timeout=30).stdout
            if digest(raw)!=result['capture_sha256']:raise ValueError('Source capture copy differs')
            f=self.output/'source-console-private.bin';f.write_bytes(raw);f.chmod(0o600)
        return result

    def abort(self):
        # Before jump intent only, helper restores ADB-only at its fixed deadline.
        # Never force unbind an uncertain owner or issue commands after a jump.
        if self.folder and self.helper_maybe_started:
            self.d.shell('i=0; while [ "$i" -lt 190 ]; do if grep -q finished '+self.folder+'/receipt; then break; fi; i=$((i+1)); sleep 1; done; test ! -e /config/usb_gadget/g1/configs/b.1/f2; test "$(cat /config/usb_gadget/g1/UDC)" = musb-hdrc',timeout=195)
        if self.process and self.process.poll() is None:
            self.process.terminate();self.process.communicate(timeout=10)

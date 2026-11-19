import struct,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from loader_fb_reservation import preserve


def fixture(names=('fb-reserved-memory@98600000',)):
    def node(name):
        b=name.encode()+b'\0';return struct.pack('>I',1)+b+bytes((-len(b))%4)
    reg=bytes.fromhex('00000000986000000000000001000000')
    body=node('')+node('reserved-memory')
    for name in names:
        body+=node(name)+struct.pack('>III',3,len(reg),0)+reg+struct.pack('>III',3,0,4)+struct.pack('>I',2)
    body+=struct.pack('>III',2,2,9);strings=b'reg\0no-map\0'
    reserve=struct.pack('>QQQQ',0x43000000,0x30000,0,0)
    start=40+len(reserve);total=start+len(body)+len(strings)
    return struct.pack('>10I',0xd00dfeed,total,start,start+len(body),40,17,16,0,len(strings),len(body))+reserve+body+strings


class LoaderFramebufferReservation(unittest.TestCase):
    def test_one_name_byte_changes_with_all_reservations_and_properties_retained(self):
        blob=fixture();fixed,report=preserve(blob)
        self.assertEqual(fixed,blob.replace(b'fb-reserved-memory@',b'fw-reserved-memory@'))
        self.assertEqual(sum(a!=b for a,b in zip(blob,fixed)),1)
        self.assertTrue(report['reservation_properties_unchanged'])
        self.assertEqual(fixed[:72],blob[:72])

    def test_unitless_loader_name_is_also_reserved(self):
        fixed,_=preserve(fixture(('fb-reserved-memory',)))
        self.assertIn(b'fw-reserved-memory\0',fixed)

    def test_ambiguous_or_absent_loader_owned_nodes_rejected(self):
        for names in [(),('other-memory@98600000',),('fb-reserved-memory','fb-reserved-memory@98600000')]:
            with self.assertRaises(ValueError):preserve(fixture(names))

    def test_truncated_or_invalid_structure_rejected(self):
        blob=fixture()
        for candidate in [blob[:39],blob[:-1],blob[:4]+bytes(4)+blob[8:],blob[:72]+struct.pack('>I',99)+blob[76:]]:
            with self.assertRaises(ValueError):preserve(candidate)

    def test_second_application_rejected(self):
        fixed,_=preserve(fixture())
        with self.assertRaises(ValueError):preserve(fixed)

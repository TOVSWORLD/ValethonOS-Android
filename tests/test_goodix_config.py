import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from generate_goodix_config import configuration,SOURCE


class GoodixConfiguration(unittest.TestCase):
    def test_public_profile_is_validated_not_generated_from_device_data(self):
        b=configuration(SOURCE.read_text());self.assertEqual(len(b),186)
        self.assertEqual(sum(b[:-1])&255,0);self.assertEqual(b[-1],1)
        self.assertEqual((int.from_bytes(b[1:3],'little'),int.from_bytes(b[3:5],'little')),(800,1280))

    def test_corrupt_sensor_group_or_payload_rejected(self):
        s=SOURCE.read_text()
        for changed in [s.replace('goodix,cfg-group0','goodix,cfg-group9',1),s.replace('44  20  03','44  21  03',1)]:
            with self.assertRaises(ValueError):configuration(changed)

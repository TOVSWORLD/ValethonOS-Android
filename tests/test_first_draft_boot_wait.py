import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from first_draft_capture_after_boot import wait_departure

class BootWait(unittest.TestCase):
    def test_owner_travel_does_not_consume_boot_observation(self):
        now=[0];states=iter([True,True,True,False])
        departed=wait_departure(lambda:next(states),clock=lambda:now[0],sleep=lambda n:now.__setitem__(0,now[0]+120))
        self.assertEqual(departed,240)
        self.assertEqual(departed+300,540)
    def test_absent_initial_device_and_travel_timeout_do_not_capture(self):
        with self.assertRaises(ValueError):wait_departure(lambda:False)
        now=[0]
        with self.assertRaises(TimeoutError):wait_departure(lambda:True,clock=lambda:now[0],sleep=lambda n:now.__setitem__(0,now[0]+601))

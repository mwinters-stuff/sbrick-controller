import unittest
import mock
from bluepy.btle import Peripheral, BTLEException

from SBrickCommunications import SBrickCommunications


class MyTestCase(unittest.TestCase):

    @mock.patch.object(Peripheral,'connect', autospec = True)
    def test_something(self, moc_connect):
        sb = SBrickCommunications("00:01:02:03:04:05")
        sb.run()
        moc_connect.assert_called_with("00:01:02:03:04:05")

    @classmethod
    def setUpClass(cls):
        print "setup class"

    @classmethod
    def tearDownClass(cls):
        print "teardown class"

def setUpModule():
    print "setupModule"

def tearDownModule():
    print "teardown Module"

if __name__ == '__main__':
    unittest.main()

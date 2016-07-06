import unittest
import mock
from bluepy.btle import Peripheral, BTLEException, Service, Characteristic

from SBrickCommunications import SBrickCommunications


class MyTestCase(unittest.TestCase):
    @mock.patch.object(Peripheral, 'connect', autospec=True)
    def test_something(self, moc_connect):
        sb = SBrickCommunications("00:01:02:03:04:05")

        with mock.patch.object(Peripheral, 'getServiceByUUID', autospec=True, return_value=Service(
                sb.SBrickPeripheral, '4dc591b0-857c-41de-b5f1-15abda665b0c', 0, 0xffff)) as moc_get_service:
            with mock.patch.object(Peripheral, 'getCharacteristics', autospec=True, return_value=[Characteristic(
                    sb.SBrickPeripheral, '02b8cbcc-0e25-4bda-8790-a15f53e6010f', 0x47, [0b00000010, 0b00001000], 0x47
            )]) as moc_get_characteristics:
                sb.run()
                moc_connect.assert_called_with(sb.SBrickPeripheral, "00:01:02:03:04:05")
                moc_get_service.assert_called_with(sb.SBrickPeripheral, '4dc591b0-857c-41de-b5f1-15abda665b0c')
                moc_get_characteristics.assert_called_with(sb.SBrickPeripheral)

    @classmethod
    def setUpClass(cls):
        print("setup class")

    @classmethod
    def tearDownClass(cls):
        print("teardown class")


# noinspection PyPep8Naming
def setUpModule():
    print("setupModule")


# noinspection PyPep8Naming
def tearDownModule():
    print("teardown Module")


if __name__ == '__main__':
    unittest.main()

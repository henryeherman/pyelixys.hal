import sys
sys.path.append("./")
sys.path.append("../")
import unittest
from statusfmt import StatusMessageFormatFactory


class StatusMessageFormatFactoryTest(unittest.TestCase):
    """ Tests for parsing packets from the elixys system """

    def setUp(self):
        """ Create some test data """
        statmsgfmt = StatusMessageFormatFactory()
        self.statstruct = statmsgfmt.get_struct()
        from testelixyshw import StatusSimulator 
        self.status = StatusSimulator()
        
        self.test_data = self.status.generate_packet_data()
        self.test_packet = self.status.generate_packet()



    def test_unpack(self):
        data = self.statstruct.unpack(self.test_packet)
        print "Testing Packet -> Data"
        for index in range(len(data)):
            sys.stdout.write(".")
            self.assertEqual(data[index], self.test_data[index])

        print

    def test_pack(self):
        print "Testing Data -> Packet"
        pkt = self.statstruct.pack(*self.test_data)
        self.assertEqual(pkt, self.test_packet)

if __name__ == '__main__':
    unittest.main()

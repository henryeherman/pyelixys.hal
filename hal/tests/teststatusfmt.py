import sys
sys.path.append("../")
import unittest
from statusfmt import StatusMessageFormatFactory
from statusfmt import config

class StatusMessageFormatFactoryTest(unittest.TestCase):
    """ Tests for parsing packets from the elixys system """
    
    def setUp(self):
        """ Create some test data """
        statmsgfmt = StatusMessageFormatFactory()
        self.statstruct = statmsgfmt.get_struct()
        from pktdata import test_data, test_packet
        self.test_data = test_data
        self.test_packet = test_packet
        
        
    def test_unpack(self):
        data = self.statstruct.unpack(self.test_packet)
        for index in range(len(data)):
            self.assertEqual(data[index], self.test_data[index])
    
    def test_pack(self):
        for i in range(len(self.test_data)):
            pass
            
if __name__=='__main__':
    unittest.main()
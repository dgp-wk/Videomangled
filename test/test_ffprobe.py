# -*- coding: UTF-8 -*-


"""Contains test cases for the ffprobe_parser object."""

import sys
import os.path
import unittest

PATH = os.path.realpath(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(PATH)))

try:
    from videomass3.vdms_THREADS.ffprobe_parser import FFProbe
except ImportError as error:
    print(error)
    sys.exit(1)

class FFprobeTestCase(unittest.TestCase):
    """Test case for FFProbe"""
    
    def setUp(self):
        """Method called to prepare the test fixture"""
        
        filename_url = 'url'
        ffprobe_url = ''
        
        self.data = FFProbe(ffprobe_url, 
                       filename_url, 
                       parse=True, 
                       pretty=True, 
                       select=None, 
                       entries=None,
                       show_format=True, 
                       show_streams=True, 
                       writer='default'
                       )
        
    def test_invalid_urls(self):
        """
        test error with an invalid url filename and/or 
        invalid executable.
        
        """
        if self.data.ERROR():
            self.assertRaises(AssertionError)
            self.assertEqual(self.data.data_format(), [])
        
    def test_available_urls(self):
        """
        test with an existing filename such video, audio, picture 
        and a valid link to the installed executable.
        Specifically, the basename of the executable must be ffprobe 
        or ffprobe.exe for MS
        
        """
        if not self.data.ERROR():
            self.assertEqual(self.data.error, False)
            self.assertTrue(self.data.data_format())

def main():
    unittest.main()

if __name__ == '__main__':
    main()

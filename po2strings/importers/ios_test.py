# -*- coding: utf-8 -*-

import os
import unittest
import ios

class iOSImporterTest(unittest.TestCase):
    def setUp(self):
        self.mock_matches = [
            {
                "context": "CONTEXT",
                "id": "Dear \"%s\",\nyou are visitor number %d!",
                "string": "Caro \"%s\",\nsei il visitatore numero %d!"
            }
        ]
        self.mock_destination_file = 'mock_destination_ios.strings'

    def tearDown(self):
        try:
            os.unlink(self.mock_destination_file)
        except Exception, e:
            pass

    # test that the iOSImporter class constructor sets matches and destination_file attributes
    def test_ctor(self):
        sut = ios.iOSImporter(
            self.mock_matches,
            self.mock_destination_file
        )

        self.assertEqual(sut.matches, self.mock_matches)
        self.assertEqual(sut.destination_file, self.mock_destination_file)
    
    # test that iOSImporter class run creates a .strings file containing input matches
    def test_run(self):
        sut = ios.iOSImporter(
            self.mock_matches,
            self.mock_destination_file
        )

        sut.run()

        with open(self.mock_destination_file, 'r') as destination_file:
            lines = destination_file.readlines()
            pot_content_as_string = "".join(lines)

            self.assertEqual(
                pot_content_as_string,
                '''
"Dear \"%@\",\nyou are visitor number %d!" = "Caro \"%@\",\nsei il visitatore numero %d!";
'''
            )
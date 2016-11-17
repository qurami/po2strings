# -*- coding: utf-8 -*-

import os
import unittest
import android

class AndroidImporterTest(unittest.TestCase):
    def setUp(self):
        self.mock_matches = [
            {
                "context": "CONTEXT",
                "id": "Dear %s,\nyou are visitor number %d!",
                "string": "Caro %s,\nsei il visitatore numero %d!"
            }
        ]
        self.mock_destination_file = 'mock_destination_android.xml'

    def tearDown(self):
        try:
            os.unlink(self.mock_destination_file)
        except Exception, e:
            pass

    # test that the AndroidImporter class constructor sets matches and destination_file attributes
    def test_ctor(self):
        sut = android.AndroidImporter(
            self.mock_matches,
            self.mock_destination_file
        )

        self.assertEqual(sut.matches, self.mock_matches)
        self.assertEqual(sut.destination_file, self.mock_destination_file)
    
    # test that AndroidImporter class run creates an XML file containing input matches
    def test_run(self):
        sut = android.AndroidImporter(
            self.mock_matches,
            self.mock_destination_file
        )

        sut.run()

        with open(self.mock_destination_file, 'r') as destination_file:
            lines = destination_file.readlines()
            pot_content_as_string = "".join(lines)

            self.assertEqual(
                pot_content_as_string,
                '''<?xml version="1.0" encoding="utf-8"?>
<resources>
	<string name="CONTEXT">Caro %1$s,\nsei il visitatore numero %2$d!</string>
</resources>'''
            )
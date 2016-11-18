# -*- coding: utf-8 -*-

import os
import unittest
import arb
import json

class ArbImporterTest(unittest.TestCase):
    def setUp(self):
        self.mock_matches = [
            {
                "context": "CONTEXT1",
                "id": "Dear \"%s\",\nyou are visitor number %d!",
                "string": "Caro \"%s\",\nsei il visitatore numero %d!"
            },
            {
                "context": "CONTEXT2",
                "id": "Your cart is empty",
                "string": "Il tuo carrello non contiene oggetti"
            },
            {
                "context": "CONTEXT3",
                "id": "Your cart contains 1 item",
                "string": "Il tuo carrello contiene un oggetto"
            },
            {
                "context": "CONTEXT4",
                "id": "Your cart contains %d items",
                "string": "Il tuo carrello contiene %d oggetti"
            }
        ]
        self.mock_destination_file = 'mock_destination_arb.arb'

        with open(self.mock_destination_file, 'w') as arb_file:
            mock_arb_file = '''{
    "visitorCounterMessage": "Dear \\"{visitorName}\\",\\nyou are visitor number {visitorNumber}!",
    "@visitorCounterMessage": {
        "type": "text",
        "placeholders": {
            "visitorName": {},
            "visitorNumber": {}
        }
    },
    "cartMessage": "{itemCounter,plural, =0{Your cart is empty}=1{Your cart contains 1 item}other{Your cart contains {itemCounter} items}}",
    "@cartMessage": {
        "type": "text",
        "placeholders": {
            "itemCounter": {}
        }
    }
}'''
            arb_file.write(mock_arb_file)
            arb_file.close()

    def tearDown(self):
        try:
            os.unlink(self.mock_destination_file)
        except Exception, e:
            pass

    # test that the ArbImporter class constructor sets matches and destination_file attributes
    def test_ctor(self):
        sut = arb.ArbImporter(
            self.mock_matches,
            self.mock_destination_file
        )

        self.assertEqual(sut.matches, self.mock_matches)
        self.assertEqual(sut.destination_file, self.mock_destination_file)

    # test that ArbImporter split_plural_string method splits plural string in multiple strings
    def test_split_plural_strings(self):
        sut = arb.ArbImporter('', '')

        mock_multiple_string = "{howMany,plural, =0{Dear {customerName}, your cart is empty}=1{Dear {customerName}, you''ve one item in your cart}other{Dear {customerName}, you have {howMany} items in your chart}}"
        self.assertEqual(
            sut.split_plural_string(
                mock_multiple_string,
                'howMany',
                ['howMany', 'customerName']
            ),
            [
                {
                    'plural_case': '=0',
                    'string': "Dear {customerName}, your cart is empty", 
                    'ordered_placeholders': ['customerName']
                },
                {
                    'plural_case': '=1',
                    'string': "Dear {customerName}, you''ve one item in your cart", 
                    'ordered_placeholders': ['customerName']
                },
                {
                    'plural_case': 'other',
                    'string': "Dear {customerName}, you have {howMany} items in your chart", 
                    'ordered_placeholders': ['customerName', 'howMany']
                }
            ]
        )
    
    # test that ArbImporter class clean_string method transforms any placeholder into %s 
    def test_clean_string(self):
        sut = arb.ArbImporter('', '')

        mock_string = "Hello %s, you are visitor number %d on site %s having score %f"
        self.assertEqual(
            sut.clean_string(mock_string),
            "Hello %s, you are visitor number %s on site %s having score %s"
        )

    # test that ArbImporter class clean_placeholders method strips {placeholders} from string
    # converting them to %s placeholders 
    def test_clean_placeholders(self):
        sut = arb.ArbImporter('', '')

        mock_string = "Hello {visitorName}, you are visitor number {visitorNumber}"
        mock_placeholders = ['visitorName', 'visitorNumber']
        self.assertEqual(
            sut.clean_placeholders(mock_string, mock_placeholders),
            "Hello %s, you are visitor number %s"
        )
    
    # test that ArbImporter class get_ordered_placeholders method returns an 
    # ordered array of strings containing {placeholders} in the input string
    def test_get_ordered_placeholders(self):
        sut = arb.ArbImporter('', '')

        mock_string = "This string contains {placeholder1}, {placeholder2} and {placeholder3}"
        self.assertEqual(
            sut.get_ordered_placeholders(mock_string),
            ['placeholder1', 'placeholder2', 'placeholder3']
        )

    # test that ArbImporter class run creates a .strings file containing input matches
    def test_run(self):
        sut = arb.ArbImporter(
            self.mock_matches,
            self.mock_destination_file
        )

        mock_output_arb_file = json.loads('''{
    "visitorCounterMessage": "Caro \\"{visitorName}\\",\\nsei il visitatore numero {visitorNumber}!",
    "@visitorCounterMessage": {
        "type": "text",
        "placeholders": {
            "visitorName": {},
            "visitorNumber": {}
        }
    },
    "cartMessage": "{itemCounter,plural, =0{Il tuo carrello non contiene oggetti}=1{Il tuo carrello contiene un oggetto}other{Il tuo carrello contiene {itemCounter} oggetti}}",
    "@cartMessage": {
        "type": "text",
        "placeholders": {
            "itemCounter": {}
        }
    }
}''')

        sut.run()

        with open(self.mock_destination_file, 'r') as arb_file:
            built_file = json.load(arb_file)
            arb_file.close() 

        self.assertEqual(
            built_file,
            mock_output_arb_file
        )
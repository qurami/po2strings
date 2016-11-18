# -*- coding: utf-8 -*-

import sys
import os
import re
import time
import datetime
import hashlib

from importers import android, ios, arb

class Po2StringsConverter:
    importer = None

    def __init__(self, po_file, strings_file):
        # verify if po_file exists:
        if not os.path.isfile(po_file):
            raise Exception("PO file %s doesn't exist" % (po_file))
        
        # get matches from PO file
        matches = self._get_matches(po_file)

        # check for destination strings file type
        if os.path.splitext(strings_file)[1] == ".xml":
            self.importer = android.AndroidImporter(matches, strings_file)
        elif os.path.splitext(strings_file)[1] == ".strings":
            self.importer = ios.iOSImporter(matches, strings_file)
        elif os.path.splitext(strings_file)[1] == ".arb":
            self.importer = arb.ArbImporter(matches, strings_file)
        else:
            raise Exception("Strings file format not supported for file %s" % (strings_file))

    def _clean_string(self, string):
        # split the string on new line char
        parts = string.split("\n")

        newParts = []

        # clean starting and ending double quotes
        for part in parts:
            part = re.sub(r'^"', '', part)
            part = re.sub(r'"$', '', part)
            newParts.append(part)
        
        # merge all the string subparts back as original string
        string = "".join(newParts)

        return string
    
    def _get_matches(self, po_file):
        # this was useful http://www.gossamer-threads.com/lists/python/dev/759682
        pattern = r"((msgctxt \"(?P<msgctxt>.*)\"\n)?msgid (?P<msgid>.*(?:\n\".*\")*))\nmsgstr (?P<msgstr>.*(?:\n\".*\")*)\n"
        prog = re.compile(pattern)

        matches_array = []

        # open file
        with open(po_file, 'r') as po:
            # read the whole file
            content = po.read()

            # iter the file finding valid PO matches
            for match in prog.finditer(content):
                # get and clean message id
                i = self._clean_string(match.groupdict().get('msgid'))
                # get and clean translated string
                s = self._clean_string(match.groupdict().get('msgstr'))
                # get message context
                c = match.groupdict().get('msgctxt')

                # if message id is null skip the string
                if i == '':  # id can't be null!
                    continue

                # create a context if not present
                if c is None:
                    c = self._create_context_id(i)

                # append the string to the matches array
                matches_array.append({
                    'context': c,
                    'id': i,
                    'string': s
                })

        return matches_array

    def _create_context_id(self, string):
        """
        Context strings will be used as string keys,
        so it is important to keep them unique from others
        """

        s = string.replace(' ', '_')  # convert spaces to underscores
        s = re.sub(r'\W', '', s)      # strip any NON-word char
        s = re.sub(r'^\d+', '', s)    # strip digits at the beginning of a string
        s = s.upper()                 # uppercase everything

        h1 = hashlib.md5(string).hexdigest()[0:5]
        h2 = hashlib.md5(string).hexdigest()[5:10]

        if len(s) > 60:
            s = s[:55]

        s = "K%s_%s_%s" % (h1, s, h2)  # on Android, keys cannot begin with digits

        return s

    def convert(self):
        self.importer.run()

# main
def _usage():
    print "Usage:", sys.argv[0], "<PO_FILE> <STRINGS_FILE>\n"


def main():
    if len(sys.argv) == 3:
        try:
            c = Po2StringsConverter(sys.argv[1], sys.argv[2])
            c.convert()
            print "OK"
        except Exception, e:
            print e
    else:
        _usage()


if __name__ == '__main__':
    main()
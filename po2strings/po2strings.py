# -*- coding: utf-8 -*-

import sys
import os
import re
import time
import datetime
import hashlib


ANDROID_FILE_HEADER = """<?xml version="1.0" encoding="utf-8"?>
<resources>
"""
ANDROID_FILE_FOOTER = "</resources>"


def _usage():
    print "Usage:", sys.argv[0], "<PO_FILE> <STRINGS_FILE>\n"


def _create_context_id(string):
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


def _clean_string(string):
    string = re.sub("\n", "", string)
    string = re.sub('""', '', string)
    string = re.sub(r'^"', '', string)
    string = re.sub(r'"$', '', string)
    return string


def _get_matches(poFile):
    # this was useful http://www.gossamer-threads.com/lists/python/dev/759682
    pattern = r"((msgctxt \"(?P<msgctxt>.*)\"\n)?msgid (?P<msgid>.*(?:\n\".*\")*))\nmsgstr (?P<msgstr>.*(?:\n\".*\")*)\n"
    prog = re.compile(pattern)

    out = []

    with open(poFile, 'r') as po:
        content = po.read()
        for match in prog.finditer(content):
            i = _clean_string(match.groupdict().get('msgid'))
            s = _clean_string(match.groupdict().get('msgstr'))
            c = match.groupdict().get('msgctxt')

            if i == '':  # id can't be null!
                continue

            if c is None:  # create a context if not present
                c = _create_context_id(i)

            out.append({
                'context': c,
                'id': i,
                'string': s
            })

    return out


def compile_for_android(poFile, stringsFile):
    matches = _get_matches(poFile)

    with open(stringsFile, 'w+') as sf:
        sf.write(ANDROID_FILE_HEADER)

        for m in matches:
            value = m['string']
            value = value.replace('<', '&lt;')
            value = value.replace('>', '&gt;')
            value = value.replace('\\"', '"')
            value = value.replace("'", "\\'")
            value = value.replace('%d', '%s')

            count = value.count('%s')

            for index in range(1, (count + 1)):
                value = value.replace('%s', '%s%s$s' % ('%', index), 1)

            content = "\t<string name=\"%s\">%s</string>\n" % (
                m['context'],
                value
            )

            sf.write(content)

        sf.write(ANDROID_FILE_FOOTER)

    return True, "OK"


def compile_for_apple(poFile, stringsFile):
    matches = _get_matches(poFile)

    with open(stringsFile, 'w+') as sf:
        for m in matches:
            identifier = m['id']
            identifier = identifier.replace('%s', '%@')

            value = m['string']
            value = value.replace('%s', '%@')

            content = "\n\"%s\" = \"%s\";\n" % (
                identifier,
                value
            )

            sf.write(content)

    return True, "OK"


def run(poFile, stringsFile):
    if not os.path.isfile(poFile):
        return False, "PO file %s doesn't exist\n" % (poFile)

    if os.path.splitext(stringsFile)[1] == ".xml":
        return compile_for_android(poFile, stringsFile)
    elif os.path.splitext(stringsFile)[1] == ".strings":
        return compile_for_apple(poFile, stringsFile)
    else:
        return False, "File format not recognized for destination file %s\n" % (
            stringsFile)


def main():
    if len(sys.argv) == 3:
        output, message = run(sys.argv[1], sys.argv[2])
        print message
    else:
        _usage()


if __name__ == '__main__':
    main()

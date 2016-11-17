# -*- coding: utf-8 -*-

class iOSImporter:
    def __init__(self, matches, strings_file):
        self.matches = matches
        self.destination_file = strings_file
    
    def run(self):
        with open(self.destination_file, 'w+') as sf:
            # for any match...
            for m in self.matches:
                # ... fix identifier and value...
                identifier = m['id']
                identifier = identifier.replace('%s', '%@')

                value = m['string']
                value = value.replace('%s', '%@')

                # ... set value as original string,
                # if it's blank (= has no translation)
                if value == "":
                    value = identifier

                # write the entry to the .strings file
                content = "\n\"%s\" = \"%s\";\n" % (
                    identifier,
                    value
                )

                sf.write(content)
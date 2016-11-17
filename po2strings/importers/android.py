# -*- coding: utf-8 -*-

class AndroidImporter:
    ANDROID_FILE_HEADER = """<?xml version="1.0" encoding="utf-8"?>
<resources>
"""
    ANDROID_FILE_FOOTER = "</resources>"

    def __init__(self, matches, strings_file):
        self.matches = matches
        self.destination_file = strings_file
    
    def run(self):
        with open(self.destination_file, 'w+') as sf:
            # write XML header
            sf.write(self.ANDROID_FILE_HEADER)

            # for any match...
            for m in self.matches:
                value = m['string']

                # ... set value as original string,
                # if it's blank (= has no translation)
                if value == "":
                    value = m['id']

                # apply char replacement
                value = value.replace('<', '&lt;')
                value = value.replace('>', '&gt;')
                value = value.replace('\\"', '"')
                value = value.replace("'", "\\'")

                # convert the %s format to %1$s format

                # counts how many variables in the string are present
                count = value.count('%s') + value.count('%d')

                # apply transformation
                for index in range(1, (count + 1)):
                    occurrence_of_s = value.find("%s")
                    occurrence_of_d = value.find("%d")
                    if occurrence_of_s == -1 and occurrence_of_d >= 0:
                        value = value.replace('%d', '%s%s$d' % ('%', index), 1)
                        continue
                    if occurrence_of_d == -1 and occurrence_of_s >= 0:
                        value = value.replace('%s', '%s%s$s' % ('%', index), 1)
                        continue
                    if occurrence_of_d != -1 and occurrence_of_s != -1:
                        if occurrence_of_d < occurrence_of_s:
                            value = value.replace('%d', '%s%s$d' % ('%', index), 1)
                        else:
                            value = value.replace('%s', '%s%s$s' % ('%', index), 1)
                
                # write the <string> tag to the XML
                content = "\t<string name=\"%s\">%s</string>\n" % (
                    m['context'],
                    value
                )

                sf.write(content)

            # write XML footer
            sf.write(self.ANDROID_FILE_FOOTER)
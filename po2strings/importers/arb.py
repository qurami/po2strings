# -*- coding: utf-8 -*-

import os
import json
import re

class ArbImporter:
    def __init__(self, matches, strings_file):
        self.matches = matches
        self.destination_file = strings_file
    
    def clean_string(self, string):
        s = string.replace("%d", "%s")
        s = s.replace("%f", "%s")
        return s

    def clean_placeholders(self, string, placeholders):
        for placeholder in placeholders:
            string = string.replace("{%s}" % placeholder, "%s")
        return string
    
    def get_ordered_placeholders(self, string):
        placeholder_pattern = r"{([a-zA-Z0-9_]+)}"
        return re.findall(placeholder_pattern, string)

    def split_plural_string(self, plural_string, plural_placeholder, placeholders):
        # init output array
        split_strings = []

        # this pattern finds if the string contains plurals
        pattern = r"^{"+ plural_placeholder +",plural, (?P<imploded_string>.*)}"
        prog = re.compile(pattern)

        # if there is no plural match, just return
        match = prog.match(plural_string)
        if not match:
            return []

        # get the group of plural strings, e.g.
        #  =0{string value}=1{string value}other{string value}
        imploded_string = match.groupdict()['imploded_string']

        # safely remove {placeholders} to avoid replace in the following loop
        for placeholder in placeholders:
            imploded_string = imploded_string.replace("{%s}" % placeholder, "_#|%s|#_" % placeholder)

        # consume the string to get all the plural cases
        while imploded_string != '':
            # get position of first { char and first } char,
            # we'll then be sure that the content is a string value for a plural case
            entry = imploded_string[imploded_string.find('{')+1:imploded_string.find('}')]

            # restore placeholders in the {placeholder} format
            for placeholder in placeholders:
                entry = entry.replace("_#|%s|#_" % placeholder, "{%s}" % placeholder)

            # get ordered placeholders
            ordered_placeholders = self.get_ordered_placeholders(entry)
            
            # append the entry to the output array
            split_strings.append({
                'plural_case': imploded_string[:imploded_string.find('{')],
                'string': entry,
                'ordered_placeholders': ordered_placeholders
            })

            # go to the next case, if it does exist
            imploded_string = imploded_string[imploded_string.find('}')+1:]

        return split_strings

    def run(self):
        # check if the destination file exists,
        # as it will be replaced by the translated version of itself
        if not os.path.isfile(self.destination_file):
            raise Exception("Destination arb file %s doesn't exist" % (self.destination_file))

        # open the arb file and convert it to a dictionary
        # using json.load (arb is JSON in fact), then close the file
        with open(self.destination_file, 'r') as arb_file:
            arb_file_as_dict = json.load(arb_file)
            arb_file.close()

        # cycle the arb dictionary
        for key in arb_file_as_dict:
            try:
                # keys with @ prefix hold the placeholders,
                # keys without it hold the string

                placeholders = []
                if key[0] == '@':
                    # get placeholders for current key
                    for placeholder in arb_file_as_dict[key]['placeholders']:
                        placeholders.append(placeholder)

                    # get string...
                    source_string = arb_file_as_dict[key[1:]]

                    # on plural strings, we'll split the string into multiple
                    # entries, because they are stored separately into the PO
                    # translations file

                    # set if it is singular case
                    strings_to_parse_for_key = [{
                        'plural_case': 'single',
                        'string': source_string,
                        'ordered_placeholders': self.get_ordered_placeholders(source_string)
                    }]
                    plural = False
                    plural_placeholder = None

                    # now check if plural
                    for placeholder in placeholders:
                        if "{%s,plural" % placeholder in source_string:
                            strings_to_parse_for_key = self.split_plural_string(source_string, placeholder, placeholders)
                            plural_placeholder = placeholder
                            plural = True
                            break

                    # prepare an empty array of strings found in PO file
                    strings_found_in_po = []

                    # for each string to parse for current key
                    for each_string_to_parse in strings_to_parse_for_key:
                        untraslated_string = self.clean_placeholders(
                            each_string_to_parse['string'],
                            placeholders
                        )

                        # search for matches in translated PO file
                        for m in self.matches:
                            translated_string_id = self.clean_string(m['id'])

                            # if they do match, we can put the translated string
                            # into arb_file_as_dict[key[1:]]
                            if translated_string_id == untraslated_string:
                                each_string_to_parse['string'] = self.clean_string(m['string'])
                                strings_found_in_po.append(each_string_to_parse)

                    if len(strings_found_in_po) > 0:
                        # if the string is not plural we can just restore
                        # its ordered placeholders
                        if not plural:
                            translation = strings_found_in_po[0]['string']
                            for placeholder in strings_found_in_po[0]['ordered_placeholders']:
                                translation = translation.replace('%s', "{%s}" % placeholder, 1)
                        
                        # if it is plural, we have to rejoin the plural string
                        # according to the specific format
                        else:
                            translation = ''
                            for string_entry in strings_found_in_po:
                                for placeholder in string_entry['ordered_placeholders']:
                                    string_entry['string'] = string_entry['string'].replace('%s', "{%s}" % placeholder, 1)
                                translation += "%s{%s}" % (string_entry['plural_case'], string_entry['string'])
                            
                            translation = "%s,plural, %s}" % (
                                source_string[:source_string.find(',plural, ')],
                                translation
                            )
                        
                        # eventually, we replace the original string with its translation
                        arb_file_as_dict[key[1:]] = translation
            except Exception, e:
                print "Exception on key %s" % key, e
        
        # save the arb_file_as_dict as self.destination_file
        with open(self.destination_file, 'w+') as sf:
            json.dump(arb_file_as_dict, sf)
            sf.close()
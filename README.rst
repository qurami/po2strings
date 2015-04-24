po2strings
==========

po2strings is useful to convert PO/POT gettext files into Apple .strings or Android/Java .xml files.


Installation
------------

::

  pip install po2strings


Command line usage
------------------

::

  root@host$ po2strings <PO_FILE> <STRINGS_FILE>

e.g.

::

  root@host$ po2strings en.po Localizable.strings

  root@host$ po2strings en.po values.xml


Code usage
----------

::

  from po2strings import po2strings

  executed, error_message = po2strings.run("en.po", "Localizable.strings")

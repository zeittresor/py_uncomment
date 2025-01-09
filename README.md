# py_uncomment
Remove the comment entries of a LLM in the py code

this simple script is removing all the comments a LLM might add to document the python code.
the idea to remove it is to save some tokens.. IMHO each LLM (so far) is somehow limited to a specifyed number of input tokens.
by removing the documentary comments it might be possible to save some of them for ex. if you would like to copy/paste your code to a LLM chat dialog.

usage:
py_uncomment.py [filename]
-> Should create a backup of the original code as [filename].backup.py and a new version with the same name like the sourcecode but without the "#" comments inside.

Its doing the same if you start it without a filename, but in that case a filedialog box should be viewed to select the file you want to be uncommented.

If you past the new sourcecode to a LLM it IMHO needs some less tokens to work with it.

Script Source: https://github.com/zeittresor/py_uncomment

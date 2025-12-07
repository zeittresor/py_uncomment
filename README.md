# py_uncomment
Remove the comment entries of a LLM in the py code

this simple script is removing all the comments a LLM might add to document the python code.
the idea to remove it is to save some tokens.. IMHO each LLM (so far) is somehow limited to a specifyed number of input tokens.
by removing the documentary comments it might be possible to save some of them for ex. if you would like to copy/paste your code to a LLM chat dialog.

btw. a backup of your original script should be also created to make sure that the script is not removing "too much".

Script Source: https://github.com/zeittresor/py_uncomment


Update 12-2025:

- Added some Options to the GUI

  <img width="605" height="316" alt="grafik" src="https://github.com/user-attachments/assets/21697b58-32ef-4a16-9694-b92a071155fe" />

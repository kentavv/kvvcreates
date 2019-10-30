These files are Autodesk Fusion 360 post processors. The originals, downloaded
from http://cam.autodesk.com/posts/, are marked with the '- original' suffix.
The others are modified versions for milling and turning. 

Changes from the originals:
1. increased the allowed size of the tool library
2. include descriptions of all tools used in the g-code file at the start of the file
3. include tool descriptions immediately following the comment containing the operation
   name, and preceeding the tool change command. 

These changes are to help the operator to locate the tool and to verify that the tool 
that Fusion 360 is expecting matches the one in hand.

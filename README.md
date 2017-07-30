mapgen
======

## Please note: I wrote this years ago in school, the code quality is poor and there are no tests. Use/read at your own risk!

Not actively maintained, but do email me in case of problems/questions.

Incomplete but usable python program to generate height and terrain maps, using the diamond-square algorithm.

Generates a wide range of terrain types with different preconditions (e.g. blobby water-level marshes, scattered trees less common on snow); can place buildings and route paths between them taking terrain into account.
Behaviour can be configured by modifying constants.py, better configuration of terrain types is a to-do.

Requires PIL (or Pillow).

N.B. - master is usually broken, use tagged releases for anything.

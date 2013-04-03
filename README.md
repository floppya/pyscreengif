screengif
========

screengif is a tool for taking animated screenshots.

Requirements
============
screengif is based on [PyQt4](http://www.riverbankcomputing.com/software/pyqt/download).
I've only tested this in win7 but it ought to work wherever PyQt works.
It also has a dependency on [Python Imaging Library](http://www.pythonware.com/products/pil/).

Binary version
==============
For those who have no idea what to do with the python code, I've created
a [binary package for Windows](http://www.filedropper.com/pyscreengif) with
py2exe. Apologies for the current, spammy host.

Usage
=====
* If you're using the binary package, run 'screengif.exe', othewise run
the 'start.bat', 'start.sh', or 'src/main.py' depending on your system.
* Select a region on your desktop by holding left-click and dragging
* Adjust fps and output size as you'd like.
* Click record
* When you're done recording, click the 'stop recording' button
* Click the 'Save GIF' or 'Save image sequence' button
* Make the world laugh

License
=======
MIT 

Exceptions:
* images2gif.py: BSD - The attributions can be found in that file.


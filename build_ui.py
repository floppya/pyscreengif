#!/usr/bin/env python
import os


def build_ui(filename, targetDir):
    print 'Building %s' % filename
    sourceFilename = os.path.join(
        targetDir, filename
    )
    targetFilename = os.path.join(
        targetDir, 'ui_%s.py' % filename[:-len('.ui')]
    )
    cmd = 'pyuic4 %s > %s' % (
        sourceFilename, targetFilename
    )
    os.system(cmd)


def build_qrc(filename, targetDir):
    print 'Building %s' % filename
    sourceFilename = os.path.join(
        targetDir, filename
    )
    targetFilename = os.path.join(
        targetDir, '%s_rc.py' % filename[:-len('.qrc')]
    )
    cmd = 'pyrcc4 %s > %s' % (
        sourceFilename, targetFilename
    )
    os.system(cmd)


RESOURCE_ACTIONS = {
    '.ui': build_ui,
    '.qrc': build_qrc
}


def main(rootDir='.'):
    """Recursively find all UI files and apply pyuic4/pyrcc4 to them."""
    print('Searching for UI files...')
    for dirpath, dirnames, filenames in os.walk(rootDir):
        for filename in filenames:
            for extension, action in RESOURCE_ACTIONS.items():
                if filename.endswith(extension):
                    sourceFilename = os.path.join(dirpath, filename)
                    print('Found: %s' % sourceFilename)
                    action(filename, dirpath)


if __name__ == '__main__':
    main()


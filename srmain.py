#!/usr/bin/python
     
import sys, csv, gettext
from PySide.QtGui import *
from srview import MainWindow

if __name__ == '__main__':

    # Initialize internationalization (gettext)
    gettext.install('shotrecorder', './locale', unicode=True)
    translation_en = gettext.translation("shotrecorder", "./locale", languages=['en'])
    translation_fi = gettext.translation("shotrecorder", "./locale", languages=['fi'])
    translation_en.install()

    # Needed to read Unicode .mo files
    _ = translation_fi.ugettext

    app = QApplication(sys.argv)

    # Initialize GUI
    mainwindow = MainWindow()
    mainwindow.show()

    app.exec_()
    sys.exit()

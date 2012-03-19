#!/usr/bin/python

from os import path

from PySide.QtCore import *
from PySide.QtGui import *

from srmodel import *

class MainWindow(QMainWindow):
    """View main window"""

    def __init__(self,  *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.setWindowTitle(_("Shotrecorder"))

        # Create a new SessionDialog
        self.sessiondialog = SessionDialog()
        self.setCentralWidget(self.sessiondialog)

        # Add a session menu containing a limited number of subentries
        self.sessionmenu = self.menuBar().addMenu(_("Session"))

        # New session; the "session" is appended there to accommodate Nokia
        # N900 which does not display menu name, only the entries.
        self.sessionmenu_new = self.sessionmenu.addAction(_("New session"))
        self.sessionmenu_new.triggered.connect(self.NewSessionTrigger)

        # Open session; not especially useful, implement later
        self.sessionmenu_open = self.sessionmenu.addAction(_("Open session"))
        self.sessionmenu_open.triggered.connect(self.OpenSessionTrigger)

        # Save session
        self.sessionmenu_save = self.sessionmenu.addAction(_("Save session"))
        self.sessionmenu_save.triggered.connect(self.SaveSessionTrigger)

    def NewSessionTrigger(self):
        """Create a new session"""
        self.sessiondialog = SessionDialog()
        self.setCentralWidget(self.sessiondialog)

    def OpenSessionTrigger(self):
        """Save session to a file"""
        self.sessiondialog = SessionDialog()
        filename = QFileDialog.getOpenFileName(self, _("Open session"), path.expanduser("~"), "*.csv")
        # QFileDialog return a tuple with filename and filter
        self.sessiondialog.session.OpenFromCSV(filename[0])
        self.setCentralWidget(self.sessiondialog)
        self.sessiondialog.Refresh()

    def SaveSessionTrigger(self):
        """Save session to a file"""
        filename = QFileDialog.getSaveFileName(self, _("Save session"), path.expanduser("~"), "*.csv")
        self.sessiondialog.session.SaveAsCSV(filename[0])

class QTableWidgetItemNumeric(QTableWidgetItem):
        """Customized item, mostly to allow overriding the __cmp__ operation"""

        def __init__(self):
            super(QTableWidgetItemNumeric, self).__init__()
 
        def __cmp__(self, other):

            if int(self.text()) < int(other.text()):
                return -1
            elif int(self.text()) == int(other.text()):
                return 0
            else:
                return 1

class InfoLabel(QLabel):
    """Simple info label"""

    def __init__(self, parent):
        super(InfoLabel, self).__init__()

        self.parent = parent

        # Insert text field containing derived information
        self.avgvelfield = _("Average velocity")
        self.avgveltext = "0.00"
        self.avgvelunit = _("m/s")
        self.Refresh()

    def Refresh(self):
        """Refresh dynamic content"""
        self.avgveltext = str(self.parent.session.GetAverageVelocity())
        self.setText(self.avgvelfield + " " + self.avgveltext + " " + self.avgvelunit)


class SessionDialog(QDialog):
    """Dialog for adding shots"""

    def __init__(self, parent=None):
        super(SessionDialog, self).__init__(parent)
        self.layout = QGridLayout()
        self.layout.rowCount = 6
        self.layout.columnCount = 2

        # Attach to a Session
        self.session = Session()

        # Shot table widget
        self.shottable = QTableWidget()
        self.shottable.setEditTriggers(QAbstractItemView.DoubleClicked)
	self.shottable.setSortingEnabled(True)
        self.layout.addWidget(self.shottable,1,1,4,1)

        # Add dynamically updating infobox
        self.info = InfoLabel(self)
        self.layout.addWidget(self.info, 5,1,1,1)

        # Insert "Remove" button
        self.removebutton = QPushButton(_("Remove"))
        self.removebutton.setAutoDefault(False)
        self.connect(self.removebutton, SIGNAL("clicked()"), self.RemoveShotTrigger)
        self.layout.addWidget(self.removebutton,5,2)

        # Insert the "Add" button
        self.addbutton = QPushButton(_("Add"))
        # If setAutoDefault(False) is not used, clicking return will trigger two 
        # signals: one from the "Add" button and one from the QLineEdit object. 
        # This seems to cause erratic str->float conversion errors, even though 
        # the value does get added to the session.
        self.addbutton.setAutoDefault(False)
        self.connect(self.addbutton, SIGNAL("clicked()"), self.AddShotTrigger)
        self.layout.addWidget(self.addbutton,6,2)

        # Insert the new shot entry form
        self.lineedit = QLineEdit()
        self.lineedit.setPlaceholderText(_("0.00"))
        self.lineedit.setMaxLength(10)
        self.lineedit.setValidator(QDoubleValidator())
        self.lineedit.selectAll()
        self.layout.addWidget(self.lineedit,6,1)

        self.connect(self.lineedit, SIGNAL("returnPressed()"), self.AddShotTrigger)

        self.setLayout(self.layout)

        self.shottable.sortItems(0)

        # Update list from the Session object
        self.Refresh()

    def Refresh(self):
        """Update tree view widget after data has been modified"""

        # Initialize the table widget
        self.shottable.clear()
        self.shottable.setRowCount(len(self.session))

        headers = [ _("Shot #"), _("Velocity (m/s)") ]
        self.shottable.setColumnCount(len(headers))
        self.shottable.setHorizontalHeaderLabels(headers)

        # We need to disabled sorting before populating the table
        self.shottable.setSortingEnabled(False)

        # Add content to the table
        row = 0

        # This loop is never entered _after_ the first run, apparently because 
        # the last entry was reached (using next()) and the internal pointer was 
        # not returned to 0 prior to the next run. Besides this the Session 
        # enumerator seemed to work fine.

        #print self.sessionGetShots()
        #for num, data in enumerate(self.session):

        for shot in self.session.GetShots():

            #print str(shot[0]) + " " + str(shot[1])
            # Shot number
            numw = QTableWidgetItemNumeric()
            numw.setText(str(shot[0]))
            numw.setData(Qt.UserRole,shot[0])
            numw.setTextAlignment(Qt.AlignRight|Qt.AlignVCenter)
            
            # Shot velocity
            velw = QTableWidgetItem(str(shot[1]))
            velw.setTextAlignment(Qt.AlignRight|Qt.AlignVCenter)
 
            # Add these to the table
            self.shottable.setItem(row, 0, numw)
            self.shottable.setItem(row, 1, velw)
            row += 1

        # Make sure the new item is visible. We catch the exception to avoid 
        # error message when len(self.session) == 0, i.e. we have deleted all 
        # rows and press the "Remove" button.
        try:
            self.shottable.scrollToItem(velw)
            self.shottable.setCurrentItem(velw)
        except UnboundLocalError:
            pass

        # Now we can re-enable sorting
        self.shottable.setSortingEnabled(True)

        self.shottable.resizeColumnToContents(0)
        self.shottable.resizeColumnToContents(1)

        # Update infotext field
        self.info.Refresh()

        self.lineedit.setFocus()

    def AddShotTrigger(self):
        """Add shot to the list"""
        text = unicode(self.lineedit.text())
        self.session.AddShot(float(text))
        self.lineedit.clear()
        self.Refresh()

    def RemoveShotTrigger(self):
        """Remove shot from the list"""
        # We need to read the shot number from the QTableWidget in order to know 
        # which shot to delete from the Session instance.

        if self.shottable.rowCount() > 0:
            currentrow = self.shottable.currentRow()
            shotnum = self.shottable.item(currentrow,0).text()
            self.session.RemoveShot(int(shotnum))
            self.Refresh()

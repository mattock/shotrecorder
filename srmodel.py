#!/usr/bin/python

import csv

from PySide.QtCore import *
from PySide.QtGui import *

class Session():
    """Class encapsulating a session. Separates data storage from the displaying widget"""
    def __init__(self,  *args, **kwargs):
        # We use a dictionary with a identifier and Shot object pairs
        self.shots = {}

        # Counter, used to generate the shot identifier
        self.shotcount = 0

        # Iterator support, see
        # http://www.rexx.com/~dkuhlman/python_101/python_101.html
        self.iterator = self._next()
        self.next = self.iterator.next

    def AddShot(self, velocity):
        """Add a shot to this session"""
        self.shots[self.shotcount] = Shot(velocity)
        self.shotcount = self.shotcount + 1

    def AddShotWithNum(self, shotnum, velocity):
        """Add a shot with given shot number to this session"""
        self.shots[shotnum] = Shot(velocity)

    def SetShotCount(self):
        """Set shotcount to avoid overwriting old shots when session is loaded from a (CSV) file"""
        self.shotcount = max(self.shots.iterkeys()) + 1

    def RemoveShot(self,shotnum):
        """Delete shot based on it's number"""
        del self.shots[shotnum]

    def AddTestList(self):
        for vel in [52,52.3,52.3,55.2,54.3,52.1]:
            self.AddShot(vel)

    def GetShots(self):
        """Return an array of tuples (shot number + velocity)"""
        shotlist = []
        # We can't use self.shotcount, as user may have deleted some shots from 
        # the middle.
        pos = 0
        for shotnum in self.shots:

            shotlist.append((shotnum, self.shots[shotnum].velocity))
            pos += 1

        return shotlist

    def GetAverageVelocity(self):
        """Return the average velocity for this session"""
        
        if len(self.shots) == 0:
            return 0
        else:
            sum = 0
            for shot in self.shots:
                sum += self.shots[shot].velocity

            return round(sum/len(self.shots), 2)

    def OpenFromCSV(self, filename):
        """Open the session from a CSV"""

        reader = csv.reader(open(filename, "r"), delimiter=";")
        for row in reader:
            self.AddShotWithNum(int(row[0]), float(row[1]))

        self.SetShotCount()

    def SaveAsCSV(self, filename):
        """Save the session to a CSV file"""

        writer = csv.writer(open(filename, "wb"), delimiter=";")
        for shotnum in self.shots:
            writer.writerow([shotnum,self.shots[shotnum].velocity])

    def __len__(self):
        return len(self.shots)

    def __str__(self):
        text = ""
        for shotnum in self.shots:
            text = text + " " + str(self.shots[shotnum].velocity)
        return text

    # We want to support the iterator protocol so that we can loop though 
    # content of this instance easily.
    def __iter__(self):
        return self

    def _next(self):
        for shotnum in self.shots:
            yield shotnum, self.shots[shotnum].velocity


class Shot():
    """Class containing all information specific to a single shot"""
    
    def __init__(self):
        self.velocity = 0

    def __init__(self, velocity):
        self.velocity = velocity

    def GetVelocity(self):
        """Return shot velocity"""
        return self.velocity

    def SetVelocity(self, velocity):
        """Set measured velocity"""
        self.velocity = velocity


if __name__ == "__main__":

    session = Session()
    session.AddTestList()

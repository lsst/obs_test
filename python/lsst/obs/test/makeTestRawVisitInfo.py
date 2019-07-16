# This file is part of obs_test.
#
# Developed for the LSST Data Management System.
# This product includes software developed by the LSST Project
# (http://www.lsst.org).
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
__all__ = ["MakeTestRawVisitInfo"]

from lsst.afw.image import VisitInfo, RotType
from lsst.afw.geom import degrees, SpherePoint
from lsst.afw.coord import Observatory, Weather
from lsst.obs.base import MakeRawVisitInfo


class MakeTestRawVisitInfo(MakeRawVisitInfo):
    """Make a VisitInfo from the FITS header of a test image.

    Notes
    -----
    Since the test data is extracted from LSST Sim data,
    this is a copy of MakeLsstSimRawVisitInfo
    (using a copy avoids undesireable dependencies).
    """
    observatory = Observatory(-70.749417*degrees, -30.244633*degrees, 2663)  # long, lat, elev

    def setArgDict(self, md, argDict):
        """Set an argument dict for VisitInfo and pop associated metadata.

        Parameters
        ----------
        md : `lsst.daf.base.PropertySet`
            Image metadata.
        argDict : `dict`
            A dict of arguments for the `lsst.afw.image.VisitInfo`
            constructor. Updated by this call.

        Returns
        -------
        visitInfo : `lsst.afw.image.VisitInfo`
            Visit information.
        """
        MakeRawVisitInfo.setArgDict(self, md, argDict)
        argDict["darkTime"] = self.popFloat(md, "DARKTIME")
        argDict["boresightAzAlt"] = SpherePoint(
            self.popAngle(md, "AZIMUTH"),
            self.altitudeFromZenithDistance(self.popAngle(md, "ZENITH")),
        )
        argDict["boresightRaDec"] = SpherePoint(
            self.popAngle(md, "RA_DEG"),
            self.popAngle(md, "DEC_DEG"),
        )
        argDict["boresightAirmass"] = self.popFloat(md, "AIRMASS")
        argDict["boresightRotAngle"] = -self.popAngle(md, "ROTANG")
        argDict["rotType"] = RotType.SKY
        argDict["observatory"] = self.observatory
        argDict["weather"] = Weather(
            self.popFloat(md, "TEMPERA"),
            self.pascalFromMmHg(self.popFloat(md, "PRESS")),
            float("nan"),
        )
        return VisitInfo(**argDict)

    def getDateAvg(self, md, exposureTime):
        """Return date at the middle of the exposure.

        Parameters
        ----------
        md : `lsst.daf.base.PropertySet`
            Image metadata.
        exposureTime : `float`
            Exposure time, in sec

        Returns
        -------
        dateAvg : `lsst.daf.base.DateTime`
            Date at middle of the exposure, or `lsst.daf.base.DateTime()`
            if the metadata item ``TAI`` is not found.
        """
        startDate = self.popMjdDate(md, "TAI", timesys="TAI")
        return self.offsetDate(startDate, 0.5*exposureTime)

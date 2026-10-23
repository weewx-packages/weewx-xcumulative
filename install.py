"""
This program is free software; you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation; either version 2 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU General Public License for more details.

                 Installer for the Cumulative XType Extension

Version: 0.1.1                                          Date: 23 October 2026

Revision History
    23 October 2026     v0.1.1
        -   replaced distutils.version.StrictVersion (removed in Python 3.12)
            with a plain version tuple comparison
        -   dropped Python 2 support
    23 October 2022     v0.1.0
        -   initial implementation
"""

# python imports
import re
from setup import ExtensionInstaller

# WeeWX imports
import weewx


REQUIRED_VERSION = "4.6.0"
XCUM_VERSION = "0.1.1"


def version_tuple(version):
    """Convert a version string to a tuple of its leading numeric components.

    Args:
        version (str): A version string such as '5.0.0b3'.

    Returns:
        tuple[int]: The numeric components, a pre-release suffix is dropped,
        eg (5, 0, 0).
    """
    return tuple(int(x) for x in re.findall(r'\d+', version)[:3])


def loader():
    return XCumulativeInstaller()


class XCumulativeInstaller(ExtensionInstaller):
    def __init__(self):
        if version_tuple(weewx.__version__) < version_tuple(REQUIRED_VERSION):
            msg = "%s requires WeeWX %s or greater, found %s" % (''.join(('Cumulative XType ', XCUM_VERSION)),
                                                                 REQUIRED_VERSION,
                                                                 weewx.__version__)
            raise weewx.UnsupportedFeature(msg)
        super().__init__(
            version=XCUM_VERSION,
            name='XCumulative',
            description='A WeeWX XType to produce cumulative series data with user specified reset times.',
            author="Gary Roderick",
            author_email="gjroderick<@>gmail.com",
            xtype_services=['user.xcumulative.StdCumulativeXType'],
            files=[('bin/user', ['bin/user/xcumulative.py'])]
        )

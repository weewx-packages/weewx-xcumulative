#
#    Test the Cumulative XType against a small archive in the WeeWX schema.
#
#    This program is free software; you can redistribute it and/or modify it
#    under the terms of the GNU General Public License as published by the
#    Free Software Foundation; either version 3 of the License, or (at your
#    option) any later version.
#
"""Series produced by the cumulative aggregate, with and without resets."""

import os
import pathlib
import sys
import time

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'bin'))
sys.path.insert(0, str(ROOT))

pytest.importorskip('weecfg.extension', reason="needs weewx on the path")

import weewx
import weewx.manager
import weewx.xtypes
from weeutil.weeutil import TimeSpan

import weewx.schemas.wview_extended
from install import XCumulativeInstaller, version_tuple
from user.xcumulative import StdCumulativeXType, XCumulative

HOUR = 3600


@pytest.fixture(autouse=True)
def local_timezone():
    """Run in a zone with an offset, so local and UTC midnight differ."""
    old = os.environ.get('TZ')
    os.environ['TZ'] = 'Europe/Berlin'
    time.tzset()
    yield
    if old is None:
        del os.environ['TZ']
    else:
        os.environ['TZ'] = old
    time.tzset()


def local(day, hour=0):
    """Timestamp of a local time in January 2026.

    Args:
        day (int): Day of the month.
        hour (int): Hour of the day.

    Returns:
        int: The timestamp.
    """
    return int(time.mktime((2026, 1, day, hour, 0, 0, 0, 0, -1)))


@pytest.fixture
def archive(tmp_path):
    """Hourly archive from 10 Jan 00:00 to 12 Jan 00:00, 1 unit of rain each hour.

    The 11 Jan 05:00 record has no rain, as if the gauge reported None.
    """
    db_dict = {'database_name': str(tmp_path / 'archive.sdb'),
               'driver': 'weedb.sqlite', 'SQLITE_ROOT': str(tmp_path)}
    with weewx.manager.DaySummaryManager.open_with_create(
            db_dict, schema=weewx.schemas.wview_extended.schema) as manager:
        for stamp in range(local(10) + HOUR, local(12) + HOUR, HOUR):
            rain = None if stamp == local(11, 5) else 1.0
            manager.addRecord({'dateTime': stamp, 'usUnits': weewx.METRIC,
                               'interval': 60, 'rain': rain})
        yield manager


@pytest.fixture
def xtype():
    return XCumulative()


def series(xtype, manager, start, stop, **options):
    """Hourly cumulative series.

    Returns:
        tuple[list, list]: Stop times and the cumulative values.
    """
    _, stop_vt, data_vt = xtype.get_series('rain', TimeSpan(start, stop), manager,
                                           'cumulative', HOUR, **options)
    return stop_vt[0], data_vt[0]


def test_without_reset_the_total_runs_through(xtype, archive):
    stops, data = series(xtype, archive, local(10), local(11))

    assert data == [float(n) for n in range(1, 25)]
    assert stops[-1] == local(11)


def test_midnight_reset_restarts_the_total(xtype, archive):
    stops, data = series(xtype, archive, local(10), local(12), reset='midnight')

    by_stop = dict(zip(stops, data))
    assert by_stop[local(10, 23)] == 23.0
    # The span ending on the reset time is discarded and the total restarts.
    assert by_stop[local(11)] == 0.0
    assert by_stop[local(11, 4)] == 4.0


def test_midday_reset_uses_local_time(xtype, archive):
    stops, data = series(xtype, archive, local(10), local(11), reset='12:00')

    by_stop = dict(zip(stops, data))
    assert by_stop[local(10, 11)] == 11.0
    assert by_stop[local(10, 12)] == 0.0
    assert by_stop[local(10, 13)] == 1.0


def test_none_values_are_skipped_unless_asked_for(xtype, archive):
    stops, data = series(xtype, archive, local(11), local(12))
    assert local(11, 5) not in stops
    assert len(stops) == 23

    stops, data = series(xtype, archive, local(11), local(12), ignore_none=False)
    by_stop = dict(zip(stops, data))
    assert len(stops) == 24
    # The gap adds nothing to the total.
    assert by_stop[local(11, 5)] == by_stop[local(11, 4)]


def test_result_carries_the_unit_of_the_archive(xtype, archive):
    _, _, data_vt = xtype.get_series('rain', TimeSpan(local(10), local(11)), archive,
                                     'cumulative', HOUR)

    assert (data_vt[1], data_vt[2]) == ('cm', 'group_rain')


def test_other_aggregates_are_not_handled(xtype, archive):
    with pytest.raises(weewx.UnknownAggregation):
        xtype.get_series('rain', TimeSpan(local(10), local(11)), archive, 'max', HOUR)


def test_unparsable_reset_names_the_option(xtype, archive):
    with pytest.raises(weewx.ViolatedPrecondition, match='1T2T3'):
        series(xtype, archive, local(10), local(11), reset='1T2T3')


def test_service_registers_the_xtype_ahead_of_the_others(archive):
    class Engine:
        pass

    service = StdCumulativeXType(Engine(), {})
    try:
        assert weewx.xtypes.xtypes[0] is service.xcumulative
        _, _, data_vt = weewx.xtypes.get_series(
            'rain', TimeSpan(local(10), local(11)), archive, 'cumulative', HOUR)
        assert data_vt[0][-1] == 24.0
    finally:
        service.shutDown()
    assert service.xcumulative not in weewx.xtypes.xtypes


def test_installer_registers_the_service_and_module():
    installer = XCumulativeInstaller()

    assert installer['xtype_services'] == ['user.xcumulative.StdCumulativeXType']
    assert installer['files'] == [('bin/user', ['bin/user/xcumulative.py'])]


def test_version_tuple_compares_numerically():
    assert version_tuple('5.5.2') >= version_tuple('4.6.0')
    assert version_tuple('4.10.1') > version_tuple('4.6.0')
    assert version_tuple('4.5.1') < version_tuple('4.6.0')
    assert version_tuple('5.0.0b3') == (5, 0, 0)

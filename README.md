# Cumulative XType

A WeeWX XType that adds the aggregate type `cumulative`. It produces a running
total of an observation, such as rain, that restarts at a time you choose. In an
image generator plot this gives, for example, rainfall since midnight. It does not
store anything in the database.

This is a continuation of [gjr80/weewx-xcumulative](https://github.com/gjr80/weewx-xcumulative)
by Gary Roderick, which no longer exists. It starts from the last copy of that
repository, [Millardiang/weewx-xcumulative](https://github.com/Millardiang/weewx-xcumulative).

![Rainfall since midnight](assets/daycumulativerain.png)

## Requirements

WeeWX with a database that holds the observation you want to total. There are no
external programs and no pip packages.

## Installation

Install `xcumulative` from the [WeeWX packages catalog](https://github.com/weewx-packages/catalog/blob/main/packages/xcumulative.md).
The catalog page lists the current release, its WeeWX and Python
requirements, and the install, update and removal commands.

The installer adds `user.xcumulative.StdCumulativeXType` to `xtype_services` in
`weewx.conf`. Restart WeeWX afterwards.

## Configuration

The extension has no section in `weewx.conf`. Select it in a plot of a skin's
`skin.conf`, with the options below on the plot line:

```ini
[ImageGenerator]
    [[day_images]]
        [[[daycumulativerain]]]
            [[[[rain]]]]
                aggregate_type = cumulative
                aggregate_interval = 1h
                reset = midnight
                plot_type = bar
```

| Option | Default | Meaning |
|---|---|---|
| `aggregate_interval` | none, required | Length of each data point. The total is reported at the end of each interval. |
| `reset` | no reset | When the total returns to zero. One of the keywords `midnight`, `midday`, `day`, `month`, `year`, or a time `HH:MM` (every day), `DDTHH:MM` (day of the month), `MM-DDTHH:MM` (day of the year), `YYYY-MM-DDTHH:MM` (once). |
| `ignore_none` | `true` | `true` leaves out data points that have no value. `false` keeps them in the series, and they add nothing to the total. |

The keywords stand for these times: `midnight` and `day` for `00:00` each day,
`midday` for `12:00` each day, `month` for `1T00:00` and `year` for `01-01T00:00`.

The point that ends exactly on a reset time is reported as zero and its own value
is not counted. Outside a plot, call
`XCumulative().get_series(obs_type, timespan, db_manager, 'cumulative', interval, reset=...)`
with the same options.

## Limitations

* Tested with a small SQLite archive in the WeeWX schema, not with a live station
  or the image generator's rendered output.
* A day of the month that the month does not have, such as `31T00:00` in April,
  raises a `ValueError`.
* A reset time that does not parse falls back to `00:00`, a date that does not
  parse is ignored, so the reset then happens every day.

## Development

```
just fast
```

Run it from the repository root with the Python of a WeeWX installation on `PATH`.

## License

Copyright Gary Roderick. GNU General Public License, version 3 or any later
version. See `LICENSE`.

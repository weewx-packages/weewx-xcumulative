# weewx-xcumulative

WeeWX XType for the `cumulative` aggregate type with user selectable reset times.
Independent continuation of gjr80/weewx-xcumulative (original deleted).

## Phase

Alpha. Keep tests to a few fast ones for the main path.

## Structure

* `install.py` registers `user.xcumulative.StdCumulativeXType` in `xtype_services`.
  It must not import `distutils`.
* `bin/user/xcumulative.py` holds the XType and the service.
* `tests/` builds an SQLite archive with the WeeWX schema. No hardware needed.

## Conventions

Python follows WeeWX style: no runtime annotations, types in Google docstrings.
GPL files carry a dated entry in their revision history, plus one in `changelog`.
README follows the weewx-packages schema and names no versions or archive URLs.

## Tests

`just fast` runs the suite in about two seconds. Needs WeeWX and pytest on `PATH`.

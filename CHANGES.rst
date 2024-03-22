=================================
Change log for gocept.pytestlayer
=================================

8.2 (unreleased)
================

- Make tests compatible with pytest >= 7.3.

- Add support for Python 3.12.


8.1 (2022-09-05)
================

- Ensure compatibility with pytest >= 7.1.3.
  ``.layered.LayeredTestCaseInstance`` now has to inherit from
  ``_pytest.unittest.UnitTestCase``.


8.0 (2021-12-13)
================

- Use GitHub actions as CI.

- Add support for Python 3.9 and 3.10.

- Drop support for Python 3.6.

- Add a workaround for
  `#4 <https://github.com/gocept/gocept.pytestlayer/issues/4>`_: Use
  ``gcoept.pytestlayer.doctest.DocTestSuite`` instead of
  ``doctest.DocTestSuite`` to circumvent the issue.


7.0 (2020-08-03)
================

Backwards imcompatible changes
------------------------------

- Drop support for Python 2.7 and 3.5 and ``pytest < 5.0``. (#8)

Features
--------

- Support ``pytest >= 6.0``. (#8)


6.3 (2020-05-15)
================

- Ensure compatibility with pytest > 5.4.2. We need a
  ``_explicit_tearDown`` on our ``LayeredTestCaseFunction`` now.


6.2 (2020-03-20)
================

- Ensure compatibility with pytest > 5.4. We need a
  ``_needs_explicit_tearDown`` on our ``LayeredTestCaseFunction`` now.


6.1 (2020-02-20)
================

- Fix tests to run with `pytest >= 4.2.0`.

- Migrate to Github.

- Do not break when rerunning a doctest using `pytest-rerunfailures`.

- Add support for Python 3.8.


6.0 (2018-10-24)
================

- Add support for Python 3.6, 3.7 and PyPy3.

- Drop support for Python 3.4.

- Fix tests to run with `pytest >= 3.9.1`.

- Release also as universal wheel.

- Update to new pytest fixture API to avoid DeprecationWarnings. (#10)


5.1 (2016-12-02)
================

- Make installation process compatible with `setuptools >= 30.0`.


5.0 (2016-08-23)
================

- Fix tests to pass if `pytest >= 3.0` is used for testing.


4.0 (2016-04-27)
================

- Support Python 3.4, 3.5 and PyPy.

- Use tox as testrunner.


3.0 (2016-04-14)
================

- Claim compatibility with py.test 2.9.x.

- Drop Python 2.6 support.

2.1 (2014-10-22)
================

- Update handling of keywords and doctest testnames for py.test-2.5.
  [wosc]

- Re-introduce ``gocept.pytestlayer.fixture.create()`` method, to allow giving
  created fixtures a non-random name, so other fixtures can depend on them.
  [tlotze, wosc]

- Generate session-scoped fixtures from layers in addition to class-scoped
  ones, if a session-scoped one is required somewhere, the class-scoped ones
  are simply ignored. [tlotze, wosc]


2.0 (2013-09-19)
================

- Remove need to explicitely create fixtures.
  [gotcha]

- Add ``plone.testing.layered`` test suites support.
  [gotcha]

- Made tests a bit more robust.
  [icemac]


1.0 (2013-08-28)
================

- Initial release.
  [tlotze, icemac, gotcha]

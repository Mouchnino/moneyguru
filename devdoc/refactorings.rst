====================
Ongoing Refactorings
====================

Some big refactorings take time. This is the page where the currently ongoing refactoring are listed so that you aren't surprised to see lack of consistency in these areas.

Pytest-ification
================

Test units are migrating to TestCase-less tests. This has a lot of implications. The most obvious one is that setup code that was previously in ``TestCase.setUp()`` methods now go in setup functions. Previously, however, all test support instances were created through ``tests.base.TestCase.create_instances()``. This has changed, and now those instances are created by the ``tests.base.TestApp`` class. For example, a setup that looked like::

    def setUp(self):
        self.create_instances()
        self.add_account('foo')
        self.add_entry(description='bar')

would become::

    def app_with_entry():
        app = TestApp()
        app.add_account('foo')
        app.add_entry(description='bar')
        return app

Tests then invoke these setups with the ``@with_app`` decorator::

    @with_app(app_with_entry)
    def test_entry_count(app):
        eq_(len(app.etable.rows), 1)

The reason why we use ``@with_app`` instead of simply doing ``app = app_with_entry()`` at the beginning of the tests is because the ``@with_app`` decorator supports setups with patchings. For example, if we want a test that patches today's date, we'd do::

    def app_with_patched_today():
        p = Patcher()
        p.patch_today(2010, 3, 27)
        app = TestApp()
        return app, p

and any test using this setup with ``@with_app`` will have the patching effective for the duration of the test. The ``Patcher`` class comes from ``hscommon.testutil`` and replaces ``mock_*`` methods that ``hscommon.testcase.TestCase`` used to offer.

One other change in idioms are the cases where the same tests was made in different testcases. Nose-ificating those will result in a test function name clash. Fortunately, Nose supports test generators. So what used to be same-test-in-multiple-testcase becomes a test generator with multiple setup func calls. In some cases, there are name clashes for tests that don't do the same thing and for which generators don't apply. In these cases, we have to rename tests to something more specifically descriptive.

More responsibilities to the view classes
=========================================

With moneyGuru 2.0, a new view system is put in place. This will allow for new views to be more easily added. In the *before times*, a lot of code that was specific to a view would go in the ``Document`` because that was the only place it could go into. Shortly before the 2.0 refactoring, view classes were added, but they had very few responsibilities other than holding references to their children. With 2.0, code is being pushed up to views to lighten up the ``Document`` class which is getting pretty heavy.

Traditionally, all GUI elements were connected directly to the ``Document`` for notifications. Since they were all independent from each other, it worked well. During the big 2.0 re-factoring, more responsibilities were given to the view classes. Because most GUI elements are children to the view classes (and thus not independent from them), the notification system caused problems because in a lot of cases, when GUI would listen to the same notification as their view, the view needed to process the notification first. Because no order is guaranteed in the notification dispatches, all hell broke loose.

Most views only contain a handful of GUI elements. Therefore, moneyGuru's codebase is migrating to a system where GUI elements that are part of views don't listen to ``Document`` notifications anymore. The parent view takes the responsibility to call appropriate methods on their children when it gets notifications from the ``Document``.

It's rather ugly for now and results in code duplication in views' event handlers, but once the re-factoring is over, some consolidation should be possible.

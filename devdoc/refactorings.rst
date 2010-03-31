====================
Ongoing Refactorings
====================

Some big refactorings take time. This is the page where the currently ongoing refactoring are listed so that you aren't surprised to see lack of consistency in these areas.

Nose-ification
==============

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

and any test using this setup with ``@with_app`` will have the patching effective for the duration of the test. The ``Patcher`` class comes from ``hsutil.testutil`` and replaces ``mock_*`` methods that ``hsutil.testcase.TestCase`` used to offer.

One other change in idioms are the cases where the same tests was made in different testcases. Nose-ificating those will result in a test function name clash. Fortunately, Nose supports test generators. So what used to be same-test-in-multiple-testcase becomes a test generator with multiple setup func calls. In some cases, there are name clashes for tests that don't do the same thing and for which generators don't apply. In these cases, we have to rename tests to something more specifically descriptive.
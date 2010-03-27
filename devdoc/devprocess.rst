===================
Development Process
===================

moneyGuru is developed using `Test Driven Development <http://en.wikipedia.org/wiki/Test-driven_development>`_, leaning heavily toward `iterative development <http://en.wikipedia.org/wiki/Iterative_and_incremental_development>`_. Refactoring is very frequent, but is done in small steps. The goal is to never have to make a major rewrite, **but**, at the same time, never be trapped by past design mistakes. We call that "having your cake and eating it too".

Tests
=====

moneyGuru's development process is different from many other TDD projects because almost all tests are "high level" (read the `article I wrote about this <http://www.hardcoded.net/articles/high-level-testing.htm>`_). This means that almost all tests **exclusively** use publicly available API. By "publicly available API", I don't mean public methods, I mean that API that is available to the GUI layer. This is why, even though the ``Transaction`` class is a core entity of moneyGuru, it is never tested directly. It (technically, it's not ``Transaction`` we're testing, it's the behavior that it provides) is always tested through a GUI element (such as ``core.gui.transaction_table.TransactionTable``).

Although this method empowers the developer with nearly unlimited refactoring potential, it makes tests harder to write and harder to organize. It is often hard to determine where a test belong and how it should be written. Tests are divided in two main categories: "gui" tests and "topical" tests. 

"gui" tests are in ``core.tests.gui`` and cover the behavior of specific gui elements (for example, testing if the transaction table has the correct number of rows after adding a new transaction).

The second type of tests live directly in ``core.tests`` and test specific behaviors of the application (for example, whether split balancing is done correctly). These tests are grouped in topical units, such as ``split_test``. Note that although these tests don't directly test gui elements behavior, *they still go through these gui elements to perform their testing*.

Test code is the type of code that is the most dangerous to refactor. moneyGuru has a lot of legacy test code lying around, in wrong places or in an old coding style (``main_test``, moneyGuru's first test unit, has a lot of those, which are at the same time core behavioral tests). Although it would be a good thing to refactor those, it still has to be done very carefully, which rules out a mass refactoring. Refactoring a test requires the developer to correctly understand the intent of the test and setup code, which is sometimes not so clear (although all tests must have comments describing their intent, this description sometimes become irrelevant due to refactorings in the code). Such an understanding can't be achieved in a mass refactoring. Therefore, the motto is: If you're playing around a test that you notice need refactoring and that you're confident you can do it safely, do it.

Tickets
=======

moneyGuru's ticket system is at https://hardcoded.lighthouseapp.com/projects/31473-moneyguru/overview . All known bugs and feature requests are listed there. This section explains how the ticket statuses, tags and milestones are organized.

Status
------

- **new:** This ticket is new and hasn't been reviewed yet. For a bug, it means that it hasn't been reproduced, and for a feature request, it means it hasn't been accepted.
- **accepted:** This ticket has been reviewed and accepted by HS. For a bug, it means it has been reproduced.
- **hold:** Some external feedback is needed to either continue working on the ticket, or to close it. For feature tickets, this status means that something is holding the feature back. Either because it has a low priority or because it needs more design work for it to be "gracefully" implemented into the app.
- **fixed:** This ticket was valid and has been fixed.
- **invalid:** This ticket is invalid, either because the bug can't be reproduced, or that the feature request is rejected.

Tags
----

There are 2 types of tickets: bugs, feature request. Bugs are tagged as ``bug``. Feature requests are tagged as ``feature``. Sometimes, a ticket only affect one platform of the project. In those cases, a tag indicates which ones (`cocoa`, `qt`).

All other tags are free-form.

Milestones
----------

A milestone is usually an upcoming release. For tickets to be worked on, they need to be part of an upcoming release first (milestone), so when tickets are accepted, the must be moved to a milestone. Once in the milestone, they can be assigned to developers and work on them can begin. When all tickets of a milestone are completed, releases are made, and the milestone is considered completed.

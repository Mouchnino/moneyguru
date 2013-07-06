====================
Ongoing Refactorings
====================

Some big refactorings take time. This is the page where the currently ongoing refactoring are listed so that you aren't surprised to see lack of consistency in these areas.

More responsibilities to the view classes
=========================================

With moneyGuru 2.0, a new view system is put in place. This will allow for new views to be more easily added. In the *before times*, a lot of code that was specific to a view would go in the ``Document`` because that was the only place it could go into. Shortly before the 2.0 refactoring, view classes were added, but they had very few responsibilities other than holding references to their children. With 2.0, code is being pushed up to views to lighten up the ``Document`` class which is getting pretty heavy.

Traditionally, all GUI elements were connected directly to the ``Document`` for notifications. Since they were all independent from each other, it worked well. During the big 2.0 re-factoring, more responsibilities were given to the view classes. Because most GUI elements are children to the view classes (and thus not independent from them), the notification system caused problems because in a lot of cases, when GUI would listen to the same notification as their view, the view needed to process the notification first. Because no order is guaranteed in the notification dispatches, all hell broke loose.

Most views only contain a handful of GUI elements. Therefore, moneyGuru's codebase is migrating to a system where GUI elements that are part of views don't listen to ``Document`` notifications anymore. The parent view takes the responsibility to call appropriate methods on their children when it gets notifications from the ``Document``.

It's rather ugly for now and results in code duplication in views' event handlers, but once the re-factoring is over, some consolidation should be possible.

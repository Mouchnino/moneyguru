<%inherit file="/base_help.mako"/>
${next.body()}

<%def name="menu()"><%
self.menuitem('en/intro.htm', 'Introduction', 'Introduction to moneyGuru')
self.menuitem('en/basics.htm', 'Basics', 'Basic concepts in moneyGuru')
self.menuitem('en/edition.htm', 'Editing', 'How to edit a moneyGuru document')
self.menuitem('en/import.htm', 'Import', 'Import data from your bank &amp; old application')
self.menuitem('en/currencies.htm', 'Currencies', 'How currencies work')
self.menuitem('en/cash.htm', 'Cash', 'Cash management strategies')
self.menuitem('en/reconciliation.htm', 'Reconciliation', 'How reconciliation works')
self.menuitem('en/forecast.htm', 'Forecasting', 'Scheduling and budgeting')
self.menuitem('en/faq.htm', 'F.A.Q.', 'Frequently Asked Questions')
self.menuitem('en/versions.htm', 'Version History', 'Changes moneyGuru went through')
self.menuitem('en/credits.htm', 'Credits', 'People who contributed to moneyGuru')
%></%def>
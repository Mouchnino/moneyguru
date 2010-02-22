<%inherit file="/base_help.mako"/>
${next.body()}

<%def name="menu()"><%
self.menuitem('intro.htm', 'Introduction', 'Introduction to moneyGuru')
self.menuitem('basics.htm', 'Basics', 'Basic concepts in moneyGuru')
self.menuitem('edition.htm', 'Editing', 'How to edit a moneyGuru document')
self.menuitem('import.htm', 'Import', 'Import data from your bank &amp; old application')
self.menuitem('currencies.htm', 'Currencies', 'How currencies work')
self.menuitem('cash.htm', 'Cash', 'Cash management strategies')
self.menuitem('reconciliation.htm', 'Reconciliation', 'How reconciliation works')
self.menuitem('forecast.htm', 'Forecasting', 'Scheduling and budgeting')
self.menuitem('faq.htm', 'F.A.Q.', 'Frequently Asked Questions')
self.menuitem('versions.htm', 'Version History', 'Changes moneyGuru went through')
self.menuitem('credits.htm', 'Credits', 'People who contributed to moneyGuru')
%></%def>
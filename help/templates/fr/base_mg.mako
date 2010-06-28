<%inherit file="/base_help.mako"/>
${next.body()}

<%def name="menu()"><%
self.menuitem('fr/intro.htm', 'Introduction', 'Introduction à moneyGuru')
self.menuitem('fr/basics.htm', 'Concepts', 'Concepts de base')
self.menuitem('fr/edition.htm', 'Édition', 'Modifier un document')
self.menuitem('fr/import.htm', 'Importer', 'Importer vos données')
self.menuitem('fr/currencies.htm', 'Devises', 'Le concept de devises')
self.menuitem('fr/cash.htm', 'Liquide', 'Gestion de liquidités')
self.menuitem('fr/reconciliation.htm', 'Réconciliation', 'Réconcilier les transactions')
self.menuitem('fr/forecast.htm', 'Prévisions', 'Récurrences et budgets')
self.menuitem('fr/faq.htm', 'F.A.Q.', 'Foire aux questions')
self.menuitem('fr/versions.htm', 'Historique', 'Historique des versions')
self.menuitem('fr/credits.htm', 'Crédits', 'Qui contribue à moneyGuru')
%></%def>
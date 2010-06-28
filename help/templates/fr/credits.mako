<%!
	title = 'Crédits'
	selected_menu_item = 'crédits'
%>
<%inherit file="/fr/base_mg.mako"/>
Voici la liste des contributeurs de moneyGuru. Merci!

${self.credit('Virgil Dupras', 'Programmeur', website='www.hardcoded.net', email='hsoft@hardcoded.net')}

${self.credit('Eric McSween', 'Programmeur')}

${self.credit('Mike Rohde', 'Design icône', website='www.rohdesign.com')}

${self.credit('Python', 'Langage de programmation', "Le meilleur des meilleurs", 'www.python.org')}

${self.credit('PyObjC', 'Pont Python/Cocoa', "Pour la version Mac OS X", 'pyobjc.sourceforge.net')}

${self.credit('Sparkle', 'Librairie de mise-à-jour', "Pour la version Mac OS X", 'andymatuschak.org/pages/sparkle')}

${self.credit('AMButtonBar', 'Les barres de filtre', "Pour la version Mac OS X", 'www.harmless.de')}

${self.credit('PSMTabBarControl', "Les barres d'onglets", "Pour la version Mac OS X", 'www.positivespinmedia.com')}

${self.credit('Vous', 'Utilisateur moneyGuru', "Merci!")}

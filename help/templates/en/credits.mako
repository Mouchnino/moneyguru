<%!
	title = 'Credits'
	selected_menu_item = 'Credits'
%>
<%inherit file="/en/base_mg.mako"/>
Below is the list of direct or indirect contributors to moneyGuru. Thanks!

${self.credit('Virgil Dupras', 'Developer', website='www.hardcoded.net', email='hsoft@hardcoded.net')}

${self.credit('Eric McSween', 'Developer')}

${self.credit('Mike Rohde', 'Main icon designer', website='www.rohdesign.com')}

${self.credit('Python', 'Programming language', "The bestest of the bests", 'www.python.org')}

${self.credit('PyObjC', 'Python-to-Cocoa bridge', "Used for the Mac OS X version", 'pyobjc.sourceforge.net')}

${self.credit('Sparkle', 'Auto-update library', "Used for the Mac OS X version", 'andymatuschak.org/pages/sparkle')}

${self.credit('AMButtonBar', 'Filter bar component', "Used for the Mac OS X version", 'www.harmless.de')}

${self.credit('PSMTabBarControl', 'Tab bar component', "Used for the Mac OS X version", 'www.positivespinmedia.com')}

${self.credit('You', 'moneyGuru user', "moneyGuru ain't much without you")}

#!/usr/bin/make -f

all:
	dh_prep  
	dh_installdirs
	python3 build_modules.py
	chmod +x src/run.py
	cp -R src/ $(CURDIR)/debian/moneyguru/usr/share/moneyguru
	cp $(CURDIR)/debian/moneyguru.desktop $(CURDIR)/debian/moneyguru/usr/share/applications
	ln -s /usr/share/moneyguru/run.py $(CURDIR)/debian/moneyguru/usr/bin/moneyguru

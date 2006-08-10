# Makefile for matplotlib users_guide
#PYTHON = /usr/bin/python2.4
# path to your matplotlib src tree
#MATPLOTLIB = /home/darren/src/matplotlib/matplotlib

all:
	make graphs figs dvi pdf

clean: 	
	find . \( -name "*~" -o -name "*.pyc" -o -name "#*" \) | xargs rm -f;\
	rm -f *.log *.aux *.dvi *.bbl *.blg *.toc *.out *.backup


pdf: 	
	latex users_guide
	bibtex users_guide
	pdflatex users_guide

dvi: 	
	latex users_guide
	bibtex users_guide
	latex users_guide

graphs:
	cd dot; python makedot.py
#        cd dot; ${PYTHON} makedot.py

figs:
	cd code; python runall.py
#        cd dot; ${PYTHON} runall.py

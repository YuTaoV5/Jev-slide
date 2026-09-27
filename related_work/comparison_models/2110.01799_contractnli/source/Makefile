BUILDDIR = build
SRC = emnlp2021.sty acl_natbib.bst main.bib *.tex fig/*.pdf fig/*.png tab/*.tex

all: ms.pdf ms_anonymous.pdf src.zip

ms.pdf ms.aux ms.bbl: $(SRC)
	pdflatex -interaction=nonstopmode ms.tex
	bibtex ms
	pdflatex -interaction=nonstopmode ms.tex
	pdflatex -interaction=nonstopmode ms.tex
	pdflatex -interaction=nonstopmode ms.tex

ms_anonymous.pdf ms_anonymous.aux ms_anonymous.bbl: $(SRC)
	pdflatex -interaction=nonstopmode ms_anonymous.tex
	bibtex ms_anonymous
	pdflatex -interaction=nonstopmode ms_anonymous.tex
	pdflatex -interaction=nonstopmode ms_anonymous.tex
	pdflatex -interaction=nonstopmode ms_anonymous.tex

src.zip: $(SRC) ms.bbl
	mkdir -p $(BUILDDIR)/files
	rsync -rR $^ Makefile $(BUILDDIR)/files
	rm $(BUILDDIR)/files/ms_anonymous.tex
	cd $(BUILDDIR)/files && zip -r ../src.zip * && cd ../..
	mv $(BUILDDIR)/src.zip .
	rm -r $(BUILDDIR)

clean:
	rm -f ms.pdf ms.dvi ms.bbl ms_blind.bbl ms.out ms.log ms.blg ms.synctex.gz
	rm -f ms_anonymous.pdf ms_anonymous.dvi ms_anonymous.bbl ms_anonymous_blind.bbl ms_anonymous.out ms_anonymous.log ms_anonymous.blg ms_anonymous.synctex.gz
	rm -f *.aux
	rm -f src.zip


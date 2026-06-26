.PHONY: reproduce clean tables figures diff

reproduce:
	python pipeline/run_all.py

tables:
	python pipeline/90_make_tables.py

figures:
	python pipeline/91_make_figures.py

diff:
	python pipeline/99_diff_against_scaffold.py

clean:
	find results -type f \( -name "*.csv" -o -name "*.json" -o -name "*.md" -o -name "*.txt" \) -delete
	find paper/tables -type f -delete
	find paper/figures -type f -delete

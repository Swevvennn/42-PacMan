install:
	pip install -r requirements.txt

run:
	python3 pac-man.py config.json

debug:
	python3 -m pdb pac-man.py config.json

clean:
	rm -rf __pycache__ */__pycache__ */*/__pycache__ .mypy_cache venv

lint:
	flake8 src
	mypy --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs src

lint-strict:
	flake8 src
	mypy --strict src

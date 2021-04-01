.PHONY: quality test release update serve clean

quality:
	black --check .
	flake8

test: quality
	pytest -vvs

release:
	fullrelease
	pip install -e ".[dev]"

update:
	pip install --upgrade --upgrade-strategy eager -e ".[dev]"

serve:
	source .env && krcg-bot

clean:
	rm -rf dist
	rm -rf .pytest_cache

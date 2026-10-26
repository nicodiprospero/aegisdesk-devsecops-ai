.PHONY: dev env test scan scan-image redteam pin-base up down

VENV := .venv
PY := $(VENV)/bin/python

dev:
	python3 -m venv $(VENV)
	$(PY) -m pip install --require-hashes -r requirements.txt -r requirements-dev.txt

env:
	python3 scripts/setup_env.py

test:
	$(PY) -m pytest --cov=app --cov-report=term-missing --cov-fail-under=85

scan:
	python3 scripts/lint_prompts.py
	python3 scripts/check_unicode.py
	bandit -r app scripts -c pyproject.toml
	semgrep scan --config p/python --config p/owasp-top-ten --config p/secrets --error --metrics off app/ scripts/
	pip-audit -r requirements.txt --require-hashes
	checkov -d . --framework dockerfile github_actions --compact --quiet --skip-path .venv
	zizmor --min-severity medium .github/workflows/

scan-image:
	docker build -t aegisdesk:local .
	trivy image --severity CRITICAL,HIGH --ignore-unfixed --exit-code 1 aegisdesk:local

redteam:
	npx --yes promptfoo@0.125.1 eval -c redteam/promptfooconfig.yaml --no-cache

# Fixa a imagem base pelo digest atual (build reprodutível)
pin-base:
	@DIGEST=$$(docker buildx imagetools inspect python:3.13-slim-trixie --format '{{json .Manifest.Digest}}' | tr -d '"'); \
	sed -i "s#FROM python:3.13-slim-trixie\(@sha256:[a-f0-9]*\)\? AS#FROM python:3.13-slim-trixie@$$DIGEST AS#g" Dockerfile; \
	grep -n '^FROM' Dockerfile

up:
	docker compose up -d --build

down:
	docker compose down

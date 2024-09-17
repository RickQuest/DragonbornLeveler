OS := $(shell uname -s 2>/dev/null || echo Windows_NT)

setup: setup-env setup-tesseract

setup-env:
	conda env create --file environment.yml || conda env update --file environment.yml

setup-tesseract:
ifeq ($(OS),Windows_NT)
	@echo "Detected Windows"
	@python tools/tesseract_setup.py
else
	@echo "Detected Linux"
	@python3 tools/tesseract_setup.py
endif

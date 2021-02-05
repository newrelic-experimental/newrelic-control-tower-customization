PROJECT = NewRelicCTOnboarding
FUNCTION = $(PROJECT)
DIST_DIR ?= $(BASE)/dist
$(shell mkdir -p $(DIST_DIR))

all: build

.PHONY: clean build

clean:
	rm -rf build
	rm -rf $(DIST_DIR)/$(FUNCTION).zip

build: clean
	mkdir -p build/site-packages
	zip -r $(DIST_DIR)/$(FUNCTION).zip . -x "*.DS_Store*" "*.git*" "build*" "Makefile" "requirements.txt"
	python3 -m venv build/$(FUNCTION)
	. build/$(FUNCTION)/bin/activate; \
	pip3 install  -r requirements.txt; \
	cp -r $$VIRTUAL_ENV/lib/python3.7/site-packages/ build/site-packages
	cd build/site-packages; zip -g -r $(DIST_DIR)/$(FUNCTION).zip . -x "*__pycache__*"


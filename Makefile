
BUCKET_PREFIX := wellsiau-quickstart
KEY_PREFIX := newrelic
PACKAGES_PREFIX := lambda_packages/
CFT_PREFIX := templates
CFT_DIR := templates

PROFILE := default
REGION := us-east-1

BUCKET_NAME ?= service_not_defined
BUILD_DIR = $(shell /bin/pwd)/build
DIST_DIR = $(shell /bin/pwd)/dist

s3_buckets := $(BUCKET_PREFIX)

TOPTARGETS := all clean package build

SUBDIRS := $(wildcard src/*/.)
ZIP_FILES := $(shell find $(DIST_DIR) -type f -name '*.zip')

$(TOPTARGETS): $(SUBDIRS)
$(SUBDIRS):
	$(MAKE) -C $@ $(MAKECMDGOALS) $(ARGS) DIST_DIR="${DIST_DIR}"

upload: $(s3_buckets)

$(s3_buckets): 
	$(info [+] Uploading artifacts to '$@' bucket)
	@$(MAKE) _upload BUCKET_NAME=$@

_upload: $(ZIP_FILES)
	$(info [+] Uploading templates to $(BUCKET_NAME) bucket)
	@aws --profile $(PROFILE) --region $(REGION) s3 cp $(CFT_DIR)/ s3://$(BUCKET_NAME)/$(KEY_PREFIX)/$(CFT_PREFIX) --recursive --exclude "*" --include "*.yaml" --include "*.yml" --acl public-read

$(ZIP_FILES):
	@aws --profile $(PROFILE) --region $(REGION) s3 cp $@ s3://$(BUCKET_NAME)/$(KEY_PREFIX)/$(PACKAGES_PREFIX) --acl public-read

.PHONY: $(TOPTARGETS) $(SUBDIRS) $(s3_buckets) $(ZIP_FILES)

#-------------------------------------------------------------------------------------
#
# Start Configuration
#
#-------------------------------------------------------------------------------------

# the upstream project
OBS_PROJECT := EA4

# the package name in OBS
OBS_PACKAGE := mpm_itk

#-------------------------------------------------------------------------------------
#
# End Configuration
#
#-------------------------------------------------------------------------------------

#-------------------------------------------------------------------------------------
#
# TODO
#
#-------------------------------------------------------------------------------------
# - Cleaning the OBS target when files are removed from git
# - Add a obs_dependencies target to rebuild the package and all of it's dependencies
# - Create a devel RPM that contains all of these Makefile stubs.  This way it's
#   in one place, instead of being copied everywhere.
#
#

#-------------------
# Variables
#-------------------

# allow override
ifndef $(ARCH)
ARCH := $(shell uname -m)
endif

ERRMSG := "Please read, https://cpanel.wiki/display/AL/Setting+up+yourself+for+using+OBS"
OBS_USERNAME := $(shell grep -A5 '[build.dev.cpanel.net]' ~/.oscrc | awk -F= '/user=/ {print $$2}')

# NOTE: OBS only like ascii alpha-numeric characters
GIT_BRANCH := $(shell git branch | awk '/^*/ { print $$2 }' | sed -e 's/[^a-z0-9]/_/ig')
ifdef bamboo_repository_git_branch
GIT_BRANCH := $(bamboo_repository_git_branch)
endif

# if we're pushing to master, push to the upstream project
ifeq ($(bamboo_repository_git_branch),master)
BUILD_TARGET := $(OBS_PROJECT)
else
BUILD_TARGET := home:$(OBS_USERNAME):$(OBS_PROJECT):$(GIT_BRANCH)
endif
# OBS does not support / in branch names
$(substr /,-,BUILD_TARGET)


OBS_WORKDIR := $(BUILD_TARGET)/$(OBS_PACKAGE)

.PHONY: all local obs check build-clean build-init

#-----------------------
# Primary make targets
#-----------------------

all: local

# Builds the RPM on your local machine using the OBS infrstructure.
# This is useful to test before submitting to OBS.
local: check
	make build-init
	cd OBS/$(OBS_WORKDIR) && osc build --clean --noverify --disable-debuginfo
	make build-clean

# Commits local file changes to OBS, and ensures a build is performed.
obs: check
	make build-init
	cd OBS/$(OBS_WORKDIR) && osc addremove -r 2> /dev/null || exit 0
	cd OBS/$(OBS_WORKDIR) && osc ci -m "Makefile check-in - date($(shell date)) branch($(GIT_BRANCH))"
	make build-clean

# If you're having a build failure, and you need to manually intervene.
# This will drop you into a shell within the build environment
# TODO: Finish writing chroot target so that it looks up current centos and arch using
#       osc tool
chroot: check
	@echo -e "\nERROR: This is still being worked on.  Please don't use.\n"
	@exit 1
	make build-init
	cd OBS/$(OBS_WORKDIR) && osc chroot --local-package -o CentOS_6.5_standard x86_64 mod_ruid2
	make build-clean

# Debug target: Prints out variables to ensure they're correct
vars: check
	@echo "OBS_USERNAME: $(OBS_USERNAME)"
	@echo "GIT_BRANCH: $(GIT_BRANCH)"
	@echo "BUILD_TARGET: $(BUILD_TARGET)"
	@echo "OBS_WORKDIR: $(OBS_WORKDIR)"
	@echo "OBS_PROJECT: $(OBS_PROJECT)"
	@echo "OBS_PACKAGE: $(OBS_PACKAGE)"

#-----------------------
# Helper make targets
#-----------------------

build-init: build-clean
	mkdir OBS
	osc branch $(OBS_PROJECT) $(OBS_PACKAGE) $(BUILD_TARGET) $(OBS_PACKAGE) 2>/dev/null || exit 0
	cd OBS && osc co $(BUILD_TARGET)
	mv OBS/$(OBS_WORKDIR)/.osc OBS/.osc.proj.$$ && rm -rf OBS/$(OBS_WORKDIR)/* && cp --remove-destination -pr SOURCES/* SPECS/* OBS/$(OBS_WORKDIR) && mv OBS/.osc.proj.$$ OBS/$(OBS_WORKDIR)/.osc

build-clean:
	rm -rf OBS

# place PATH before this because cpanel overrides python location
rpmlint:
	@PATH=/bin:/usr/bin rpmlint SPECS/*.spec

check:
	@[ -e ~/.oscrc ] || make errmsg
	@[ -x /usr/bin/osc ] || make errmsg
	@[ -x /usr/bin/build ] || make errmsg
	@[ -d .git ] || ERRMSG="This isn't a git repository." make -e errmsg

errmsg:
	@echo -e "\nERROR: You haven't set up OBS correctly on your machine.\n $(ERRMSG)\n"
	@exit 1
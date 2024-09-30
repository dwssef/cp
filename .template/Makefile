# +--------------------+
# |                    |
# |   GENERAL CONFIG   |
# |                    |
# +--------------------+

# PROBLEM_NAME := problem_name
PROBLEM_NAME := $(basename $(notdir $(shell ls *.cpp 2>/dev/null | head -n 1)))

DEBUG := true
LANG := cpp

ifeq ($(LANG),cpp)
TARGET := $(PROBLEM_NAME)
EXECUTE := ./$(TARGET)
CLEAN_TARGETS := $(TARGET)
else ifeq ($(LANG),python)
TARGET := $(PROBLEM_NAME).py
EXECUTE := python3 ./$(TARGET)
CLEAN_TARGETS :=
else
$(error "Unknown language; please set TARGET, EXECUTE, and CLEAN_TARGETS manually")
endif

CXX := g++
CXXFLAGS := -std=c++17 -Wall -Wshadow -Wno-unused-result -pipe
DEBUG_CXXFLAGS := -g -fsanitize=signed-integer-overflow,undefined

ifeq ($(DEBUG),true)
CXXFLAGS += $(DEBUG_CXXFLAGS)
endif

PRECOMPILE_HEADERS := bits/stdc++.h

# +-------------------+
# |                   |
# |   GENERAL RULES   |
# |                   |
# +-------------------+

all: $(TARGET)
.PHONY: all

clean:
	-rm -rf $(CLEAN_TARGETS)
.PHONY: clean

veryclean:
	-rm -rf $(CLEAN_TARGETS) *.res
.PHONY: veryclean

rebuild: clean all
.PHONY: rebuild

# +---------------------+
# |                     |
# |   C++ COMPILATION   |
# |                     |
# +---------------------+

PCH := .precompiled_headers
CLEAN_TARGETS += $(PCH)

$(PCH)/%.gch:
	rm -f $@
	mkdir -p $(dir $@)
	$(LINK.cpp) -x c++-header "$$(echo '#include<$*>' | $(LINK.cpp) -H -E -x c++ - 2>&1 >/dev/null | head -1 | cut -d ' ' -f2)" -o $@
.PRECIOUS: $(PCH)/%.gch

# Compile rule
%: %.cpp $(patsubst %,$(PCH)/%.gch,$(PRECOMPILE_HEADERS))
	$(CXX) $(CXXFLAGS) $< -o $@
.PRECIOUS: %

# +-----------------------+
# |                       |
# |   RUNNING / TESTING   |
# |                       |
# +-----------------------+

export TIME=\n  real\t%es\n  user\t%Us\n  sys\t%Ss\n  mem\t%MKB

run: $(TARGET)
	\time $(EXECUTE)
ifeq ($(DEBUG),true)
	@echo "Built with DEBUG flags enabled, code may be slower than normal"
endif
.PHONY: run

%.res: $(TARGET) %.in
	\time $(EXECUTE) < $*.in > $*.res
ifeq ($(DEBUG),true)
	@echo "Built with DEBUG flags enabled, code may be slower than normal"
endif
.PRECIOUS: %.res

%.out: % # Cancel the builtin rule

__test_%: %.res %.out
	diff $*.res $*.out
.PHONY: __test_% 

CASES := $(sort $(basename $(wildcard *.in)))
TESTS := $(sort $(basename $(wildcard *.out)))

runs: $(patsubst %,%.res,$(CASES))
.PHONY: run

solve: runs
.PHONY: solve

test: $(patsubst %,__test_%,$(TESTS))
.PHONY: test


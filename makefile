CXX = g++
CXXFLAGS = -Wall -g

TARGET = program

SRC = $(wildcard *.cpp)

build: $(SRC)
	$(CXX) $(CXXFLAGS) -o $(TARGET) $(SRC)

run: build
	./$(TARGET)

clean:
	rm -f $(TARGET)

.PHONY: build run clean

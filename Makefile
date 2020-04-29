all: clean
	./generate.py
clean:
	rm -rf .build

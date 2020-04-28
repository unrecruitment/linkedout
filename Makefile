all: clean
	./process.py
clean:
	rm -rf .build

all: clean
	./generate.py
	ln -s ../../overlay/style.css .build/static/
httpserver: all
	python3 -m http.server --directory .build/static/
clean:
	rm -rf .build

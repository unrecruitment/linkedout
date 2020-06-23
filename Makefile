all: clean
	./generate.py
	ln -s ../../overlay/style.css build_dir/static/
httpserver: all
	python3 -m http.server --directory build_dir/static/
clean:
	rm -rf build_dir

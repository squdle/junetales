all:
	python main.py -a -H ./examples/*.txt > ./html/index.html 
preview:
	python main.py -a -H ./examples/*.txt > ./html/index.html
	xdg-open ./html/index.html
clean:
	rm ./html/index.html

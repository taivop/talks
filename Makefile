render:
	~/mambaforge/bin/python make_readme.py

view:
	pandoc -f markdown README.md > index.html && open index.html

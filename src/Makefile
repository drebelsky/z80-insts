insts.json: insts.txt parse.py
	python3 parse.py insts.txt > insts.json

insts.txt: extract.py um0080.pdf
	python3 extract.py > insts.txt

um0080.pdf:
	wget "https://www.zilog.com/docs/z80/um0080.pdf"

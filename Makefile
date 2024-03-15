all:
	echo "Nothing here yet."

.PHONY: dev
dev:
	rm -rf .venv
	python3.11 -m venv .venv --upgrade-deps
	.venv/bin/pip3 install -r requirements.txt
	echo "run 'source .venv/bin/activate' to activate the venv"

.PHONY: run
run:
	streamlit run streamlit_core.py

.PHONY: bin
bin:
	gcc ./test/echo_input.c -o ./test/myBinary
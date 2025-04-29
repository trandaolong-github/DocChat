.PHONY: env clean fe be

env:
	python3 -m venv env
	. env/bin/activate && \
	pip install --upgrade pip && \
	pip install -r requirements.txt

clean:
	rm -rf env/

fe: env
	mkdir -p database uploaded_docs
	. env/bin/activate && streamlit run src/rag_fe/main.py

be: env
	# . env/bin/activate && uvicorn src.rag_api.main:app --reload
	mkdir -p database uploaded_docs
	. env/bin/activate && fastapi run src/rag_api/main.py

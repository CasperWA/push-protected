FROM python:3.8

COPY README.md setup.py ./
COPY push_action ./push_action
RUN pip install -e .

RUN apt-get update && apt-get install uuid-runtime

COPY entrypoint.sh ./
ENTRYPOINT [ "/entrypoint.sh" ]

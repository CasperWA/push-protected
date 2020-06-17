FROM python:3.8

COPY README.md setup.py ./
COPY push_action ./app

COPY entrypoint.sh ./
ENTRYPOINT [ "/entrypoint.sh" ]

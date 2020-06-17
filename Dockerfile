FROM python:3.8

COPY README.md setup.py ./
COPY push_action ./push_action
RUN pip install -e .

COPY entrypoint.sh ./
ENTRYPOINT [ "/entrypoint.sh" ]

FROM python:3.8

COPY README.md setup.py requirements*.txt ./
COPY push_action ./push_action
RUN pip install -U -e .

COPY entrypoint.sh ./
ENTRYPOINT [ "/entrypoint.sh" ]

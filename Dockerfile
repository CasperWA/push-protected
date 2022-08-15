FROM python:alpine

COPY README.md setup.py requirements*.txt ./
COPY push_action ./push_action

RUN apk update \
    && apk add --no-cache git git-lfs bash \
    && pip install -U -e .

COPY entrypoint.sh ./
ENTRYPOINT [ "/entrypoint.sh" ]

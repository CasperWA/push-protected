FROM python:3.12-alpine

COPY LICENSE README.md pyproject.toml ./
COPY push_action ./push_action

RUN apk update \
    && apk add --no-cache git git-lfs bash \
    && pip install -U -e .

COPY entrypoint.sh ./
ENTRYPOINT [ "/entrypoint.sh" ]

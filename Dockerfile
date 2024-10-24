FROM python:3.11
RUN apt-get clean && apt-get update && \
    apt-get install -y --no-install-recommends \
           postgresql-client-common \
           postgresql-client \
           netcat-traditional \
           gosu

WORKDIR /app
COPY project/requirements /app/project/requirements
RUN pip install -r project/requirements/remote.txt --src=/pip-repos

COPY . /app

RUN git describe --tags --always > PROJECT_VERSION && \
    date --iso-8601=seconds > PROJECT_BUILD_DATE && \
    git rev-parse HEAD > PROJECT_COMMIT_HASH && \
    rm -rf .git

EXPOSE 3030

ENV PATH="/app/docker/remote/bin:${PATH}"

ENTRYPOINT ["/app/docker/remote/entrypoint.sh"]
CMD ["django"]

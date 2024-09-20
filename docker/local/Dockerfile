FROM python:3.11
RUN apt-get clean && apt-get update && \
    apt-get install -y --no-install-recommends \
           postgresql-client-common \
           postgresql-client \
           netcat-traditional \
           gosu

WORKDIR /app
COPY project/requirements /app/project/requirements
RUN pip install -r project/requirements/local.txt --src=/pip-repos

COPY . /app

EXPOSE 8000

ENV PATH="/app/docker/local/bin:${PATH}"

ENTRYPOINT ["/app/docker/local/entrypoint.sh"]
CMD ["django"]

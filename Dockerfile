FROM python:3.12-slim

RUN apt update && apt install -y curl git && curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin v0.56.2

RUN apt-get update && apt-get install -y awscli

RUN trivy image --download-db-only --db-repository public.ecr.aws/aquasecurity/trivy-db:2

RUN trivy plugin install github.com/aquasecurity/trivy-aws

COPY requirements.txt /agent/requirements.txt

RUN pip install -r /agent/requirements.txt

ENV PYTHONPATH=/agent

WORKDIR /agent

COPY . /agent

COPY .chainlit /agent/.chainlit

ENV TIKTOKEN_CACHE_DIR=/agent/cache

CMD ["/agent/scripts/entrypoint.sh"]

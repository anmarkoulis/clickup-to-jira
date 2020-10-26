FROM python:3.8-slim-buster

# Requirements are installed here to ensure they will be cached.
COPY ./ /opt/clickup_to_jira
# All imports needed for autodoc.

WORKDIR /opt/clickup_to_jira
RUN python setup.py install
RUN rm -rf /opt/clickup_to_jira
ENTRYPOINT ["run.py"]

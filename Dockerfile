FROM public.ecr.aws/docker/library/python:3.11.0-slim-bullseye
COPY --from=public.ecr.aws/awsguru/aws-lambda-adapter:0.7.1 /lambda-adapter /opt/extensions/lambda-adapter

ARG VAR1
#ARG VAR2

ENV OPENAI_API_KEY=$VAR1
#ENV PINECONE_API_KEY=$VAR2
ENV AWS_LWA_INVOKE_MODE=buffered

WORKDIR /app
ADD . .

RUN pip install -r requirements.txt

# run server
CMD ["python", "server_fast_api.py"]
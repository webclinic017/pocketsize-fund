FROM public.ecr.aws/lambda/python:3.10-arm64

ARG FUNCTION_NAME

COPY requirements.txt ${LAMBDA_TASK_ROOT}

COPY pkg ${LAMBDA_TASK_ROOT}/pkg

COPY cmd/lambda/${FUNCTION_NAME}/main.py ${LAMBDA_TASK_ROOT}

RUN yum update -y && yum install -y libxml2-devel libxslt-devel gcc

RUN pip3 install --requirement requirements.txt --target "${LAMBDA_TASK_ROOT}"

ENV S3_DATA_BUCKET_NAME=""

ENV ALPACA_API_KEY=""

ENV ALPACA_API_SECRET=""

ENV DARQUBE_API_KEY=""

ENV ALPHA_VANTAGE_API_KEY=""

ENV MODEL_FILE_PATH=""

ENV IS_PAPER=""

ENV SNS_ERRORS_TOPIC_ARN=""

ENV INVITE_SECRET_KEY=""

ENV INVITE_BASE_URL=""

ENV ALPACA_OAUTH_CLIENT_ID=""

ENV ALPACA_OAUTH_CLIENT_SECRET=""

ENV USERS_TABLE_NAME=""

ENV MODEL_ENDPOINT_NAME=""

CMD [ "main.handler" ]

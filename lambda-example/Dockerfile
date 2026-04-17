# AWS Lambda Python 3.12 base image
FROM public.ecr.aws/lambda/python:3.12

# Copy and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir

# Copy the handler
COPY lambda_function.py .

# Lambda entry point: <module>.<function>
CMD ["lambda_function.handler"]

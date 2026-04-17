import base64
import subprocess

import boto3


def get_or_create_repository(repository_name: str, region: str) -> str:
    """
    Return the URI of an ECR repository, creating it if it doesn't exist yet.
    """
    ecr = boto3.client("ecr", region_name=region)
    try:
        response = ecr.describe_repositories(repositoryNames=[repository_name])
        uri = response["repositories"][0]["repositoryUri"]
        print(f"Repository already exists: {uri}")
        return uri
    except ecr.exceptions.RepositoryNotFoundException:
        response = ecr.create_repository(
            repositoryName=repository_name,
            imageScanningConfiguration={"scanOnPush": True},
        )
        uri = response["repository"]["repositoryUri"]
        print(f"Repository created: {uri}")
        return uri


def build_image(local_tag: str) -> None:
    """
    Build a Docker image from the Dockerfile in the current directory.
    The --platform flag targets the Lambda execution environment (linux/amd64).
    """
    print(f"Building image '{local_tag}' ...")
    subprocess.run(
        [
            "docker", "build", 
            "--platform", "linux/amd64", 
            "--provenance=false",  
            "-t", local_tag, 
            "."
        ],
        check=True,
    )
    print("Build complete.")


def push_image(repository_uri: str, local_tag: str, region: str) -> str:
    """
    Authenticate with ECR, tag the local image, push it, and return the full image URI.
    """
    ecr = boto3.client("ecr", region_name=region)

    # Retrieve short-lived ECR credentials
    token_data = ecr.get_authorization_token()
    auth = token_data["authorizationData"][0]
    username, password = (
        base64.b64decode(auth["authorizationToken"]).decode().split(":", 1)
    )
    registry = auth["proxyEndpoint"]

    print(f"Logging in to ECR registry {registry} ...")
    subprocess.run(
        ["docker", "login", "--username", username, "--password-stdin", registry],
        input=password.encode(),
        check=True,
    )

    full_uri = f"{repository_uri}:latest"

    print(f"Tagging '{local_tag}' -> '{full_uri}' ...")
    subprocess.run(["docker", "tag", local_tag, full_uri], check=True)

    print(f"Pushing '{full_uri}' ...")
    subprocess.run(["docker", "push", full_uri], check=True)

    print("Push complete.")
    return full_uri


# ─────────────────────────────────────────────────────────────────────────────
# Fill in the variables below, then run:  python ecr_helper.py
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    REPOSITORY_NAME = "lambda-images-xd"   # ECR repository name to create/reuse
    REGION          = "us-east-1"        # AWS region
    LOCAL_IMAGE_TAG = "lambda-example"   # local docker tag used during the build

    repository_uri = get_or_create_repository(REPOSITORY_NAME, REGION)

    build_image(LOCAL_IMAGE_TAG)

    image_uri = push_image(repository_uri, LOCAL_IMAGE_TAG, REGION)
    print(f"\nImage URI (use this in create_lambda.py):\n  {image_uri}")

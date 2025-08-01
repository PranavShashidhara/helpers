import os
import unittest.mock as umock
from typing import Optional

import boto3
import pytest
from botocore.client import BaseClient
from moto import mock_aws

import helpers.haws as haws
import helpers.hunit_test as hunitest


# #############################################################################
# Haws_test_case
# #############################################################################


class Haws_test_case(hunitest.TestCase):

    @pytest.fixture(autouse=True, scope="class")
    def aws_credentials(self) -> None:
        """
        Mocked AWS credentials for moto.
        """
        os.environ["MOCK_AWS_ACCESS_KEY_ID"] = "testing"
        os.environ["MOCK_AWS_SECRET_ACCESS_KEY"] = "testing"
        os.environ["MOCK_AWS_SECURITY_TOKEN"] = "testing"
        os.environ["MOCK_AWS_SESSION_TOKEN"] = "testing"
        os.environ["MOCK_AWS_DEFAULT_REGION"] = "us-east-1"


# #############################################################################
# Test_get_session
# #############################################################################


class Test_get_session(Haws_test_case):

    @pytest.fixture(autouse=True)
    def set_up_test(self) -> None:
        os.environ["MOCK_AWS_S3_BUCKET"] = "mock_aws_bucket"

    @mock_aws
    @umock.patch("boto3.Session")
    def test_get_session1(self, mock_boto3_session: umock.Mock) -> None:
        """
        Test that `haws.get_session` correctly return a session without region
        parameter.
        """
        aws_profile = "__mock__"
        # Create a mock session.
        mock_session = umock.MagicMock()
        mock_boto3_session.return_value = mock_session
        # Test that get_session returns a session object.
        session = haws.get_session(aws_profile)
        self.assertEqual(session, mock_session)
        # Verify that `boto3.Session` was called with the correct profile.
        mock_boto3_session.assert_called_once_with(profile_name=aws_profile)

    @mock_aws
    @umock.patch("boto3.Session")
    def test_get_session2(self, mock_boto3_session: umock.Mock) -> None:
        """
        Test that `haws.get_session` correctly return a session with region
        parameter.
        """
        aws_profile = "__mock__"
        region = "us-east-1"
        # Create a mock session
        mock_session = umock.MagicMock()
        mock_boto3_session.return_value = mock_session
        # Test that `get_session` returns a session object with the specified region.
        session = haws.get_session(aws_profile, region=region)
        self.assertEqual(session, mock_session)
        # Verify that `boto3.Session` was called with the correct profile and region.
        mock_boto3_session.assert_called_once_with(
            profile_name=aws_profile, region_name=region
        )


# #############################################################################
# Test_get_service_client
# #############################################################################


class Test_get_service_client(Haws_test_case):

    @mock_aws
    @umock.patch("helpers.haws.get_session")
    def test1(self, mock_get_session: umock.Mock) -> None:
        """
        Test `haws.get_service_client()` returns a client for S3.
        """
        aws_profile = "__mock__"
        service_name = "s3"
        region = "us-east-1"
        # Create a mock session with the expected credentials.
        mock_session = boto3.session.Session(
            aws_access_key_id="testing",
            aws_secret_access_key="testing",
            region_name=region,
        )
        mock_get_session.return_value = mock_session
        # Create mock client for S3.
        client = haws.get_service_client(
            aws_profile=aws_profile, service_name=service_name, region=region
        )
        # Check that the returned client is for the S3 service.
        self.assert_equal(client.meta.service_model.service_name, "s3")
        # Check for region.
        self.assert_equal(client.meta.region_name, region)


# #############################################################################
# Test_get_service_resource
# #############################################################################


class Test_get_service_resource(Haws_test_case):

    @mock_aws
    @umock.patch("helpers.haws.get_session")
    def test1(self, mock_get_session: umock.Mock) -> None:
        """
        Test that `haws.get_service_resource()` correctly retrieves a S3
        resource.
        """
        aws_profile = "__mock__"
        service_name = "s3"
        # Create a mock session with the expected credentials.
        mock_session = boto3.session.Session(
            aws_access_key_id="testing",
            aws_secret_access_key="testing",
            region_name="us-east-1",
        )
        mock_get_session.return_value = mock_session
        # Create mock S3 bucket.
        s3 = boto3.resource("s3")
        s3.create_bucket(Bucket="my-test-bucket")
        s3_resource = haws.get_service_resource(
            aws_profile=aws_profile, service_name=service_name
        )
        # Get all `S3` buckets.
        buckets = list(s3_resource.buckets.all())
        bucket_names = [bucket.name for bucket in buckets]
        # Check.
        self.assertIn("my-test-bucket", bucket_names)


# #############################################################################
# Test_get_task_definition_image_url
# #############################################################################


class Test_get_task_definition_image_url(Haws_test_case):

    @mock_aws
    @umock.patch("helpers.haws.get_service_client")
    def test1(self, mock_get_service_client: umock.Mock) -> None:
        """
        Test that `get_task_definition_image_url` retrieves correct image URL.
        """
        # Mock data.
        task_definition_name = "my-task-definition"
        mock_image_url = "old_image_url"
        region = "us-east-1"
        # Mock the return value of `get_service_client`.
        mock_client = boto3.client("ecs", region_name=region)
        mock_get_service_client.return_value = mock_client
        # Create a mock task definition.
        mock_client.register_task_definition(
            family=task_definition_name,
            # The following are required parameters.
            containerDefinitions=[
                {"name": "my-container", "image": mock_image_url, "memory": 512}
            ],
        )
        image_url = haws.get_task_definition_image_url(task_definition_name)
        self.assertEqual(image_url, mock_image_url)


# #############################################################################
# Test_update_task_definition
# #############################################################################


class Test_update_task_definition(Haws_test_case):

    @mock_aws
    @umock.patch("helpers.haws.get_ecs_client")
    def test1(self, mock_get_ecs_client: BaseClient) -> None:
        """
        Test updating a task definition with a new image URL.
        """
        # Mock data.
        task_definition_name = "my-task-definition"
        old_image_url = "old_image_url"
        new_image_url = "new_image_url"
        region = "us-east-1"
        # Mock the return value of `get_ecs_client`.
        mock_client = boto3.client("ecs", region_name=region)
        mock_get_ecs_client.return_value = mock_client
        # Create a mock task definition.
        mock_client.register_task_definition(
            family=task_definition_name,
            containerDefinitions=[
                {"name": "my-container", "image": old_image_url}
            ],
            executionRoleArn="__mock__",
            networkMode="bridge",
            requiresCompatibilities=["EC2"],
            cpu="256",
            memory="512",
        )
        # Update task definition.
        haws.update_task_definition(
            task_definition_name, new_image_url, region=region
        )
        # Check if the task definition is updated.
        task_description = mock_client.describe_task_definition(
            taskDefinition=task_definition_name
        )
        updated_image_url = task_description["taskDefinition"][
            "containerDefinitions"
        ][0]["image"]
        self.assertEqual(updated_image_url, new_image_url)


# #############################################################################
# Test_get_ecs_client
# #############################################################################


class Test_get_ecs_client(Haws_test_case):

    def mock_aws_client(
        self, mock_get_session: umock.Mock, *, region: Optional[str] = None
    ) -> None:
        aws_profile = "__mock__"
        test_cluster_name = "test-cluster"
        # Create a mock session with the expected credentials.
        mock_session = boto3.session.Session(
            aws_access_key_id="testing",
            aws_secret_access_key="testing",
            region_name=region or "us-east-1",
        )
        mock_get_session.return_value = mock_session
        # Create mock ECS client.
        ecs_client = boto3.client("ecs", region_name="us-east-1")
        ecs_client.create_cluster(clusterName=test_cluster_name)
        # Get ECS client.
        if region:
            test_client = haws.get_ecs_client(aws_profile, region=region)
        else:
            test_client = haws.get_ecs_client(aws_profile)
        # Get the created cluster.
        cluster_name = test_client.list_clusters()["clusterArns"][0]
        # Check cluster name.
        self.assertIn(test_cluster_name, cluster_name)

    @mock_aws
    @umock.patch("helpers.haws.get_session")
    def test1(self, mock_get_session: umock.Mock) -> None:
        """
        Test that `haws.get_ecs_client()` correctly return a client to work
        with ECS within a specified region.
        """
        self.mock_aws_client(mock_get_session, region="us-east-1")

    @mock_aws
    @umock.patch("helpers.haws.get_session")
    def test2(self, mock_get_session: umock.Mock) -> None:
        """
        Test that `haws.get_ecs_client()` correctly return a client to work
        with ECS without a specified region.
        """
        self.mock_aws_client(mock_get_session)

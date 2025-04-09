import pytest
from unittest import mock
from food_detection import FoodDetector
from clarifai_grpc.grpc.api import service_pb2
from clarifai_grpc.grpc.api.status import status_code_pb2
from unittest.mock import patch, MagicMock
import base64
from food_detection import FoodDetector

@pytest.fixture
def food_detector():
    # Create an instance of the FoodDetector class for use in tests
    return FoodDetector()

# Mock responses for the stub's method
def mock_post_model_outputs(request, metadata=None):
    # Create a mock response with fake data
    response = service_pb2.PostModelOutputsResponse(
        status=service_pb2.Status(code=status_code_pb2.SUCCESS),
        outputs=[
            service_pb2.Output(
                data=service_pb2.Data(
                    concepts=[
                        service_pb2.Concept(name="apple", value=0.95),
                        service_pb2.Concept(name="banana", value=0.75),
                        service_pb2.Concept(name="carrot", value=0.05),  # Below threshold
                    ]
                )
            )
        ]
    )
    return response

@patch('clarifai_grpc.grpc.api.service_pb2_grpc.V2Stub')
def test_detect_food_success(mock_v2_stub):
    # Setup the mock stub instance and its method
    mock_stub_instance = MagicMock()
    mock_v2_stub.return_value = mock_stub_instance

    mock_response = MagicMock()
    mock_response.status.code = 10000  # SUCCESS
    mock_concept = MagicMock()
    mock_concept.name = "pizza"
    mock_concept.value = 0.95
    mock_response.outputs = [MagicMock(data=MagicMock(concepts=[mock_concept]))]

    mock_stub_instance.PostModelOutputs.return_value = mock_response

    detector = FoodDetector()
    dummy_image = base64.b64encode(b"fake image data").decode("utf-8")
    status, foods = detector.detect_food(dummy_image)

    assert status == "Success"
    assert foods == ["pizza"]

# Unit test for failure when Clarifai API returns a non-success status
def mock_post_model_outputs_fail(request, metadata=None):
    # Create a mock response with a failure status
    response = service_pb2.PostModelOutputsResponse(
        status=service_pb2.Status(code=status_code_pb2.FAILED),
        outputs=[]
    )
    return response

@patch('clarifai_grpc.grpc.api.service_pb2_grpc.V2Stub')
def test_detect_food_failure(mock_v2_stub):
    mock_stub_instance = MagicMock()
    mock_v2_stub.return_value = mock_stub_instance

    mock_response = MagicMock()
    mock_response.status.code = 400  # Simulated failure code
    mock_response.outputs = []

    mock_stub_instance.PostModelOutputs.return_value = mock_response

    detector = FoodDetector()
    dummy_image = base64.b64encode(b"fake image data").decode("utf-8")
    status, foods = detector.detect_food(dummy_image)

    assert status == "Fail"
    assert foods == []

@patch('clarifai_grpc.grpc.api.service_pb2_grpc.V2Stub')
def test_detect_food_exception(mock_v2_stub):
    mock_stub_instance = MagicMock()
    mock_v2_stub.return_value = mock_stub_instance

    # Raise an exception when PostModelOutputs is called
    mock_stub_instance.PostModelOutputs.side_effect = Exception("Simulated API failure")

    detector = FoodDetector()
    dummy_image = base64.b64encode(b"fake image data").decode("utf-8")
    status, foods = detector.detect_food(dummy_image)

    assert status == "Fail"
    assert foods == []

from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
from clarifai_grpc.grpc.api import resources_pb2, service_pb2, service_pb2_grpc
from clarifai_grpc.grpc.api.status import status_code_pb2
from dotenv import load_dotenv, dotenv_values
import os 
import base64

class FoodDetector:
    def __init__(self):
        """
        Initialize the food detector with model data
        """
        load_dotenv()
        self.USER_ID = 'clarifai'
        self.APP_ID = 'main'
        self.MODEL_ID = 'food-item-recognition'
        self.MODEL_VERSION_ID = '1d5fd481e0cf4826aa72ec3ff049e044'
        self.foods = []
        self.PAT = os.getenv("CLARIFAI_API_KEY")
        if not self.PAT:
            raise ValueError("CLARIFAI_API_KEY is not set in the environment variables.")

    def detect_food(self, image):
        """
        Detect foods in the given image

        Args:
            image: image bytes (may need to be changed)

        Returns:
            list: List of foods detected in image with probabilities over threshold
        """
        

        try:
            channel = ClarifaiChannel.get_grpc_channel()
            stub = service_pb2_grpc.V2Stub(channel)
            # Decode image

            image = base64.b64decode(image)
            print(f"Decoded image length: {len(image)}")

            metadata = (('authorization', 'Key ' + self.PAT),)

            userDataObject = resources_pb2.UserAppIDSet(user_id=self.USER_ID, app_id=self.APP_ID)

            post_model_outputs_response = stub.PostModelOutputs(
                service_pb2.PostModelOutputsRequest(
                    user_app_id=userDataObject, 
                    model_id=self.MODEL_ID,
                    version_id=self.MODEL_VERSION_ID, 
                    inputs=[resources_pb2.Input(
                        data=resources_pb2.Data(
                            image=resources_pb2.Image(
                                base64=image
                            )
                        )
                    )]
                ),
                metadata=metadata
            )

            if post_model_outputs_response.status.code != status_code_pb2.SUCCESS:
                print(f"Error in response: {post_model_outputs_response.status.code}")
                return ('Fail', self.foods)

            output = post_model_outputs_response.outputs[0]
            print("Clarifai response received:", output)

            threshold = 0.1
            self.foods = []  # Clear any old results
            for concept in output.data.concepts:
                if concept.value > threshold:
                    self.foods.append(concept.name)  # Append, not extend

            return ('Success', self.foods)

        except Exception as e:
            print(f"Error in detect_food: {e}")
            return ('Fail', self.foods)


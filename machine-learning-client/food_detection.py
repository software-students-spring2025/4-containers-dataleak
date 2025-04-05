from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
from clarifai_grpc.grpc.api import resources_pb2, service_pb2, service_pb2_grpc
from clarifai_grpc.grpc.api.status import status_code_pb2

class FoodDetector:
    def __init__(self):
        """
        Initialize the food detector with model data
        """
        self.USER_ID = 'clarifai'
        self.APP_ID = 'main'
        self.MODEL_ID = 'food-item-recognition'
        self.MODEL_VERSION_ID = '1d5fd481e0cf4826aa72ec3ff049e044'
        self.foods = []
        self.PAT = '' #replace with PAT

    def detect_food(self, image):
        """
        Detect foods in the given image

        Args:
            image: image url (may need to be changed)

        Returns:
            list: List of foods detected in image with probabilities over threshold
        """
        channel = ClarifaiChannel.get_grpc_channel()
        stub = service_pb2_grpc.V2Stub(channel)

        metadata = (('authorization', 'Key ' + self.PAT),)

        userDataObject = resources_pb2.UserAppIDSet(user_id=self.USER_ID, app_id=self.APP_ID)

        post_model_outputs_response = stub.PostModelOutputs(
            service_pb2.PostModelOutputsRequest(
                user_app_id=userDataObject, 
                model_id=self.MODEL_ID,
                version_id=self.MODEL_VERSION_ID, 
                inputs=[
                    resources_pb2.Input(
                        data=resources_pb2.Data(
                            image=resources_pb2.Image(
                                url=image
                            )
                        )
                    )
                ]
            ),
            metadata=metadata
        )
        if post_model_outputs_response.status.code != status_code_pb2.SUCCESS:
            return self.foods

        output = post_model_outputs_response.outputs[0]

        threshold = 0.80

        for concept in output.data.concepts:
            if concept.value > threshold:
                self.foods.extend([concept.name])

        print(self.foods)
        return self.foods


"""
#Test example:
instance = FoodDetector()
instance.detect_food('https://media.istockphoto.com/id/1189709277/photo/pasta-penne-with-roasted-tomato-sauce-mozzarella-cheese-grey-stone-background-top-view.jpg?s=612x612&w=0&k=20&c=5ro7Cvwx79tWpyN1r2hy3DwplFi5FuPrD_4DYD8tZpg=')
"""
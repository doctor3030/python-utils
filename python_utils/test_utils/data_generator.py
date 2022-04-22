import json
import uuid


class Message:

    def __init__(self, value):
        self.value = value


class DataGenerator:

    def __init__(self, data_path, source):
        self.data_path = data_path
        self.source = source
        # self.__iter__ = getattr(self, source)
        # print(self.__iter__)

    def __iter__(self):
        for i in getattr(self, self.source)():
            yield i

    def ap_crawler_to_nlp(self):
        with open(self.data_path, 'r') as f:
            data = json.load(f)

        service_id = str(uuid.uuid4())
        for obj in data:
            obj['data_collected'] = "1"
            obj['text_id'] = str(uuid.uuid4())

            msg = Message({
                "service": "ap_crawler",
                "service_id": service_id,
                "message": obj
            })

            yield msg

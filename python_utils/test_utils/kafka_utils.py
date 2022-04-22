import sys
# from kafka import KafkaProducer, KafkaConsumer
# from collections import deque
# from unittest.mock import MagicMock


class Moc_KafkaProducer:

    def send(self, topic, value):
        pass

    def flush(self):
        pass

    def close(self):
        pass


class Moc_KafkaConsumer:

    def __init__(self, data_generator, **kwargs):
        # super().__init__()
        try:
            self.data_generator = data_generator
            self.poll_batches = False

            poll_batches = kwargs.get('poll_batches')
            if poll_batches is not None:
                self.poll_batches = poll_batches

            if poll_batches:
                n_partitions = kwargs.get('n_partitions')
                if n_partitions is None: raise AttributeError('"n_partitions" is not defined.')
                self.n_partitions = n_partitions

                batch_size = kwargs.get('batch_size')
                if batch_size is None: raise AttributeError('"batch_size" is not defined.')
                self.batch_size = batch_size

        except Exception as e:
            print(e, file=sys.stderr)

    def poll(self):
        if self.poll_batches:
            batch = {}
            for np in range(self.n_partitions):
                partition_batch = []
                while len(partition_batch) < self.batch_size:
                    partition_batch.append({"value": next(self.data_generator)})
                batch['partition_{}'.format(np)] = partition_batch

            return batch

        else:
            it = iter(self.data_generator)
            return {"partition_1": [next(it)]}

    def commit(self):
        pass

    def close(self):
        pass

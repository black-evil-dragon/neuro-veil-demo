from keras.models import Sequential




class InterfaceModel:

    def __str__(self):
        return ''


    def __init__(self):
        super().__init__()

        self.name = ''


    def build_model(self, input_shape: tuple) -> 'Sequential':
        raise NotImplementedError('build_model() method is not implemented!')
    

    @staticmethod
    def get_model_default(model: 'Sequential', input_shape: tuple):
        raise NotImplementedError('get_model_default() method is not implemented!')
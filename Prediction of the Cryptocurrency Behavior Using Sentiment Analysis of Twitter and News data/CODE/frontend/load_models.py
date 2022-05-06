import pickle


class LoadModels:

    def __init__(self):
        self.coin_names = ['Bitcoin', 'Litecoin',
                           'Ethereum', 'Dogecoin', 'XRP']
        self.file_path = 'pickle/'
        self.models = {}

    def _build_file_path(self, coin_name):
        return self.file_path + coin_name + '.sav'

    def save_model(self, model, coin_name):
        if coin_name not in self.coin_names:
            raise Exception(
                "Provided coin name must be from lis: ", self.coin_names)
        pickle.dump(model, open(self._build_file_path(coin_name), 'wb'))

    def load(self):
        # load all models from disk
        for coin_name in self.coin_names:
            loaded_model = pickle.load(
                open(self._build_file_path(coin_name), 'rb'))
            self.models[coin_name] = loaded_model

    def get_model_for_coin(self, coin_name):
        if coin_name not in self.coin_names:
            raise Exception(
                "Provided coin name must be from lis: ", self.coin_names)
        return self.models[coin_name]

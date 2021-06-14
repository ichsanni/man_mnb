import copy

class KFoldCrossValidation():
    def __init__(self, data, fold=10):
        self.folds = fold
        self.data = data
        self.index = int(len(self.data) / self.folds)

    def fold(self):
        # BAGI DATA JADI BEBERAPA FOLDS
        f = []
        for x in range(self.folds):
            g = []
            
            while len(g) < self.index:
                g.append(self.data.pop(0))
            print(len(g))
            f.append(g)

        # TRAIN TEST SPLIT DARI FOLD
        y = 0
        for x in range(self.folds):
            while y < self.folds:
                print(f"fold-{y}:")
                data_copy = copy.deepcopy(f)
                test = data_copy.pop(y)
                print(len(test))
                train = data_copy
                print(len(train))
                print()
                # TO-BE IMPLEMENTED: naive bayes predictor
                y += 1

import csv, re, copy, random
from collections import Counter
from math import prod, log


class MultinomialNaiveBayes():
    def __init__(self, alpha=1.0):
        '''
        Multinomial Naive Bayes: 

        posterior = prior * likelihood

        P(A|C) = P(C) * P(A1|c) * P(A2|c) * ... * P(An|C)

        untuk mencari probabilitas

        posterior = prior * likelihood / evidence

        P(A|C) = P(C) * P(A1|c) * P(A2|c) * ... * P(An|C) / P(A1|V) * P(A2|V) * ... * P(An|V)
        '''
        # MULTINOMIAL NAIVE BAYES
        self.alpha = alpha
        self.vocab = 0
        self.positif = 0
        self.negatif = 0
        self.word = {}
        self._sent = []
        self.prior_pos = 0
        self.prior_neg = 0
        self.cm = []

    def fit(self, word_dict, freq_dist=False):
        self.word_dict = word_dict
        # HITUNG FREKUENSI KATA PADA KELAS POSITIF DAN NEGATIF DARI DATA LATIH
        for text, sent in self.word_dict:
            self._sent.append(sent)
            for x in text:
                if x not in self.word:
                    self.word[x] = {'positif':0, 'negatif':0}
                self.word[x][sent] += 1
                #### word = {'kata': {'positif':x, 'negatif':x}, 'kata': {'positif':x, 'negatif':x}, dst}
        if freq_dist:
            with open('data/latih/freq_dist.csv', 'w', encoding='utf8', newline='\n') as fr:
                writer = csv.writer(fr)
                for w, s in self.word.items():
                    writer.writerow([w, s['positif'], s['negatif']])

        # HITUNG JUMLAH KATA PADA KELAS POSITIF DAN NEGATIF
        for k,v in self.word.items():
            if k: self.vocab += 1
            self.positif += v['positif']
            self.negatif += v['negatif']

        # HITUNG PROBABILITAS PRIOR
        cc = Counter(self._sent)
        self.prior_pos = cc['positif'] / (cc['positif'] + cc['negatif'])
        self.prior_neg = cc['negatif'] / (cc['positif'] + cc['negatif'])

    def predict(self, pred):
        predicted_sent = []
        for arr in pred:
            likelihood_pos = []
            likelihood_neg = []
            fr_pos = 0
            fr_neg = 0
            for kata in arr:
                if kata in self.word.keys():
                    fr_pos = self.word[kata]['positif']
                    fr_neg = self.word[kata]['negatif']

                # LIKELIHOOD DENGAN LAPLACE SMOOTHING
                # (kata + 1) / (jumlah kata positif + jumlah vocabulary)
                _word_pos = log((fr_pos + self.alpha) / (self.positif + self.vocab))
                _word_neg = log((fr_neg + self.alpha) / (self.negatif + self.vocab))
                likelihood_pos.append(_word_pos)
                likelihood_neg.append(_word_neg)

            # MULTINOMIAL NAIVE BAYES
            sent_pos = log(self.prior_pos) + sum(likelihood_pos)
            sent_neg = log(self.prior_neg) + sum(likelihood_neg)
            predicted_sent.append('positif') if sent_pos > sent_neg else predicted_sent.append('negatif')

        return predicted_sent

    def predict_prob(self, pred):
        pred_pos = []
        pred_neg = []
        for arr in pred:
            likelihood_pos = []
            likelihood_neg = []
            evidence = []
            fr_pos = 0
            fr_neg = 0
            for kata in arr:
                if kata in self.word.keys():
                    fr_pos = self.word[kata]['positif']
                    fr_neg = self.word[kata]['negatif']

                # LIKELIHOOD DENGAN LAPLACE SMOOTHING
                # (kata + 1) / (jumlah kata positif + jumlah vocabulary)
                _word_pos = (fr_pos + self.alpha) / (self.positif + self.vocab)
                _word_neg = (fr_neg + self.alpha) / (self.negatif + self.vocab)
                likelihood_pos.append(_word_pos)
                likelihood_neg.append(_word_neg)
                # cari evidence kata
                _evid = ((fr_pos + fr_neg) / self.vocab) if (fr_pos | fr_neg) else (2 / self.vocab)
                evidence.append(_evid)
            
            # MULITNOMIAL NAIVE BAYES
            sent_pos = (self.prior_pos * prod(likelihood_pos)) / prod(evidence)
            sent_neg = (self.prior_neg * prod(likelihood_neg)) / prod(evidence)
            
            # NORMALISASI
            _pos = 1 / log(sent_pos)
            _neg = 1 / log(sent_neg)
            
            prob_pos = _pos / (_pos + _neg)
            prob_neg = _neg / (_pos + _neg)

            pred_pos.append(f"{prob_pos:.9f}")
            pred_neg.append(f"{prob_neg:.9f}")

        return pred_pos, pred_neg

    def train_test_split(self, z_data, test_data=0.2, seed=42):
        raw = [[tw, x, y] for tw, x, y in z_data]
        test_data *= 100
        self.splits = test_data / 100 * len(raw)
        self.word = {}
        
        # ACAK DATA
        random.seed(seed)
        random.shuffle(raw)

        # BAGI DATA BERDASARKAN PERBANDINGAN DATA TRAINING DAN TESTING
        _test = []
        while len(_test) < self.splits:
            _test.append(raw.pop(0))
        _pred = []
        _sent = []
        _ori_tw = []
        for ori, tknz, sntm in _test:
            _ori_tw.append(ori)
            _pred.append(tknz)
            _sent.append(sntm)
        
        # TRAINING DAN TESTING
        train = [[x,y] for tw, x, y in raw]
        self.fit(train, freq_dist=True)
        prediction = self.predict(_pred)
        pred_pos, pred_neg = self.predict_prob(_pred)

        # SIMPAN DATA TRAINING DAN HASIL TESTING
        with open(f'data/latih/split_train.csv', 'w', newline='\n', encoding='utf8') as train:
            writer = csv.writer(train)
            for i in range(len(raw)):
                writer.writerow([raw[i][0], ' '.join(raw[i][1]), raw[i][2]])
        with open(f'data/latih/split_test.csv', 'w', newline='\n', encoding='utf8') as tested:
            writer = csv.writer(tested)
            for i in range(len(_pred)):
                writer.writerow([_ori_tw[i], ' '.join(_pred[i]), _sent[i], 
                                prediction[i], pred_pos[i], pred_neg[i]])

        # HITUNG AKURASI
        _wp = 0
        TP, TN, FP, FN = 0, 0, 0, 0
        for i in range(len(_pred)):
            if _sent[i] != prediction[i]:
                _wp += 1
                if prediction[i] == 'positif' : FP += 1
                else: FN += 1
            else:
                if prediction[i] == 'positif' : TP += 1
                else: TN += 1
        _acc = 100 - (_wp / len(_pred)) * 100 if _wp > 0 else 100
        print([[TP, FN], [FP, TN]])
        self.cm =[[TP, FN], [FP, TN]]
        return _acc

    def kfold_cross_validation(self, data, folds=10, seed=42):
        raw = [[x, y] for x, y in data]
        self.folds = folds
        self.index = int(len(raw) / self.folds)
        accuracy = []

        # ACAK DATA
        random.seed(seed)
        random.shuffle(raw)
        
        # BAGI DATA JADI BEBERAPA FOLDS
        f = []
        for x in range(self.folds):
            g = []
            while len(g) < self.index:
                g.append(raw.pop(0))
            f.append(g)

        # TRAIN TEST SPLIT DARI FOLD
        for x in range(self.folds):
            self.word = {}
            data_copy = copy.deepcopy(f)
            test = data_copy.pop(x)
            train = [w for q in data_copy for w in q]
            # LAKUKAN TRAINING DAN TESTING
            _pred = []
            _sent = []
            for tknz, sntm in test:
                _pred.append(tknz)
                _sent.append(sntm)
            self.fit(train)
            prediction = self.predict(_pred)
            # HITUNG AKURASI
            _wp = 0
            for i in range(len(_pred)):
                if _sent[i] != prediction[i]:
                    _wp += 1
            _acc = 100 - (_wp / len(_pred)) * 100 if _wp > 0 else 100
            accuracy.append(_acc)

        with open(f'data/latih/kfold_acc.csv', 'w', newline='\n', encoding='utf8') as kf:
            writer = csv.writer(kf)
            writer.writerow(accuracy)

        return accuracy


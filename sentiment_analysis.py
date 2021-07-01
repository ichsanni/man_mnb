from multinomial_naive_bayes import MultinomialNaiveBayes
import csv, pickle
from preprocessing import Preprocessing
import matplotlib.pyplot as plt 
import numpy as np

class SentimentAnalysis():
    def __init__(self):
        pass

    def plot_histogram(self, target, count, bar_color=['red', 'green']):
        plt.figure(figsize=(9,5))
        plt.subplot()
        plt.xlabel('Sentimen', fontsize=15)
        plt.ylabel('Jumlah Tweet', fontsize=15)
        plt.bar(target, count, color=bar_color)
        plt.tight_layout()
        plt.savefig('static/histogram.png')
    
    def plot_kfold(self):
        acc = []
        with open("data/latih/kfold_acc.csv", 'r') as n:
            reader = csv.reader(n)
            for x in reader:
                for y in x:
                    acc.append(float(y))
        num = [x+1 for x in range(len(acc))]
        plt.figure(figsize=(9,5))
        plt.plot(num, acc, '-o', color="black")
        plt.xlabel(f'Fold Ke-n\nrata-rata akurasi: {sum(acc)/len(acc)}', fontsize=15)
        plt.ylabel('Akurasi', fontsize=15)
        plt.xticks(num)
        plt.tight_layout()
        plt.savefig('static/kfold.png')

    def plot_confusion_matrix(self, cmx, target_names, cmap='Greens'):
        import itertools

        cm = np.array(cmx)
        accuracy = np.trace(cm) / float(np.sum(cm))
        misclass = 1 - accuracy

        plt.figure(figsize=(9, 5))
        plt.imshow(cm, interpolation='nearest', cmap=cmap)
        
        plt.colorbar()

        if target_names is not None:
            tick_marks = np.arange(len(target_names))
            plt.xticks(tick_marks, target_names, rotation=45)
            plt.yticks(tick_marks, target_names)

        thresh = cm.max() / 2
        for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
                plt.text(j, i, "{:,}".format(cm[i, j]),
                        horizontalalignment="center",
                        color="white" if cm[i, j] > thresh else "black")

        plt.ylabel('Actual label')
        plt.xlabel('Predicted label\nakurasi={:0.4f}; misclass={:0.4f}'.format(accuracy, misclass))
        
        plt.tight_layout()
        plt.savefig('static/conf_matrix.png')

    def classify_model(self, location = 'data/unggahan/training_data.csv'):
        tweet = []
        label = []
        tweet_id = []
        tweet_date = []

        with open(location, 'r', encoding='utf8') as file_csv:
            reader = csv.DictReader(file_csv)
            for row in reader:
                tweet.append(row["text"])               # ambil teks tweet
                label.append(row["sentiment"])          # ambil label sentimen
                tweet_id.append(row["id"])
                tweet_date.append(row["created_at"])
        
        preprocessing = Preprocessing(new=True)
        preprocessing.update_status(0, 1)
        case_folding = preprocessing.case_folding(tweet)
        stop_word_removal = preprocessing.stop_word_removal(case_folding) # filtering
        stemming = preprocessing.stemming(stop_word_removal)
        tokenized = preprocessing.tokenizing(stemming)
        preprocessing.update_status(5, 1)
        preprocessing.update_status(0, 2)

        class_counter = preprocessing.class_frequency(label)
        _class, _counter = [x for x,y in class_counter], [y for x,y in class_counter]
        if _class[0] == 'negatif':
            preprocessing.update_status(7, _counter[0])
            preprocessing.update_status(8, _counter[1])
        if _class[0] == 'positif':
            preprocessing.update_status(7, _counter[1])
            preprocessing.update_status(8, _counter[0])

        # LATIH MODEL
        model = MultinomialNaiveBayes(alpha=1)
        # SPLIT 90:10 (0.9:0.1)
        train_test_split = model.train_test_split(zip(tweet, tokenized, label), test_data=0.1)
        preprocessing.update_status(6, train_test_split)
        # SIMPAN MODEL
        with open(f"data/latih/trained_model.pickle", 'wb') as pickl:
            pickle.dump(model, pickl)
        
        # K-FOLD ACCURACY
        kfold = model.kfold_cross_validation(zip(tokenized, label), folds=10)

        # BUAT HISTOGRAM
        self.plot_histogram(_class, _counter, bar_color=['red', 'green'])
        # BUAT K-FOLD GRAPH
        self.plot_kfold()
        # BUAT CONFUSION MATRIX
        target = ['Positif', 'Negatif']
        self.plot_confusion_matrix(model.cm, target)




    
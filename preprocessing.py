from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
import re, csv, collections



class Preprocessing():
    def __init__(self, new = False):
        self.new = new
        if self.new:
            # status.csv:
            ### overall, casefolding, filtering, stemming, totalstemmed, tokenization, accuracy, negatif, positif
            with open('data/latih/status.csv', 'w') as f:
                writer = csv.writer(f)
                writer.writerow([0, 0, 0, 0, 0, 0, 0, 0, 0])
                print("made status.csv")
        else:
            with open('data/latih/livetwt_status.csv', 'w') as f:
                writer = csv.writer(f)
                writer.writerow([0, 0])
                print("made livetwt_status.csv")

    def case_folding(self, teks):
        sentence = []
        for x in teks:
            # hapus mention, retweet, alamat web, dan hashtag
            # ubah teks menjadi huruf kecil
            r1 = re.sub('\@[A-Za-z0-9._]+|(^rt)|(http|https)://[A-Za-z0-9.\-\/]+|\#\w+', '', x.lower())
            r4 = re.sub('\W|\n+', ' ', r1)      # hapus tanda baca, emoji, dan newline char
            r5 = re.sub('\s{2,}', ' ', r4)      # hapus spasi lebih dari 1
            r6 = re.sub('^\s|\s$', '', r5)      # hapus spasi di awal dan akhir kalimat
            sentence.append(r6)
        if self.new: self.update_status(1, 1)
        return sentence

    def stemming(self, teks):
        stem_factory = StemmerFactory()
        stemmer = stem_factory.create_stemmer()
        if self.new: self.update_status(4, len(teks))
        sentence_stemmed = []
        for x in range(len(teks)):
            # mulai proses stemming
            # menggunakan algoritma nazief adriani
            sentence_stemmed.append(stemmer.stem(teks[x]))
            ind = x + 1
            if self.new:
                self.update_status(3, ind)
            else:
                self.update_status(1, ind)
        return sentence_stemmed

    def stop_word_removal(self, teks):
        sentence = []
        stop_word_factory = StopWordRemoverFactory()
        word_list = stop_word_factory.get_stop_words()
        for x in teks:
            # filtering: hapus stop words pada teks
            removed = [y for y in x.split() if y not in word_list]
            sentence.append(" ".join(removed))
        if self.new: self.update_status(2, 1)
        return sentence

    def tokenizing(self, teks):
        return [x.split() for x in teks]
    
    def class_frequency(self, class_feats):
        counter = collections.Counter(class_feats)
        _cc = []
        for x in counter.most_common():
            _cc.append(x)
        return _cc

    def update_status(self, position, status):
        temp = []
        if self.new:
            with open('data/latih/status.csv', 'r') as b:
                reader = csv.reader(b)
                for x in reader:
                    for y in range(len(x)):
                        temp.append(x[y])
            temp[position] = status
            with open('data/latih/status.csv', 'w') as t:
                writer = csv.writer(t)
                writer.writerow(temp)
        else:
            with open('data/latih/livetwt_status.csv', 'r') as b:
                reader = csv.reader(b)
                for x in reader:
                    for y in range(len(x)):
                        temp.append(x[y])
            temp[position] = status
            with open('data/latih/livetwt_status.csv', 'w') as t:
                writer = csv.writer(t)
                writer.writerow(temp)


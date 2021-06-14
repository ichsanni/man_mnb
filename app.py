from flask import Flask 
from flask import render_template, request
from sentiment_analysis import SentimentAnalysis
import csv
import os

# command: flask run

app = Flask("Skripsi Analisis Sentimen",
            template_folder='templates',
            static_folder='static')
app.config['TESTING'] = True
app.config.update(
    UPLOAD_FOLDER = 'data/unggahan',
    MAX_CONTENT_PATH = 15 * 1024 * 1024)
lihat_sentimen = SentimentAnalysis()

# 127.0.0.1
@app.route('/')
def home():
    histogram = 'static/histogram.png'
    kfold_curve = 'static/kfold.png'
    conf = 'static/conf_matrix.png'
    return render_template('home.html', 
                            histogram = histogram, 
                            kfold = kfold_curve,
                            conf = conf)

# 127.0.0.1/data_train
@app.route('/data_train')
def data_train():
    try:
        train_data = []
        with open('data/latih/split_train.csv', 'r', encoding='utf8') as f:
            reader = csv.reader(f)
            train_data = [row for row in reader]
        return render_template('data_train.html', train = train_data, len_train = len(train_data))
    except FileNotFoundError as e:
        train_data = ['-', '-', '-']
        return render_template('data_train.html', train = train_data, len_train = len(train_data))

# 127.0.0.1/data_test
@app.route('/data_test')
def data_test():
    try:
        test_data = []
        with open('data/latih/split_test.csv', 'r', encoding='utf8') as f:
            reader = csv.reader(f)
            test_data = [row for row in reader]
        return render_template('data_test.html', test = test_data, len_test = len(test_data))
    except FileNotFoundError as e:
        test_data = ['-','-','-','-','-','-']
        return render_template('data_test.html', test = test_data, len_test = len(test_data))

# 127.0.0.1/live
@app.route('/live')
def live_tweet():
    return render_template('live_sent.html')

# 127.0.0.1/delete
@app.route('/delete')
def delete_trained_model():
    files = ["data/latih/freq_dist.csv", "data/latih/kfold_acc.csv", "data/latih/livetwt_status.csv",
            "data/latih/real_time_data.csv", "data/latih/split_test.csv", "data/latih/split_train.csv",
            "data/latih/status.csv", "data/latih/trained_model.pickle", "data/latih/word.csv", "data/live_tweet.csv",
            "static/conf_matrix.png", "static/histogram.png", "static/kfold.png"]
    
    for f in files:
        if os.path.exists(f): os.remove(f)

    return {'status':'200'}

# 127.0.0.1/latih
@app.route('/latih')
def latih_sentimen():
    lihat_sentimen.classify_model()
    return {'status':'200'}

# 127.0.0.1/unggah
@app.route('/unggah', methods=['POST'])
def unggah_file():
    file = request.files['file']
    file_name = 'training_data.csv'
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
    print(file_path)
    file.save(file_path)
    return {'status': '200'}
    
# 127.0.0.1/status
@app.route('/status')
def baca_status():
    temp = {}
    if os.path.exists('data/latih/status.csv'):
        with open('data/latih/status.csv', 'r') as f:
            reader = csv.reader(f)
            for x in reader:
                for y in range(len(x)):
                    temp['overall'] = x[0]
                    temp['casefolding'] = x[1]
                    temp['filtering'] = x[2]
                    temp['stemming'] = x[3]
                    temp['totalstemmed'] = x[4]
                    temp['tokenizing'] = x[5]
                    temp['accuracy'] = x[6]
                    temp['negatif'] = x[7]
                    temp['positif'] = x[8]
        with open('data/latih/kfold_acc.csv', 'r') as g:
            reader = csv.reader(g)
            kf = []
            for x in reader:
                for y in range(len(x)):
                    kf.append(float(x[y]))
            avg_kfold = sum(kf) / len(kf)
            temp['kfold'] = kf
            temp['avg_kfold'] = avg_kfold
    return temp

# 127.0.0.1/live_sentiment
@app.route('/live_sentiment')
def get_live_sent():
    from twitter_scrape import TwitterScrape
    from preprocessing import Preprocessing
    import pickle
    
    preprocessing = Preprocessing()

    ts = TwitterScrape()
    ts.manual_scrape()
    preprocessing.update_status(0, 1)

    tweet = []
    id_tw = []
    tgl = []
    with open('data/live_tweet.csv', 'r', encoding='utf8') as f:
        reader = csv.reader(f)
        for x in reader:
            tweet.append(x[0])
            id_tw.append(x[1])
            tgl.append(x[2])
 
    case_folding = preprocessing.case_folding(tweet)
    stop_word_removal = preprocessing.stop_word_removal(case_folding) # filtering
    stemming = preprocessing.stemming(stop_word_removal)
    tokenized = preprocessing.tokenizing(stemming)

    with open('data/latih/trained_model.pickle', 'rb') as g:
        model = pickle.load(g)
    
    prediction = model.predict(tokenized)

    with open('data/latih/real_time_data.csv', 'w', encoding='utf8') as gg:
        writer = csv.writer(gg)
        writer.writerows(zip(tgl, id_tw, tweet, prediction))

    return {'status':200}

# 127.0.0.1/livetwt_status
@app.route('/livetwt_status')
def baca_livetwt_status():
    temp = {}
    if os.path.exists('data/latih/livetwt_status.csv'):
        with open('data/latih/livetwt_status.csv', 'r') as f:
            reader = csv.reader(f)
            for x in reader:
                for y in range(len(x)):
                    temp['scraped_data'] = x[0]
                    temp['stemming_status'] = x[1]
    return temp

# 127.0.0.1/get_livetwt_data
@app.route('/get_livetwt_data')
def get_livetwt_data():
    try:
        with open('data/latih/real_time_data.csv', 'r', encoding='utf8', newline='') as f:
            reader = csv.reader(f)
            data = [row for row in reader if len(row) != 0]
            return {'status': '200', 
                    'data': data}
    except FileNotFoundError as e:
        return {'status': '404', 'error': str(e)}

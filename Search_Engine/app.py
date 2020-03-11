from pymongo import MongoClient
from flask import Flask, request, render_template, redirect, url_for
from engine.search_engine import SearchEngine
from flask_bootstrap import Bootstrap

app = Flask(__name__)
Bootstrap(app)

client = MongoClient('localhost', 27017)
se = SearchEngine(client.test1)


@app.route('/', methods=['get', 'post'])
def index():
    if request.method == 'POST':
        query = request.form.get('text_query')
        docs = se.resolve_query(query)
        return query_result(docs)
    docs_num = len(se.collection) + se.DBH.get_songs_number()
    return render_template('index.html', docs_num=docs_num)


@app.route('/engine/search', methods=['post'])
def query_result(docs):
    return render_template('search_result.html', docs=docs)


@app.route('/songs', methods=['get'])
def get_song():
    id = request.args.get('id')
    print(id)
    if not id or not int(id) in se.collection.keys():
        print("getting song form db")
        song = se.DBH.get_song(int(id))
        print(song.id)
        if not song:
            return redirect(url_for('index'))
    else:
        print("getting song form memory")
        song = se.collection[int(id)]
        print(song.id)
    return render_template('song_detail.html', song=song)


if __name__ == '__main__':
    se.load()
    se.start_crawler()
    app.run()

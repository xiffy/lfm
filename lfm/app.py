import os
import requests

from flask import Flask, render_template, request, send_from_directory
from config import Config

app = Flask(__name__)
config = Config()


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/', methods=['GET', 'POST'])
def hello_readers():
    if request.method == 'GET':
        payload = {'user': 'thexiffy', 'title': 'Example URLs'}
    else:
        payload = {'user': request.form['user'], 'title': 'Your URLs'}
    payload['base_url'] = config.base_url
    return render_template('home.html', context=payload)


@app.route('/<user>')
def recent_tracks(user):
    # /2.0/?method=user.getrecenttracks&user=rj&api_key=YOUR_API_KEY&format=json
    payload = {'api_key': config.api_key,
               'method': 'user.getrecenttracks',
               'user': user,
               'format': 'json'}
    response = requests.get(config.api_base_url, params=payload)
    try:
        json = response.json()
        context = {'user': user,
                   'tracks': json['recenttracks'],
                   'type': 'recent'}
        return render_template('recent.html', context=context), 200, {"Content-type": "text/xml; charset=utf-8",
                                                                      "Cache-Control": "s-maxage=600"}
    except ValueError:
        return response.content


@app.route('/<user>/loved')
def loved_tracks(user):
    payload = {'api_key': config.api_key,
               'method': 'user.getlovedtracks',
               'user': user,
               'format': 'json'}
    response = requests.get(config.api_base_url, params=payload)
    try:
        json = response.json()
        context = {'user': user,
                   'tracks': json['lovedtracks'],
                   'type': 'loved'}
        return render_template('loved.html', context=context), 200, {"Content-type": "text/xml; charset=utf-8",
                                                                     "Cache-Control": "s-maxage=600"}
    except ValueError:
        return response.content


@app.template_filter('artistlink')
def make_artistlink(url):
    return '/'.join(url.split('/')[:-2])


if __name__ == '__main__':
    app.run()

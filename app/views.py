import requests
from flask import render_template, request, redirect, make_response
from app import app
import urllib
import uuid


@app.route('/')
def hello_world():  # put application's code here
    return render_template('index.html', name=app.config['NAME'], token=request.cookies.get('token'))


@app.route('/login')
def login():
    return render_template('sign-in.html')


@app.route('/spotify-login')
def spotify_login():
    authentication_request_params = {
        'response_type': 'code',
        'client_id': app.config['CLIENT_ID'],
        'redirect_uri': app.config['REDIRECT_URI'],
        'scope': 'user-read-email user-read-private user-top-read',
        'state': str(uuid.uuid4()),
        'show_dialog': 'false'
    }

    return redirect('https://accounts.spotify.com/authorize/?' + urllib.parse.urlencode(authentication_request_params))


@app.route('/callback')
def callback():
    code = request.args.get('code')
    credentials = get_access_token(authorization_code=code)
    refresh_token = credentials['refresh_token']
    print(refresh_token)
    response = make_response(redirect("/"))
    response.set_cookie('token', credentials['access_token'])

    return response


def get_access_token(authorization_code: str):
    spotify_request_access_token_url = 'https://accounts.spotify.com/api/token/'
    body = {'grant_type': 'authorization_code',
            'code': authorization_code,
            'client_id': app.config['CLIENT_ID'],
            'client_secret': app.config['CLIENT_SECRET'],
            'redirect_uri': app.config['REDIRECT_URI']
            }
    response: requests.Response = requests.post(spotify_request_access_token_url, data=body)
    if response.status_code == 200:
        return response.json()

    raise Exception(f'Failed to obtain Access token.Response: {response.text}')


@app.route('/top-tracks')
def top_tracks():
    token = request.cookies.get('token')

    root_url = 'https://api.spotify.com/v1/me/top/tracks'

    # NB: Add the access token to the request header
    headers = {
        'Authorization': f'Bearer {token}'
    }

    request_params = {
        'time_range': 'medium_term',
        'limit': 20,
        'offset': 0
    }

    # NOTE: This requires the scope 'user-top-read'
    full_url = root_url
    response = requests.get(full_url,
                            headers=headers,
                            params=request_params)

    if response.status_code == 200:
        return response.json()

    raise Exception(f'API Call to {full_url} failed. {response.text}')


@app.route("/logout")
def navbar():
    response = make_response(redirect("/"))
    response.set_cookie('token', expires=0)

    return response

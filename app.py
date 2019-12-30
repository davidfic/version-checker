import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify


app = Flask(__name__)

hashicorp_urls = {'terraform': 'https://releases.hashicorp.com/terraform',
                'vault': 'https://releases.hashicorp.com/vault'}

release_channel = {'stable': 'https://cloud.google.com/kubernetes-engine/docs/release-notes-stable', 
                    'regular': 'https://cloud.google.com/kubernetes-engine/docs/release-notes-regular',
                    'rapid': 'https://cloud.google.com/kubernetes-engine/docs/release-notes-rapid'
}

def get_version(url):
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, 'html.parser')
    release_list = soup.find_all('a')
    if 'vault' in url:
        #ugly hack to avoid the hsm versions
        return str(release_list[1])[str(release_list[1]).index('>')+1:str(release_list[1]).index('>')+12]
    return str(release_list[1])[str(release_list[1]).index('>')+1:-4]

@app.route('/terraform')
def get_terraform_latest_version():
    return get_version(hashicorp_urls['terraform'])

@app.route('/vault')
def get_vault_latest_version():
    return get_version(hashicorp_urls['vault'])

@app.route('/')
def index():
    all_release_versions = {}
    all_release_versions = {'terraform': get_terraform_latest_version(), 
                            'vault': get_vault_latest_version(),
                            'gke-stable': get_gke_stable_release(),
                            'gke-regular': get_gke_regular_release(),
                            'gke-rapid': get_gke_rapid_release()}

    return all_release_versions


def gke_release_version(channel):
    resp = requests.get(channel)
    soup = BeautifulSoup(resp.text, 'html.parser')
    release_number = soup.find('div', {'class': 'release-changed'}).find('p')
    return str(release_number)[3:str(release_number).index(' ')]

@app.route('/gke-stable')
def get_gke_stable_release():
    return gke_release_version(release_channel['stable'])


@app.route('/gke-regular')
def get_gke_regular_release():
    return gke_release_version(release_channel['regular'])

@app.route('/gke-rapid')
def get_gke_rapid_release():

    resp = requests.get(release_channel['rapid'])
    soup = BeautifulSoup(resp.text, 'html.parser')
    release_number = soup.find_all('h3')
    latest_release = release_number[0]

    start = str(latest_release).index('>')+1
    return str(latest_release)[start:-5]

@app.route('/gke-stable-all')
def get_gke_stable_release_all():
    resp = requests.get(release_channel['stable'])
    soup = BeautifulSoup(resp.text, 'html.parser')
    release_changed = soup.find_all('div', {'class': 'release-changed'})

    ps = []
    for release in release_changed:
        ps.append(release.find('p'))

    versions = {}
    count = 0 
    for tag_release in ps:
        tag_text = tag_release.text
        if tag_text.lstrip().startswith('v'):
            versions[count] = (tag_text.lstrip()[1:tag_text.lstrip().index(' ')])
            count += 1
    return versions


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0',port='8080')

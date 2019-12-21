import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify,make_response


app = Flask(__name__)

hashicorp_base_url = 'https://releases.hashicorp.com/'

release_channel = {'stable': 'https://cloud.google.com/kubernetes-engine/docs/release-notes-stable', 
                    'regular': 'https://cloud.google.com/kubernetes-engine/docs/release-notes-regular',
                    'rapid': 'https://cloud.google.com/kubernetes-engine/docs/release-notes-rapid'
}

def get_version(url):
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, 'html.parser')
    release_list = soup.find_all('a')
    return str(release_list[1])[str(release_list[1]).index('>')+1:-4]

@app.route('/terraform')
def get_terraform_latest_version():
    return get_version(hashicorp_base_url + 'terraform')

@app.route('/vault')
def get_vault_latest_version():
    
    return get_version(hashicorp_base_url + 'vault')

@app.route('/')
def index():
    all_release_versions = {}
    all_release_versions = {'terraform': get_terraform_latest_version(), 
                        'vault': get_vault_latest_version(),
                        'gke-stable': get_gke_stable_release(),
                        'gke-regular': get_gke_regular_release()}

    return all_release_versions


def gke_release_version(channel):
    resp = requests.get(channel)
    soup = BeautifulSoup(resp.text, 'html.parser')
    release_number = soup.find('div', {'class': 'release-changed'}).find('p')
    str_rel = str(release_number)
    rel_num = str_rel[3:str_rel.index(' ')]
    return rel_num

@app.route('/gke-stable')
def get_gke_stable_release():
    return gke_release_version(release_channel['stable'])


@app.route('/gke-regular')
def get_gke_regular_release():
    return gke_release_version(release_channel['regular'])

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0',port='8080')

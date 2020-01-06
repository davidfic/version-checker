import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify, render_template
import re
from flask_bootstrap import Bootstrap

app = Flask(__name__)
Bootstrap(app)

release_notes_urls = {'gke-stable': 'https://cloud.google.com/kubernetes-engine/docs/release-notes-stable',
                      'gke-rapid': 'https://cloud.google.com/kubernetes-engine/docs/release-notes-rapid',
                      'gke-regular': 'https://cloud.google.com/kubernetes-engine/docs/release-notes-regular',
                      'vault': 'https://github.com/hashicorp/vault/blob/master/CHANGELOG.md',
                      'terraform': 'https://github.com/hashicorp/terraform/blob/master/CHANGELOG.md'
                    }   
releases = {}
releases['vault'] = []
releases['terraform'] = []
releases['gke-stable'] = []
releases['gke-regular'] = []
releases['gke-rapid'] = []

hashicorp_urls = {'terraform': 'https://releases.hashicorp.com/terraform',
                'vault': 'https://releases.hashicorp.com/vault'}

release_channel = {'stable': 'https://cloud.google.com/kubernetes-engine/docs/release-notes-stable', 
                    'regular': 'https://cloud.google.com/kubernetes-engine/docs/release-notes-regular',
                    'rapid': 'https://cloud.google.com/kubernetes-engine/docs/release-notes-rapid'
}

software = ['gke-stable', 'gke-rapid', 'gke-regular', 'vault', 'terraform']

def get_anchors(url):
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, 'html.parser')
    return soup.find_all('a')

def get_versions(url):
    release_list = get_anchors(url)
    versions = []
    for release in release_list:
        if release.text.startswith('v'):
            versions.append(re.sub('[-+]', '', release.text[:12]))
        elif release.text.startswith('t'):
            versions.append(release.text)
    return versions
    

def get_version(url):
    release_list = get_anchors(url)
    if 'vault' in url:
        #ugly hack to avoid the hsm versions
        return release_list[1].text[:11]
    # return str(release_list[1])[str(release_list[1]).index('>')+1:-4]
    return release_list[1].text

def get_release_notes(software):
    resp = requests.get(release_notes)


@app.route('/terraform')
def get_terraform_latest_version():
    return get_version(hashicorp_urls['terraform'])

@app.route('/vault')
def get_vault_latest_version():
    return get_version(hashicorp_urls['vault'])

@app.route('/vault-all')
def get_all_vault_versions():
    vault_versions = get_versions(hashicorp_urls['vault'])
    return jsonify(vault_versions)


@app.route('/terraform-all')
def get_all_terraform_versions():
    terraform_versions = get_versions(hashicorp_urls['terraform'])
    return jsonify(terraform_versions)
     

@app.route('/')
def index():
    all_release_versions = {}
    all_release_versions = {'terraform': get_terraform_latest_version(), 
                            'vault': get_vault_latest_version(),
                            'gke-stable': get_gke_stable_release(),
                            'gke-regular': get_gke_regular_release(),
                            'gke-rapid': get_gke_rapid_release()}

    # return all_release_versions
    return render_template('index.html', releases=all_release_versions, software=software, release_notes=release_notes_urls)


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


def get_releases(channel):
    resp = requests.get(release_channel[channel])
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

@app.route('/gke-stable-all')
def get_gke_stable_release_all():
    return get_releases('stable')


@app.route('/gke-regular-all')
def get_gke_regular_release_all():
    return get_releases('regular')



if __name__ == "__main__":
    
    app.run(debug=True, host='0.0.0.0',port='8080')

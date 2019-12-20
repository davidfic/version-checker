import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify


app = Flask(__name__)

def get_version(base_url):
    resp = requests.get(base_url)
    soup = BeautifulSoup(resp.text, 'html.parser')
    release_list = soup.find_all('a')
    return str(release_list[1])[str(release_list[1]).index('>')+1:-4]

@app.route('/terraform')
def get_terraform_version():
    # base_url = 'https://releases.hashicorp.com/terraform'

    
    # resp = requests.get(base_url)
    # soup = BeautifulSoup(resp.text, 'html.parser')
    # release_list = soup.find_all('a')
    # return str(release_list[1])[str(release_list[1]).index('>')+1:-4]
    return get_version('https://releases.hashicorp.com/terraform')

@app.route('/vault')
def get_vault_latest_version():
    return get_version('https://releases.hashicorp.com/vault')
    # base_url = 'https://releases.hashicorp.com/vault'

if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0',port='8080')

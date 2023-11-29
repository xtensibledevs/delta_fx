import os
from flask import Blueprint, request

deploy_hook = Blueprint('webhooks')


@deploy_hook.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    
    repo_url = data.get('repository',{}).get('clone_url')
    branch = data.get('ref', '').split('/')[-1]
    commit = data.get('after')

    pass
import os

settings = {
    'host': os.environ.get('ACCOUNT_HOST', 'https://260025lab6.documents.azure.com:443/'),
    'master_key': os.environ.get('ACCOUNT_KEY', 'secret:)'),
    'database_id': os.environ.get('COSMOS_DATABASE', 'ToDoList'),
    'container_id': os.environ.get('COSMOS_CONTAINER', 'Items'),
}
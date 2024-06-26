import azure.cosmos.documents as documents
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
from azure.cosmos.partition_key import PartitionKey
import datetime
import logging
import sys

import config

logging.basicConfig(filename='logs_sprawko6.log',
                    encoding='UTF-8',
                    filemode='a',
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logger2 = logging.getLogger('azure')
logger2.setLevel(logging.DEBUG)

handler = logging.StreamHandler(stream=sys.stdout)
logger2.addHandler(handler)


# ----------------------------------------------------------------------------------------------------------
# Prerequistes -
#
# 1. An Azure Cosmos account -
#    https://docs.microsoft.com/azure/cosmos-db/create-cosmosdb-resources-portal#create-an-azure-cosmos-db-account
#
# 2. Microsoft Azure Cosmos PyPi package -
#    https://pypi.python.org/pypi/azure-cosmos/
# ----------------------------------------------------------------------------------------------------------
# Sample - demonstrates the basic CRUD operations on a Item resource for Azure Cosmos
# ----------------------------------------------------------------------------------------------------------

HOST = config.settings['host']
MASTER_KEY = config.settings['master_key']
DATABASE_ID = config.settings['database_id']
CONTAINER_ID = config.settings['container_id']


def create_items(container):
    """
    Creates items in the specified container.

    Parameters:
    - container (azure.cosmos.container.Container): The container where items will be created.

    Returns:
    - None
    """
    logging.info('\nCreating Items\n')

    sales_order = get_sales_order("SalesOrder1")
    logging.info('\nCreating Items1\n')
    container.create_item(body=sales_order)

    sales_order2 = get_sales_order_v2("SalesOrder2")
    logging.info('\nCreating Items2\n')
    container.create_item(body=sales_order2)


    sales_order3 = get_sales_order_v3("SalesOrder3")
    logging.info('\nCreating Items3\n')


    container.create_item(body=sales_order3)

def scale_container(container):
    """
    Scales the throughput of the specified container.

    Parameters:
    - container (azure.cosmos.container.Container): The container to scale.

    Returns:
    - None
    """
    logging.info('\nScaling Container\n')

    # You can scale the throughput (RU/s) of your container up and down to meet the needs of the workload. Learn more: https://aka.ms/cosmos-request-units
    try:
        offer = container.read_offer()
        logging.info('Found Offer and its throughput is \'{0}\''.format(offer.offer_throughput))

        offer.offer_throughput += 100
        container.replace_throughput(offer.offer_throughput)

        logging.info('Replaced Offer. Offer Throughput is now \'{0}\''.format(offer.offer_throughput))

    except exceptions.CosmosHttpResponseError as e:
        if e.status_code == 400:
            logging.info('Cannot read container throuthput.')
            logging.info(e.http_error_message)
        else:
            raise;

def read_item(container, doc_id, account_number):
    """
    Reads an item from the specified container by its ID and partition key.

    Parameters:
    - container (azure.cosmos.container.Container): The container to read the item from.
    - doc_id (str): The ID of the item to read.
    - account_number (str): The partition key of the item to read.

    Returns:
    - None
    """
    logging.info('\nReading Item by Id\n')

    # We can do an efficient point read lookup on partition key and id
    response = container.read_item(item=doc_id, partition_key=account_number)

    logging.info('Item read by Id {0}'.format(doc_id))
    logging.info('Partition Key: {0}'.format(response.get('partitionKey')))
    logging.info('Subtotal: {0}'.format(response.get('subtotal')))


def read_items(container):
    """
    Reads all items in the specified container.

    Parameters:
    - container (azure.cosmos.container.Container): The container to read items from.

    Returns:
    - None
    """
    logging.info('\nReading all items in a container\n')

    # NOTE: Use MaxItemCount on Options to control how many items come back per trip to the server
    #       Important to handle throttles whenever you are doing operations such as this that might
    #       result in a 429 (throttled request)
    item_list = list(container.read_all_items(max_item_count=10))

    logging.info('Found {0} items'.format(item_list.__len__()))

    for doc in item_list:
        logging.info('Item Id: {0}'.format(doc.get('id')))


def query_items(container, account_number):
    """
    Queries items in the specified container by partition key.

    Parameters:
    - container (azure.cosmos.container.Container): The container to query items from.
    - account_number (str): The partition key to filter items by.

    Returns:
    - None
    """
    logging.info('\nQuerying for an  Item by Partition Key\n')

    # Including the partition key value of account_number in the WHERE filter results in a more efficient query
    items = list(container.query_items(
        query="SELECT * FROM r WHERE r.partitionKey=@account_number",
        parameters=[
            { "name":"@account_number", "value": account_number }
        ]
    ))

    logging.info('Item queried by Partition Key {0}'.format(items[0].get("id")))


def replace_item(container, doc_id, account_number):
    """
    Replaces an item in the specified container by its ID and partition key.

    Parameters:
    - container (azure.cosmos.container.Container): The container to replace the item in.
    - doc_id (str): The ID of the item to replace.
    - account_number (str): The partition key of the item to replace.

    Returns:
    - None
    """
    logging.info('\nReplace an Item\n')

    read_item = container.read_item(item=doc_id, partition_key=account_number)
    read_item['subtotal'] = read_item['subtotal'] + 1
    response = container.replace_item(item=read_item, body=read_item)

    logging.info('Replaced Item\'s Id is {0}, new subtotal={1}'.format(response['id'], response['subtotal']))


def upsert_item(container, doc_id, account_number):
    """
    Upserts an item in the specified container by its ID and partition key.

    Parameters:
    - container (azure.cosmos.container.Container): The container to upsert the item in.
    - doc_id (str): The ID of the item to upsert.
    - account_number (str): The partition key of the item to upsert.

    Returns:
    - None
    """
    logging.info('\nUpserting an item\n')

    read_item = container.read_item(item=doc_id, partition_key=account_number)
    read_item['subtotal'] = read_item['subtotal'] + 1
    response = container.upsert_item(body=read_item)

    logging.info('Upserted Item\'s Id is {0}, new subtotal={1}'.format(response['id'], response['subtotal']))


def delete_item(container, doc_id, account_number):

    """
    Deletes an item from the specified container by its ID and partition key.

    Parameters:
    - container (azure.cosmos.container.Container): The container to delete the item from.
    - doc_id (str): The ID of the item to delete.
    - account_number (str): The partition key of the item to delete.

    Returns:
    - None
    """
    logging.info('\nDeleting Item by Id\n')

    response = container.delete_item(item=doc_id, partition_key=account_number)

    logging.info('Deleted item\'s Id is {0}'.format(doc_id))


def get_sales_order(item_id):
    """
    Generates a sales order object.

    Parameters:
    - item_id (str): The ID of the sales order.

    Returns:
    - dict: A dictionary representing the sales order.
    """
    order1 = {'id' : item_id,
            'partitionKey' : 'Account1',
            'purchase_order_number' : 'PO18009186470',
            'order_date' : datetime.date(2005,1,10).strftime('%c'),
            'subtotal' : 419.4589,
            'tax_amount' : 12.5838,
            'freight' : 472.3108,
            'total_due' : 985.018,
            'items' : [
                {'order_qty' : 1,
                    'product_id' : 100,
                    'unit_price' : 418.4589,
                    'line_price' : 418.4589
                }
                ],
            'ttl' : 60 * 60 * 24 * 30
            }

    return order1


def get_sales_order_v2(item_id):
    """
    Generates a version 2 sales order object.

    Parameters:
    - item_id (str): The ID of the sales order.

    Returns:
    - dict: A dictionary representing the version 2 sales order.
    """
    order2 = {'id' : item_id,
            'partitionKey' : 'Account2',
            'purchase_order_number' : 'PO15428132599',
            'order_date' : datetime.date(2005,7,11).strftime('%c'),
            'due_date' : datetime.date(2005,7,21).strftime('%c'),
            'shipped_date' : datetime.date(2005,7,15).strftime('%c'),
            'subtotal' : 6107.0820,
            'tax_amount' : 586.1203,
            'freight' : 183.1626,
            'discount_amt' : 1982.872,
            'total_due' : 4893.3929,
            'items' : [
                {'order_qty' : 3,
                    'product_code' : 'A-123',      # notice how in item details we no longer reference a ProductId
                    'product_name' : 'Product 1',  # instead we have decided to denormalise our schema and include
                    'currency_symbol' : '$',       # the Product details relevant to the Order on to the Order directly
                    'currency_code' : 'USD',       # this is a typical refactor that happens in the course of an application
                    'unit_price' : 17.1,           # that would have previously required schema changes and data migrations etc.
                    'line_price' : 5.7
                }
                ],
            'ttl' : 60 * 60 * 24 * 30
            }

    return order2

def get_sales_order_v3(item_id):
    """
    Generates a version 3 sales order object.

    Parameters:
    - item_id (str): The ID of the sales order.

    Returns:
    - dict: A dictionary representing the version 3 sales order.
    """
    order2 = {'id' : item_id,
            'partitionKey' : 'Account2',
            'purchase_order_number' : 'PO15428132599',
            'order_date' : datetime.date(2005,7,11).strftime('%c'),
            'due_date' : datetime.date(2005,7,21).strftime('%c'),
            'shipped_date' : datetime.date(2005,7,15).strftime('%c'),
            'subtotal' : 6107.0820,
            'tax_amount' : 586.1203,
            'freight' : 183.1626,
            'discount_amt' : 1982.872,
            'total_due' : 4893.3929,
            'items' : [
                {'order_qty' : 3,
                    'product_code' : 'A-123',      # notice how in item details we no longer reference a ProductId
                    'product_name' : 'Product 1',  # instead we have decided to denormalise our schema and include
                    'currency_symbol' : '$',       # the Product details relevant to the Order on to the Order directly
                    'currency_code' : 'USD',       # this is a typical refactor that happens in the course of an application
                    'unit_price' : 17.1,           # that would have previously required schema changes and data migrations etc.
                    'line_price' : 5.7
                }
                ],
            'ttl' : 60 * 60 * 24 * 30
            }

    return order2


def run_sample():
    """
    Runs the sample application, demonstrating basic CRUD operations on Azure Cosmos DB.

    Parameters:
    - None

    Returns:
    - None
    """
    client = cosmos_client.CosmosClient(HOST,
                                        {'masterKey': MASTER_KEY},
                                        user_agent="CosmosDBPythonQuickstart",
                                        user_agent_overwrite=True, logger=logger2,
                                        enable_diagnostics_logging=True)
    try:
        # setup database for this sample
        try:
            db = client.create_database(id=DATABASE_ID)
            logging.info('Database with id \'{0}\' created'.format(DATABASE_ID))

        except exceptions.CosmosResourceExistsError:
            db = client.get_database_client(DATABASE_ID)
            logging.info('Database with id \'{0}\' was found'.format(DATABASE_ID))

        # setup container for this sample
        try:
            container = db.create_container(id=CONTAINER_ID, partition_key=PartitionKey(path='/partitionKey'))
            logging.info('Container with id \'{0}\' created'.format(CONTAINER_ID))

        except exceptions.CosmosResourceExistsError:
            container = db.get_container_client(CONTAINER_ID)
            logging.info('Container with id \'{0}\' was found'.format(CONTAINER_ID))

        scale_container(container)
        create_items(container)
        read_items(container)
        read_item(container, 'SalesOrder1', 'Account1')
        query_items(container, 'Account1')
        replace_item(container, 'SalesOrder1', 'Account1')
        upsert_item(container, 'SalesOrder1', 'Account1')
        delete_item(container, 'SalesOrder1', 'Account1')

        try:
            client.delete_database(db)
            logger.info('DB deleted')

        except exceptions.CosmosResourceNotFoundError:
            pass

    except exceptions.CosmosHttpResponseError as e:
        logging.error('\nrun_sample has caught an error. {0}'.format(e.message))

    finally:
        logging.info("\nrun_sample done")

if __name__ == '__main__':
    logger.info('Running demo app')
    run_sample()

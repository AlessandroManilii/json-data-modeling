import json
import sqlite3
import sql_interface
import datetime

# JSON parsing and extraction 

def parse_json_file(json_path: str) -> list[dict]:
    with open(json_path, 'r') as json_file:
        return json.load(json_file)['events']


def extract_events(events: list[dict]) -> (list[dict]):

    """
        For each event both metadata and data are read, collected and organized in a dict
    """

    formatted_events = []

    for event in events:

        event = event['_source']

        # select relevant fields
        action = event['eventType'] # create, delete, update
        source = event['eventSource'] # PROVISIONING, TRANSACTIONS, DEVICE MGMT
        data_type = event['eventDataType'] # ORGANIZATION, MERCHANT, LOGICAL_DEVICE, DEPLOYMENT, CAPTURE
        event_datetime = event['eventDateTime']
        data = event['eventData']

        format_data = {}
        match data_type:
            case 'ORGANIZATION':
                data_type = 'organizations'
                format_data = {
                    "organization_id": data.get("id"),
                    "organization_name": data.get("name"),
                    "parent_id": data.get("parent", {}).get("Id"),
                    "address" : data.get("location", {}).get("address"),
                    "city" : data.get("location", {}).get("city"),
                    "zipCode" : data.get("location", {}).get("zipCode"),
                    "state" : data.get("location", {}).get("state"),
                    "country" : data.get("location", {}).get("country")
                }

            case 'MERCHANT':
                data_type = 'merchants'
                format_data = {
                    "merchant_id": data.get("id"),
					"organization_id": data.get("parent", {}).get("id"),
				    "merchant_name": data.get("name"),
					"address" : data.get("location", {}).get("address"),
                    "city" : data.get("location", {}).get("city"),
                    "zipCode" : data.get("location", {}).get("zipCode"),
                    "state" : data.get("location", {}).get("state"),
                    "country" : data.get("location", {}).get("country"),
                    "merchant_category_code" : data.get("merchantCategoryCode")
                }

            case 'LOGICAL_DEVICE': 
                data_type = 'devices'
                format_data = {
                    "device_id": data.get("id"),
					"merchant_id": data.get("parent", {}).get("Id"),
				    "device_name": data.get("name"),
					"device_reference" : data.get("reference")
                }

            case 'DEPLOYMENT':
                data_type = 'device_updates'
                format_data = {
                    "deployment_id": data.get("deploymentId"),
                    "deployment_name": data.get("deploymentName"),
                    "device_id": data.get("devicesTarget", {})[0].get("logicalDeviceId"),
                    "status": data.get("status")
                }

            case 'CAPTURE':
                data_type = 'transactions'
                format_data = {
                    "transaction_id": data.get("requestId"),
                    "merchant_name": data.get("merchantData", {}).get("merchantName"),
                    "device_reference": data.get("deviceReference"),
                    "payment_type" : data.get("paymentMethod", {}).get("paymentType"),
                    "transaction_value" : data.get("transactionData", {}).get("totalAmount", {}).get("value")
                }

        formatted_events.append({'data_type':data_type, 'action':action, 'data':format_data, 'datetime':event_datetime}) 
    return formatted_events


def route_events_to_sql(events: list[dict], connection: sqlite3.Connection):

    """
        This function routes events to the correspondant SQl command based on the action type
    """

    for event in events:
        match event['action']:
            case 'CREATE': sql_interface.load(event, connection)
            case 'UPDATE': sql_interface.update(event, connection)
            case 'DELETE': sql_interface.delete(event, connection)


# main program
if __name__ == "__main__":

    events = parse_json_file('input.json')
    formatted_events = extract_events(events)

    # define the database and establish a connection
    connection = sqlite3.connect('events.db')
    # create tables
    sql_interface.create_tables(connection)

    # order events list based on timestamp
    events_sorted = sorted(formatted_events, key=lambda x: x['datetime'])

    # route event to sql
    route_events_to_sql(formatted_events, connection)
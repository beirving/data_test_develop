import os
import csv
import urllib2
import datetime
import collections
import xml.etree.ElementTree as eTree


def download_file(url, file_name='downloaded_xml_data.xml'):
    """
    Download a file from an external source and save locally
    :param url: str
        Valid url for XML
    :param file_name: str
        Set location for file to be downloaded
        Default CWD/downloaded_xml_data.xml
    :return:  str : file location
    """
    source = urllib2.urlopen(url)
    contents = source.read()
    file_handler = open(file_name, 'w')
    file_handler.write(contents)
    file_handler.close()
    return os.path.realpath(file_name)


def check_valid_year(check_date, target_year=2016):
    """
    check if the date given is valid for the target year
    :param check_date: str
    :param target_year: str
    :return: bool
    """
    start = datetime.datetime(target_year, 1, 1)
    end = datetime.datetime(target_year, 12, 31, 23, 59, 59)
    date = datetime.datetime.strptime(check_date, '%Y-%m-%d %H:%M:%S')
    if date > end:
        return False
    if date < start:
        return False
    return True


def check_description(description, check_term=' and '):
    """
    Check if the first argument contains the 2nd argument
    :param description: str
    :param check_term: str
    :return: bool
    """
    if description.find(check_term) >= 0:
        return True
    return False


def listing_valid(listing_iterator_item):
    """
    Helper function to clean up parse_file function
    Runs check_valid_year and check_description under default params
    :param listing_iterator_item: xml.etree.ElementTree.Element
    :return: bool
    """
    listing_details = listing_iterator_item.find('ListingDetails')
    date_result = check_valid_year(listing_details.find('DateListed').text)
    if date_result is False:
        return date_result
    basic_details = listing_iterator_item.find('BasicDetails')
    return check_description(basic_details.find('Description').text)


def join_sub_nodes(main_node, term):
    """
    Outputs a comma separated string of the "term" node values
    :param main_node: xml.etree.ElementTree.Element
    :param term: str
    :return: str
    """
    if main_node is None:
        return ''
    else:
        node_items = main_node.findall(term)
        if node_items is None:
            return ''
        else:
            output_list = []
            for node_item in node_items:
                output_list.append(node_item.text)
        return ','.join(output_list)


def get_get_fields(listing_iterator_item):
    """
    Collect desired node values from xml
    :param listing_iterator_item: xml.etree.ElementTree.Element
    :return: collections.OrderedDict
    """
    output = collections.OrderedDict()
    listing_details = listing_iterator_item.find('ListingDetails')
    location_details = listing_iterator_item.find('Location')
    basic_details = listing_iterator_item.find('BasicDetails')
    rich_details = listing_iterator_item.find('RichDetails')

    output['MlsId'] = listing_details.find('MlsId').text
    output['MlsName'] = listing_details.find('MlsName').text

    output['DateListed'] = listing_details.find('DateListed').text

    output['StreetAddress'] = location_details.find('StreetAddress').text

    output['Price'] = listing_details.find('Price').text
    output['Bedrooms'] = basic_details.find('Bedrooms').text

    # this is producing no values
    # at this point I would talk with stake holders for clarifications on which nodes are important
    # lets talk about the process for getting more information on issues like this
    output['Bathrooms'] = basic_details.find('Bathrooms').text

    # this would be code to switch to use FullBathrooms, HalfBathrooms, ThreeQuarterBathrooms nodes
    # bathrooms = 0
    # bathrooms += int(0 if basic_details.find('FullBathrooms').text is None else basic_details.find('FullBathrooms').text)
    # bathrooms += int(0 if basic_details.find('HalfBathrooms').text is None else basic_details.find('HalfBathrooms').text)
    # bathrooms += int(0 if basic_details.find('ThreeQuarterBathrooms').text is None else basic_details.find('ThreeQuarterBathrooms').text)
    # output['Bathrooms'] = bathrooms
    #   Humorous result:
    #       the listing for 1110 Felbar Avenue has 102 bathrooms
    #       due to the xml having <HalfBathrooms>99</HalfBathrooms>

    output['Appliances'] = join_sub_nodes(rich_details.find('Appliances'), 'Appliance')
    output['Rooms '] = join_sub_nodes(rich_details.find('Rooms'), 'Room')

    # truncate to the 200th character
    description = basic_details.find('Description').text
    output['Description'] = description[0:200]
    return output


def write_listing_to_csv(listing_order_dict, file_name='output'):
    """
    Write the given dict data to the given csv
    :param listing_order_dict: collections.OrderedDict
    :param file_name: str
    :return: void
    """
    file_location = file_name+".csv"
    write_header = True
    if os.path.isfile(file_location) is True:
        write_header = False

    with open(file_location, 'ab') as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(listing_order_dict.keys())
        writer.writerow(listing_order_dict.values())


def parse_and_save(local_file_location):
    """
    Iterate through given local xml file line by line and write to default csv location
    :param local_file_location: str
    :return: void
    """
    context = eTree.iterparse(local_file_location)
    for event, element in context:
        if event == "end" and element.tag == 'Listings':
            for listing in element:
                if listing_valid(listing):
                    listing_fields = get_get_fields(listing)
                    write_listing_to_csv(listing_fields)


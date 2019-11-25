import os
import xml
import pytest
import collections
import parseXmlSaveCsv
from mock import Mock, patch


@pytest.fixture(scope='function')
def mock_xml_element():
    mock_element = Mock(spec=xml.etree.ElementTree.Element)
    mock_text = Mock()
    mock_text.text = 'string'
    mock_element.find.return_value = mock_text
    mock_element.tag.return_value = 'Listings'
    return mock_element


@patch('parseXmlSaveCsv.urllib2.urlopen')
def test_download_file_will_pass(mock_urlopen):
    test_path = os.path.dirname(os.path.realpath(__file__))+'\\test.xml'
    mock = Mock()
    mock.read.side_effect = ['mock_contents1']
    mock_urlopen.return_value = mock
    result = parseXmlSaveCsv.download_file('http://test.com', 'test.xml')
    assert type(result) is str
    assert result == test_path
    os.remove(result)


@patch('parseXmlSaveCsv.urllib2.urlopen')
def test_download_file_will_fail(mock_urlopen):
    test_path = os.path.dirname(os.path.realpath(__file__))+'\\test_fail.xml'
    mock = Mock()
    mock.read.side_effect = ['mock_contents1']
    mock_urlopen.return_value = mock
    result = parseXmlSaveCsv.download_file('http://test.com', 'test.xml')
    assert result is not test_path
    os.remove(result)


def test_check_description_will_pass():
    result = parseXmlSaveCsv.check_description('this test will pass', 'pass')
    assert result


def test_check_description_will_fail():
    result = parseXmlSaveCsv.check_description('this test will pass', 'fail')
    assert result is False


def test_check_valid_year_will_pass():
    result = parseXmlSaveCsv.check_valid_year('2019-05-15 13:29:45', 2019)
    assert result


def test_check_valid_year_will_fail():
    result = parseXmlSaveCsv.check_valid_year('2019-05-15 13:29:45', 2018)
    assert result is False


@patch("parseXmlSaveCsv.check_valid_year", return_value=True)
@patch("parseXmlSaveCsv.check_description", return_value=True)
def test_listing_valid_will_pass(mock_check_year, mock_check_description, mock_xml_element):
    result = parseXmlSaveCsv.listing_valid(mock_xml_element)
    assert mock_check_year.called
    assert mock_check_description.called
    assert result


@patch("parseXmlSaveCsv.check_valid_year", return_value=False)
def test_listing_valid_will_fail_check_year(mock_check_year, mock_xml_element):
    result = parseXmlSaveCsv.listing_valid(mock_xml_element)
    assert mock_check_year.called
    assert result is False


@patch("parseXmlSaveCsv.check_valid_year", return_value=True)
@patch("parseXmlSaveCsv.check_description", return_value=False)
def test_listing_valid_will_fail_check_description(mock_check_year, mock_check_description, mock_xml_element):
    result = parseXmlSaveCsv.listing_valid(mock_xml_element)
    assert mock_check_year.called
    assert mock_check_description.called
    assert result is False


def test_join_sub_nodes_will_pass(mock_xml_element):
    mock_text = Mock()
    mock_text.text = 'string'

    mock_xml_element.findall.return_value = [mock_text, mock_text]

    result = parseXmlSaveCsv.join_sub_nodes(mock_xml_element, 'test')
    assert result == 'string,string'


def test_join_sub_nodes_will_fail_main_node_is_none():
    result = parseXmlSaveCsv.join_sub_nodes(None, 'test')
    assert result == ''


def test_join_sub_nodes_will_fail_main_node_find_all_is_none(mock_xml_element):
    mock_xml_element.findall.return_value = None
    result = parseXmlSaveCsv.join_sub_nodes(mock_xml_element, 'test')
    assert result == ''


@patch("parseXmlSaveCsv.join_sub_nodes", return_value='string')
def test_get_fields_will_pass(mock_join_sub_nodes, mock_xml_element):
    mock_element = Mock(spec=xml.etree.ElementTree.Element)
    mock_element.find.return_value = mock_xml_element
    result = parseXmlSaveCsv.get_get_fields(mock_element)
    assert mock_join_sub_nodes.called
    assert type(result) is collections.OrderedDict


def test_write_listing_to_csv_will_pass():
    test_path = os.path.dirname(os.path.realpath(__file__)) + '\\test.csv'
    mock_dict = collections.OrderedDict()
    mock_dict['header'] = 'value'
    parseXmlSaveCsv.write_listing_to_csv(mock_dict, 'test')
    assert os.path.isfile('test.csv')
    os.remove(test_path)

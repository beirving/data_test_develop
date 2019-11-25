import parseXmlSaveCsv

# set target xml feed
challenge_url = 'http://syndication.enterprise.websiteidx.com/feeds/BoojCodeTest.xml'
# download xml feed to local file
local_file = parseXmlSaveCsv.download_file(challenge_url)
# parse xml and save as csv
parseXmlSaveCsv.parse_and_save(local_file)

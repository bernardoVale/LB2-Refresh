__author__ = 'bernardovale'
import json

import json
from pprint import pprint
json_data=open('/Users/bernardovale/Documents/LB2/scripts/lb2_refresh/config.json')

data = json.load(json_data)
pprint(data)
json_data.close()

# Cryptopia python API by CC Tech
Originally made by The Bot Guy (thebotguy@protonmail.com)
Ported to Python 3 by segfaultsourcery.

## Overview
This wrapper provides a friendly way to call Cryptopia API from a Python 3 script. Requires requests.

## Usage
Just import it and use it.
``` python
from cryptopia_api import Api, CryptopiaAPIException

#later...
api_wrapper = Api(MY_PUBLIC_KEY, MY_SECRET_KEY)

try:
    #call a request to the api, like balance in BTC...
    print("Your balance:", api_wrapper.get_balance('BTC'))
except CryptopiaAPIException as exception:
    print("Error:", exception)
```

# Donate
Feel free to donate:

| METHOD 	| ADDRESS                                   	|
|--------	|--------------------------------------------	|
| ETH    	| 0x8E511f7CCCEA6a70bb8B728191306F5d1b2a74C1 	|

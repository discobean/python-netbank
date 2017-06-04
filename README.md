# python-netbank
Netbank wrapper for python

Example:

```
#!/usr/bin/env python2.7
from netbank.api import Netbank
import json

def strip(string):
    return string.strip().replace("\n", ' ')

nb = Netbank()

account_list = nb.login('login', 'password')

transactions = nb.get_transactions(account_list[0], "30/05/2017", "")

for tx in transactions:
    amount = 0
    if tx["SortableAmount"]["Sort"][0] == 2:
        amount = tx["SortableAmount"]["Sort"][1]
    elif tx["SortableAmount"]["Sort"][0] == 1:
        amount = 0 - tx["SortableAmount"]["Sort"][1]

    print "%-12s%-7s%-14s%-80s%20s%20s" % (
            strip(tx["Date"]["Text"]),
            strip(tx["TranCode"]["Text"]),
            strip(tx["ReceiptNumber"]["Text"]),
            strip(tx["Description"]["Text"]),
            strip(tx["SortableAmount"]["Text"]),
            amount
            )
```

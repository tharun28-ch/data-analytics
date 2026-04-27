import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules

data = {
'TransactionID': [1, 1, 1, 2, 2, 3, 3, 3, 4, 4, 5, 5],
'Activity': ['Coding', 'Chess', 'Pizza', 'Coding', 'Chess',
'Hiking', 'Photography', 'Pizza', 'Hiking', 'Photography', 'Coding',
'Pizza']
}

df = pd.DataFrame(data)

basket = (df.groupby(['TransactionID', 'Activity'])['Activity']
.count().unstack().reset_index().fillna(0)
.set_index('TransactionID'))

def encode_units(x):
    return 1 if x >= 1 else 0

basket_sets = basket.map(encode_units)
print(basket_sets.head())

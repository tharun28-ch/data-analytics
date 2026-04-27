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

frequent_itemsets = apriori(basket_sets, min_support=0.2, use_colnames=True)

rules = association_rules(frequent_itemsets, metric="lift", min_threshold=1.2)

rules = rules.sort_values('confidence', ascending=False)

print(rules[['antecedents', 'consequents', 'support', 'confidence', 'lift']].head())

import pandas as pd
df1 = pd.read_csv('./data/es_algolia_788741.tsv', sep='\t', header=0)
df2 = pd.read_csv('./data/im_poc_810366_1day.tsv', sep='\t', header=0)



df2 = df2['query', 'suggestion', 'order_count']
df2['sugg_count'] = df2.groupby('query')['suggestion'].transform('count')


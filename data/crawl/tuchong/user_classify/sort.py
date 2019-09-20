import pandas as pd
import re

common = pd.read_csv('common.csv', names=['id'])
special = pd.read_csv('special.csv', names=['id', 'url'])
empty = pd.read_csv('empty.csv', names=['id'])

df_name_s = ['common', 'special', 'empty']

for df_name in df_name_s:
    exec('{0:s}.sort_values("id").to_csv("{0:s}.csv", index=False)'.format(df_name))
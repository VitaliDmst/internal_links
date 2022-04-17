import pandas as pd
from bs4 import BeautifulSoup
import re
from nltk import ngrams
import string

df = pd.read_csv('data/hd_html.csv')
df = df.rename(columns={
    'Address': 'url',
    'text-body 1': 'html'})

# keywords = pd.read_csv('data/kw.csv')
# keywords = keywords.rename(columns={
#     'Address': 'url',
#     'Unnamed 6': 'kw'})
#
# all_data = df.join(keywords.set_index('url'), on='url', how='left')[['url', 'html', 'kw']]
# all_data = all_data.rename(columns={
#     'Unnamed 6': 'kw'
# })

# semrush


semrush_data = pd.read_csv('data/semrush_kw.csv')
#semrush normalization
semrush_kw = pd.DataFrame({
    'url': [],
    'kw': []
})
for page, page_data in semrush_data.groupby(by='URL', dropna=True, as_index=False)['Keyword']:
    semrush_kw= semrush_kw.append({
        'url': page,
        'kw': ','.join(page_data['Keyword'])
    }, ignore_index=True)

all_data = df.join(semrush_kw.set_index('url'), on='url', how='outer')[['url', 'html', 'kw']]
all_data = all_data.dropna(how='all')

result = pd.DataFrame({
    'From': [],
    'To': [],
    'Anchor': []
})

# for i in all_data.iterrows():
#     print(i)

for index, row in all_data.iterrows():
    try:
        soup = BeautifulSoup(row['html'], 'html.parser')
        # text normalization removing \n and spaces, and removing punctiations
        text = re.sub('\n', '', soup.text.strip())
        text = text.translate(str.maketrans('','',string.punctuation))

        for ind, i in all_data.iterrows():
            link_from = row['url']
            link_to = i['url']
            kw = i['kw']
            try:
                for keyword in kw.split(','):
                    kw_len = len(keyword.split())
                    grams = [' '.join(q) for q in ngrams(text.split(), kw_len)]
                    if keyword in grams and link_from != link_to:
                        result = result.append({
                            'From': link_from,
                            'To': link_to,
                            'Anchor': keyword
                        }, ignore_index=True)
                        # print(link_from, link_to, keyword)
                        # print(result)
            except:
                pass
    except:
        pass

result.to_csv('result.csv')
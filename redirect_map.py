import difflib
from urllib.parse import urlparse
import pandas as pd

# old = list(pd.read_csv('redirect_data/cryomed_old.csv')['Address'])
# new = list(pd.read_csv('redirect_data/cryomed_new.csv')['Address'])

old = pd.read_csv('redirect_data/cryomed_old.csv')
new = pd.read_csv('redirect_data/cryomed_new.csv')

def get_page_name(url):
    try:
        path_last = urlparse(url).path
        if path_last[-1] != '/':
            return path_last[path_last.rindex('/', 0, len(path_last) - 1):]
        else:
            return url[url.rindex('/', 0, len(url) - 1):]
    except:
        pass

def create_redirects_map(old: pd.DataFrame,
                         new: pd.DataFrame,
                         output_filename: str,
                         same_domain: bool = True,
                         indexation_status: bool = False
                         ):
    """
    Function parse 2 screaming frog crawl files and create new in csv format with redirect map that contains 2 columns From and To,
    second column can contain multiple values, comma separated and should be splitted at following steps (use =SPLIT() in sheets)

    :param old: read crawl data from old site
    :param new: read crawl data from new site
    :param same_domain: if new domain links will be absolute by default True
    :param indexation_status: by default False, set True if old domain crawl contains URL inspection data
    :param output_filename: path and name for output file, csv format
    :return:
    """


    if indexation_status == True:
        old = list(old[(old['Status Code'] == 200) &
                  ((old['Coverage'] == 'Submitted and indexed') |
                  (old['Coverage'] == 'Indexed, not submitted in sitemap'))]['Address'])
        new = list(new['Address'])
    else:
        old = list(old['Address'])
        new = list(new['Address'])

    result = pd.DataFrame({
        'From': [],
        'To': []
    })

    zip_old = dict(zip(list(map(get_page_name, old)), old))
    zip_new = dict(zip(list(map(get_page_name, new)), new))

    if not same_domain:
        for page, full_url in zip_old.items():
            # old_page = urlparse(zip_old[page])
            new_pages = [urlparse(zip_new[i]).path for i in difflib.get_close_matches(page, zip_new)]

            result = result.append({
                'From': full_url,
                'To': ",".join([zip_new.get(e) for e in map(get_page_name, new_pages)
                                if zip_new.get(e) != None])
            }, ignore_index=True)
    else:
        for page in zip_old:

            old_page = urlparse(zip_old[page]).path
            new_page = ",".join([urlparse(zip_new[i]).path for i in difflib.get_close_matches(page, zip_new)])
            if new_page == "":
                new_page = "same"

            result = result.append({
                'From': old_page,
                'To': new_page
            }, ignore_index=True)

    result.dropna(thresh=2)
    result.to_csv(f'{output_filename}.csv')
    # print(result)

create_redirects_map(new, old, 'qe', False, True)






# for page in zip_old:
#     old_page = urlparse(zip_old[page]).path
#     new_page = ",".join([urlparse(zip_new[i]).path for i in difflib.get_close_matches(page, zip_new)])
#     # new_page = [urlparse(zip_old[i]).path for i in difflib.get_close_matches(page, zip_old)]
#
#     if new_page == "":
#         new_page = "same"
#
#     result = result.append({
#         'From': old_page,
#         'To': new_page
#     }, ignore_index=True)
#
#
# # print(result)
# result.to_csv('redirect_map.csv')

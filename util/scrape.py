"""
Utilities module containing functions to scrape fanfic metadata and text from
Archive of Our Own (https://archiveofourown.org/), also known as AO3.

@author Andrew Zhou
@updated Nov 7 2020
"""

from bs4 import BeautifulSoup
import requests
import re
import string
import time
import pandas as pd
import numpy as np
from collections import defaultdict

sleep = 5


def get_search_mod(mod, value):
    return f"&work_search[{mod}]={value}"

def get_search_url(fandom, min_kudos=0, complete=True, single_only=False, crossover=False, english_only=True):

    base_url = "https://archiveofourown.org/works/search?utf8=✓"

    params = {}

    complete =  ("complete", "T" if complete else "")
    crossover = ("crossover", "" if crossover else "F")
    fandom = ("fandom_names", fandom)
    single_chapter = ("single_chapter", 1 if single_only else "")
    language = ("language_id", "en" if english_only else "")
    kudos = ("kudos_count", f">{min_kudos}")
    sort_by = ("sort_column", "created_at")
    sort_order = ("sort_direction", "desc")

    params = [complete, crossover, fandom, single_chapter, language, kudos, sort_by, sort_order]

    return base_url + ''.join([get_search_mod(*param) for param in params])


def get_works_info(search_url, count, page=1, single_only=False, word_range=(0,0), include_adult=False, exclude_series=True, print_every=5):
    '''
    Given the URL of an AO3 search query, extracts the work ID and data for
    the first {count} works.
    '''
    

    url_page = search_url if page == 1 else search_url + "&page=" + str(page)

    r = requests.get(url_page, headers="")
    html = r.text
    soup = BeautifulSoup(html, 'html.parser')
    info_list = soup.find_all(class_="blurb")

    if page == 1:
        num_found_html = soup.find(text=re.compile(r'\d+ Found'))
        num_found = re.match('(\d+) Found', str(num_found_html)).groups()[0]
        print(f"{num_found} potential matches found")
        
    if page % print_every == 1:
        print(f"getting page {page}, {count} works left")
    
    if not info_list:
        print(f"ran out of fics with {count} left")
        return []
    work_info = [parse_meta_list(info_html) for info_html in info_list]
    
    work_info = [x for x in work_info if match_conditions(x, single_only, word_range, include_adult, exclude_series)]

    if count <= len(work_info):
        print("finished")
        return work_info[:count]
    time.sleep(sleep)
    return work_info + get_works_info(search_url, count-len(work_info), page+1, single_only=single_only, word_range=word_range)

def match_conditions(info, single_only, word_range, include_adult, exclude_series):
    if info["lang"] != "English":
        return False
    if single_only and info["chapters"] != 1:
        return False
    if info["words"] < word_range[0] or (word_range[1] and info["words"] > word_range[1]):
        return False
    if include_adult == False and (info["rating"] == "mature" or info["rating"] == "explicit"):
        return False
    if exclude_series and info["series"]:
        return False
    return True

def get_id_from_heading(heading_html):
    link = heading_html.find("a")
    if link:
        return link['href'].split("/")[2]

def parse_meta_list(info_html):
    work_id = info_html.get("id").split("_")[1]
    rating = info_html.find(class_="rating").get("class")[0].split("-")[1]
    lang = info_html.find_all(class_="language")[1].text
    words = int(info_html.find_all(class_="words")[1].text.replace(",", ""))
    chapters = int(info_html.find_all(class_="chapters")[1].text.split("/")[0])
    series_html = info_html.find(class_="series")
    author_html = info_html.find_all(rel="author")
    
    if author_html:
        author = author_html[0].text
        all_authors = list(map(lambda x: x.text, author_html))
    else:
        # sometimes there's no author and our find_all fails
        author = "Anonymous"
        all_authors = []
        
    series = {}
    if series_html:
        match = re.search(r".*Part (\d+) of (.+)", series_html.text)
        series["part"], series["name"] = match.groups()
    
    date = info_html.find(class_="datetime").text
    return {"work_id": work_id, "rating": rating, "lang": lang, "words": words, "chapters": chapters, "date": date, "series": series, "author": author, "all_authors": all_authors}

def chap_html_to_str(chap_html):
    all_p = chap_html.find_all("p")
    str_arr = list(map(lambda x: str(x.text).replace("\xa0", " "), all_p))
    str_arr = [st for st in str_arr if st]
    return ' '.join(str_arr)

def scrape_fic(work_id, as_pd_series=True, no_text=False):
    '''
    Scrape information for a single fanfiction, optionally returning as dict or Series.
    '''
    url = 'http://archiveofourown.org/works/' + str(work_id) + "?view_full_work=true?view_adult=true"

    r = requests.get(url)
    html = r.text
    soup = BeautifulSoup(html, 'html.parser')

    title = soup.find(class_="title").text.strip()

    authors_html = soup.find_all(rel="author")
    if authors_html:
        author = authors_html[0].text
        all_authors = list(map(lambda x: x.text, authors_html))
    else:
        author = "Anonymous"
        all_authors = []

    if not no_text:
        chaps_html = soup.find("div", id="chapters").find_all(class_="userstuff")
        chaps_clean = list(map(chap_html_to_str, chaps_html))
        chaps_clean = " ".join(chaps_clean)
    else:
        chaps_clean = ""
    
    meta_html = soup.find(class_="meta")
    meta_info = parse_meta_fic(meta_html)
    
    full_dict = {"title": title, "text": chaps_clean, "author": author, "all_authors": all_authors, **meta_info}

    return pd.Series(full_dict) if as_pd_series else full_dict

def parse_meta_fic(meta_html):
    reln_tags = []
    char_tags = []
    addl_tags = []
    series = {}
    
    reln_tags_html = meta_html.find_all(class_="relationship tags")
    if len(reln_tags_html) >= 2:
        reln_tags_html = reln_tags_html[1].find_all(class_="tag")
        reln_tags = list(map(lambda x: x.text, reln_tags_html))

    char_tags_html = meta_html.find_all(class_="character tags")
    if len(char_tags_html) >= 2:
        char_tags_html = char_tags_html[1].find_all(class_="tag")
        char_tags = list(map(lambda x: x.text, char_tags_html))

    series_html = meta_html.find_all(class_="series")
    if series_html:
        series_txt = series_html[1].find(class_="position").text
        match = re.match(r"Part (\d+) of the (.+) series", series_txt)
        series["part"], series["name"] = match.groups()

    addl_tags_html = meta_html.find_all(class_="freeform tags")
    if len(addl_tags_html) >= 2:
        addl_tags_html = addl_tags_html[1].find_all(class_="tag")
        addl_tags = list(map(lambda x: x.text, addl_tags_html))

    return {"relationships": reln_tags, "chars": char_tags, "tags": addl_tags, "series": series}


def scrape_fic_list(info_list, partial_df = None, print_every=0):
    '''
    Scrapes a list of fanfictions based on information from get_works_info.
    If interrupted, returns a partial result. Can be resumed by passing in that
    partial result on a subsequent call.
    '''
    if print_every:
        print("beginning scrape...")
    
    count = 0
    skipped = 0
        
    partial_scrape = []
    if type(partial_df) == pd.DataFrame:
        partial_scrape = partial_df["work_id"].values
     
    # assume we pass in at least one element
    info_keys = list(info_list[0].keys())
    full_dict = defaultdict(list)
    
    for fic_info in info_list:
        try:
            if fic_info["work_id"] in partial_scrape:
                skipped += 1
                continue

            if print_every and count % print_every == 0:
                print(f"scraping fic {count+1}/{len(info_list)}")

            fic_dict = scrape_fic(fic_info["work_id"], as_pd_series=False)

            
            for key, value in fic_info.items():
                full_dict[key].append(value)
            
            # handle potential overlaps depending on how much info we pass in
            for key, value in fic_dict.items():
                if key not in info_keys:
                    full_dict[key].append(value)
            count += 1

            time.sleep(sleep)
        except Exception as e:
            # should be no exception in dict appending
            print(f"Error encountered, ending scrape at {count}/{len(info_list)} works processed")
            print(e)
            break
        except KeyboardInterrupt:
            print("Scraping interrupted")
            num_scraped = count - skipped
            for key, value in full_dict.items():
                this_length = len(value)
                if this_length != num_scraped:
                    print("Last fic data incomplete, attempted to correct but should examined")
                    # should have one extra element from the interrupt during appending to full_dict 
                    # if not, serious error
                    assert(this_length == num_scraped+1)
                    full_dict[key] = value[:-1]
            break

    full_df = pd.DataFrame.from_dict(full_dict)
    if type(partial_df) == pd.DataFrame:
        full_df = pd.concat([partial_df, full_df], ignore_index=True)
            
    return full_df
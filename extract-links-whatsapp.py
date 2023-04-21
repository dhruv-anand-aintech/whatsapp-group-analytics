import pandas as pd
import numpy as np
from tqdm import tqdm
import re
import requests
from bs4 import BeautifulSoup
from collections import Counter

chat_file_name = "path/to/chat/WhatsApp Chat with blah.txt"
text = open(chat_file_name, "r").read()
# extract all urls from the text into a list, along with the rest of the text (in previous line as well) in the message in a list of tuples

urls = re.findall(
    "http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
    text,
)
# put into a dataframe
df = pd.DataFrame({"url": urls})

# get context of the url by finding the text between timestamp lines (4/5/23, 6:41 PM)
# split the text into lines
lines = text.splitlines()
# find the indices of the lines that contain the url
url_indices = {}
for url in urls:
    for i, line in enumerate(lines):
        if url in line:
            url_indices[url] = i


# get the context of the url by finding the text between timestamp lines (4/5/23, 6:41 PM)
def get_context(url):
    # get the index of the line that contains the url
    inp_index = url_indices[url]
    index = inp_index
    while index > 0:
        index -= 1
        # if the line contains a timestamp, then the previous line contains the context
        if re.match(r"\d{1,2}\/\d{1,2}\/\d{1,2}, \d{1,2}:\d{1,2} [AP]M", lines[index]):
            # return lines from this line to the line that contains the url
            pre_context = lines[index:inp_index]
            break
    # get the index of the line that contains the url
    index = inp_index
    while index < len(lines):
        index += 1
        # if the line contains a timestamp, then the next line contains the context
        if re.match(r"\d{1,2}\/\d{1,2}\/\d{1,2}, \d{1,2}:\d{1,2} [AP]M", lines[index]):
            # return lines from this line to the line that contains the url
            post_context = lines[inp_index:index]
            break
    return pre_context + post_context


# get context of the url for each url in the dataframe
df["context"] = df["url"].apply(get_context)
df.to_excel("path/to/chat/whatsapp-links-context.xlsx")
# get title of the url


def get_title(url):
    try:
        # get only head of the page to reduce time
        page = requests.get(url, stream=True, timeout=5)
        soup = BeautifulSoup(page.content, "html.parser")
        title = soup.find("title").text
        return title
    except:
        return ""


# get title of the url for each url in the dataframe using apply and tqdm
tqdm.pandas()
df["title"] = df["url"].progress_apply(get_title)
df.to_excel("path/to/chat/whatsapp-links-context-titles.xlsx")
urls = re.findall(
    "http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
    text,
)
# standardize the urls by converting them to lowercase and removing trailing slashes and anything after #
urls = [url.lower().split("#")[0].rstrip("/") for url in urls]


# count the number of times each url appears in the list
url_counts = Counter(urls)

# convert the url_counts dictionary into a pandas dataframe
url_counts_df = pd.DataFrame.from_dict(url_counts, orient="index").reset_index()
url_counts_df.columns = ["url", "count"]

# sort the dataframe by the count column
url_counts_df = url_counts_df.sort_values(by="count", ascending=False)

# print the top 10 urls with word wrap
pd.set_option("display.max_colwidth", None)
# put this in a excel file
url_counts_df.to_excel("path/to/chat/links.xlsx", index=False)

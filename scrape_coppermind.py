from random import uniform
from time import sleep
import requests
from bs4 import BeautifulSoup
import os


base_url = 'https://coppermind.net'
fetch_sleep_min = .5
fetch_sleep_max = 10.00

script_dir = os.path.dirname(__file__)
page_dir = os.path.join(script_dir, 'coppermind')

pages_file = 'all_pages.txt'

try:
    os.mkdir(page_dir)
except FileExistsError as error:
    print(page_dir + ' exists')
except OSError as error:
    print(error)

def make_request(path):
    url = base_url + path
    print('Fetching: ' + url)
    r = requests.get(base_url + path)
    sleep(uniform(fetch_sleep_min, fetch_sleep_max))
    return r.text

def collect_all_pages():
    next_page = '/wiki/Special:AllPages'

    all_pages = []

    while next_page is not None:
        page = make_request(next_page)
        soup = BeautifulSoup(page, 'lxml')
        page_links_div = soup.find(class_='mw-allpages-nav')
        if page_links_div is not None:
            print(page_links_div)
            page_links = page_links_div.find_all('a')
            found = False
            for page_link in page_links:
                if 'Next page' in page_link.text:
                    next_page = page_link.get('href')
                    found = True
            if not found:
                next_page = None
        else:
            next_page = None

        allpages_body = soup.find(class_='mw-allpages-body')
        if allpages_body is not None:
            content_page_links = allpages_body.find_all('a')
            for content_page_link in content_page_links:
                content_link = content_page_link.get('href')
                all_pages.append(content_link)
                print("\tFound: " + content_link)

    return all_pages

def write_page(page, force = False):
    filename = page.replace('/wiki/', '').replace('/', '-').replace(':', '-')
    output_filename = os.path.join(page_dir,  filename + '.htm')
    if os.path.exists(output_filename) and not force:
        print('File exists: ' + output_filename)
    else:
        page_htm = make_request(page)
        print('Writing: ' + output_filename)
        with open(output_filename, 'w') as page_file:
            page_file.write(page_htm)

def write_page_list(pages):
    with open(pages_file, 'w') as file:
        for page in pages:
            print('Writing: ' + page )
            file.write(page + "\n")

print('Starting coppermind scraper')

all_pages = []
try:
    with open(pages_file, 'r') as f:
        for line in f:
            all_pages.append(line.strip())
except FileNotFoundError:
    print('Collecting Pages')
    all_pages = collect_all_pages()
    print('Writing Collected Pages')
    write_page_list(all_pages)

print('Collected ' + str(len(all_pages)) + ' pages')

for page in all_pages:
    write_page(page)

print('Complete')

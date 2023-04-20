import requests
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs

def scrape_links(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a', href=True)
        filtered_links = []

        for link in links:
            href = link['href']
            if '/bajnoksagok/' in href or '=floorball_matches&year' in href:
                # Properly join the base URL with the relative link
                full_url = urljoin(url, href)
                filtered_links.append((full_url, link.text))

        return filtered_links
    else:
        print(f"Error: Failed to load the page (status code {response.status_code})")
        return []

def scrape_options(links):
    grouped_options = {}

    for link, link_text in links:
        response = requests.get(link)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            select_element = soup.find('select', {'name': 'ch_id', 'id': 'ch_id', 'class': 'form-control select-red'})

            if select_element:
                options = select_element.find_all('option')
                options_list = [(option['value'], option.text) for option in options]
                grouped_options[link_text] = options_list

    return grouped_options

def create_option_url(base_url, ch_id, year):
    return urljoin(base_url, f"index.php?ch_id={ch_id}&pg=floorball_matches&year={year}")

url = "http://hunfloorball.hu/"
filtered_links = scrape_links(url)
grouped_options = scrape_options(filtered_links)

print("Grouped option values, strings, and URLs:")
for link_text, options_list in grouped_options.items():
    print(f"{link_text}:")
    for link, (value, text) in zip(filtered_links, options_list):
        # Extract the 'year' parameter value from the filtered link
        year = parse_qs(urlparse(link[0]).query).get('year', [''])[0]
        option_url = create_option_url(url, value, year)
        print(f"    {text}: {value}")
        print(f"    URL: {option_url}")

def save_to_json_file(result, filename):
    with open(filename, 'w') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)

def run_script():
    filtered_links = scrape_links(url)
    grouped_options = scrape_options(filtered_links)
    
    result = {}
    for link_text, options_list in grouped_options.items():
        result[link_text] = []
        for link, (value, text) in zip(filtered_links, options_list):
            year = parse_qs(urlparse(link[0]).query).get('year', [''])[0]
            option_url = create_option_url(url, value, year)
            result[link_text].append({'text': text, 'value': value, 'url': option_url})
    
    return result

if __name__ == '__main__':
    result = run_script()
    save_to_json_file(result, 'output.json')
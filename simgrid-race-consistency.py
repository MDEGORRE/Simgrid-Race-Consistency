from bs4 import BeautifulSoup
from urllib.request import Request,urlopen
from urllib.parse import urlparse, parse_qs
import json

# This script is used to calculate the race consistency of a driver on Simgrid website. It parses the lap times of the tables and creates a Json file with name of the driver and the consistency. 
# Be reminded that laps where driver has crash or a pit stop significantly lowers the race consistency. Lap 1 is also ignored.

# url = "https://www.thesimgrid.com/championships/9918/results?filter_class_id=22705&overall=false&race_id=59881&result_type=laps&session_type=race_1"
url = input('Url of race laps results: ')
req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
page = urlopen(req)
html = page.read().decode("utf-8")
soup = BeautifulSoup(html, "html.parser")

# Get all laps results table
result_lists = soup.find_all('table', class_='table-results')

# Get the drivers name
tbody = result_lists[0].find('tbody')
rows = tbody.find_all('tr', attrs={'data-best': True})

drivers_names = []
for row in rows:
    drivers_names.append(row.select_one(':nth-child(2)').getText().strip())

# Remove the first table result (includes all laps which is not interesting) as we have the drivers name
result_lists.pop(0)

# Store racelaptimes objects into an array data
data = []
for result_list in result_lists:
    cells = result_list.find_all('td', class_='sect_0')
    racelaptimes = {
        'laptimes': [],
        'average_lap': None,
        'delta_from_average_lap': []
    }
    for cell in cells:
        racelaptimes['laptimes'].append(int(cell['data-milliseconds']))
        # Remove the first lap: this lap is usually slower than the average lap time and is not a good representation of driver speed.
    racelaptimes['laptimes'].pop(0)
        # Average lap time in milliseconds
    racelaptimes['average_lap'] = round(sum(racelaptimes['laptimes']) / len(racelaptimes['laptimes']),2)
        # For each lap in the laptimes array, calculate the absolute delta in % from the average lap and store in the delta_from_average_lap array.
    for laptime in racelaptimes['laptimes']:
        racelaptimes['delta_from_average_lap'].append(round(abs(100 - laptime / racelaptimes['average_lap'] * 100), 2))
        racelaptimes.update({'consistency': 100 - round(sum(racelaptimes['delta_from_average_lap']) / len(racelaptimes['delta_from_average_lap']), 2)})
    data.append(racelaptimes)

# Get race-id
parsed_url = urlparse(url)
raceId = parse_qs(parsed_url.query)['race_id'][0]

# Get event title
event = soup.find('h1').get_text().replace(' ', '')

# Combine both arrays to get driver name and his race consistency and create the json file
result = {}
i = 0
while i < len(drivers_names):
    result[i+1] = {'driver': drivers_names[i], 'consistency': data[i]['consistency']}
    i += 1
json_data = json.dumps(result)

with open(event.strip() + '-' + raceId + '-race-consistency.json', "w") as outfile:
    outfile.write(json_data)
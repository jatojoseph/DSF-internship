import csv
from collections import OrderedDict
import argparse


# Helper functions

#changes CSV rows into an array ofdcitionaries for each and every row
def parse_csv(file_path = None, silver_plan =False):
    data = []
    with open(file_path, 'r') as file_obj:
        reader = csv.DictReader(file_obj)

        if silver_plan:
            for row in reader:
                if row['metal_level'] == 'Silver':
                    data.append(row)
        else:
            for row in reader:
                data.append(row)
        next(reader, None)
    return data


def write_csv(file_path=None, data_dict={}):
    with open(file_path, 'w') as f:
        writer = csv.DictWriter(f, ['zipcode', 'rate'], lineterminator='\n')
        writer.writeheader()

        for zipcode, rates in data_dict.items():
            if len(rates) > 1:
                rates.sort()
                writer.writerow({'zipcode': zipcode, 'rate': rates[1]})
            else:
                writer.writerow({'zipcode': zipcode, 'rate': str(rates)})




parser = argparse.ArgumentParser(description='Parser to calculate second lowest cost silver plan (SLCSP)')
parser.add_argument('-s', '--slcsp', help='CSV containing zipcodes of associated silver plans', required=True)
parser.add_argument('-p', '--plans', help='CSV containing all the health plans in the U.S. on the marketplace',
                    required=True)
parser.add_argument('-z', '--zips', help='a mapping of ZIP Code to county/counties & rate area(s)', required=True)

args = vars(parser.parse_args())

# Turn csv's into lists of dictionaries to maintain order
slcsp = parse_csv(args['slcsp'], False)
plans = parse_csv(args['plans'], True)
zips = parse_csv(args['zips'], False)

silver_rate_area_state = OrderedDict()
for silver_plans in slcsp:
    silver_zip = silver_plans['zipcode']
    for zip in zips:
        if silver_zip == zip['zipcode']:
            if silver_zip in silver_rate_area_state:
                # Verifies if that zipcode already has a rate_area, if rate_area differs provide blank answer
                if silver_rate_area_state[silver_zip]['rate_area'] != zip['rate_area']:
                    silver_rate_area_state[silver_zip] = None
                break
            else:
                silver_rate_area_state[silver_zip] = {'rate_area': zip['rate_area'], 'state': zip['state']}

silver_plans = []
answers = OrderedDict()
for zipcode, rate_area_state in silver_rate_area_state.items():
    if not silver_rate_area_state[zipcode]:  # if this valuates to None then set to a blank answer
        answers[zipcode] = ''
    else:
        for plan in plans:
            if rate_area_state['rate_area'] == plan['rate_area'] and rate_area_state['state'] == plan['state']:
                if zipcode in answers:
                    answers[zipcode].append(plan['rate'])
                else:
                    answers[zipcode] = [plan['rate']]

    if zipcode not in answers:
        # Zipcode doesn't have a rate_area/state in plans.csv
        answers[zipcode] = ''

# Write each dictionary of second lowest silver plans to slcsp.csv
write_csv(args['slcsp'], answers)
    
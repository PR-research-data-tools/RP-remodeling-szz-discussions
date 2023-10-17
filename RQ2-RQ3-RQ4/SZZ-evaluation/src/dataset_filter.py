import json
import os
from os import path
import csv
import sys
import random

import logging
from tqdm import tqdm


LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
csv.field_size_limit(sys.maxsize)

def main():
    relevant_ids = list()
    relevant_sample_ids = list()

    relevant_sample_size = 620
    population_size = 8919

    gt_path = path.join('full_data.csv')
    ds_path = path.join('Datasets', 'with_empties')
    filtered_ds_path = path.join('Datasets', 'Filtered')

    with open(gt_path, 'r') as f:
        reader = csv.reader(f)
        next(reader)
        logging.info('Gathering ids of bugs with references...')
        for row in tqdm(reader):
            if row[3] == '[]' or row[9] == '[]':
                continue
            relevant_ids.append(row[1])

    for i in range(relevant_sample_size):
        relevant_sample_ids.append(relevant_ids.pop(random.randrange(len(relevant_ids))))

    assert (len(relevant_ids) + len(relevant_sample_ids)) == population_size

    logging.info(f'{len(relevant_ids)} bug ids gathered.')
    logging.info('Filtering existing datasets...')
    for file in os.listdir(ds_path):
        ds_file_path = os.path.join(ds_path, file)
        filtered_ds = list()
        filtered_sample = list()
        logging.info(f'Filtering {ds_file_path}...')
        with open(ds_file_path, 'r') as ds_file:
            ds = json.load(ds_file)
            for el in tqdm(ds):
                if str(el["id"]) in relevant_sample_ids:
                    filtered_sample.append(el)

                elif str(el["id"]) in relevant_ids:
                    filtered_ds.append(el)

        ds_file.close()
        assert (len(filtered_sample) + len(filtered_ds)) == population_size

        logging.info('Filtering complete. Saving filtered dataset...')
        filtered_out_path = path.join(filtered_ds_path, f'filtered_{file}')
        with open(filtered_out_path, 'w+') as filtered_out_file:
            json.dump(filtered_ds, filtered_out_file, indent=4)
        filtered_out_file.close()
        logging.info(f'{filtered_out_path} saved.')

        filtered_sample_path = path.join(filtered_ds_path, 'RelevantSample', f'sample_filtered_{file}')
        with open(filtered_sample_path, 'w+') as filtered_out_file:
            json.dump(filtered_sample, filtered_out_file, indent=4)
        filtered_out_file.close()
        logging.info(f'{filtered_sample_path} saved.')

    return


if __name__ == '__main__':
    main()

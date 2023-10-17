import os
from os import path, walk
import logging
from tqdm import tqdm
from pydriller import RepositoryMining
import json

LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def file_walker(root):
    #logging.info(f'Traversing `{root}` ...')
    for (dirpath, dirnames, filenames) in tqdm(walk(root)):
        for filename in filenames:
            file_path = path.join(dirpath, filename)
            #logging.info(f'Adding {file_path}')
            yield file_path


def file_list(root):
    logging.info(f'Retriving files in `{root}` ...')
    all_files = list()
    for file_path in file_walker(root):
        all_files.append(file_path)

    return list(set(all_files))


def file_dict(root):
    filenames_dict = dict()
    for file in file_walker(root):
        filename = str(file).split(os.sep)[-1]
        filenames_dict.setdefault(filename, list()).append(file.replace(os.sep, "/"))

    return filenames_dict


def historical_file_dict(root):
    filenames_dict = dict()
    for commit in RepositoryMining(root).traverse_commits():
        for modification in commit.modifications:
            old_path = modification.old_path
            if old_path:
                old_filename = old_path.split("/")[-1]
                filenames_dict.setdefault(old_filename, list())
                if old_path not in filenames_dict[old_filename]:
                    filenames_dict[old_filename].append(old_path)

            new_path = modification.new_path
            if new_path and new_path != old_path:
                new_filename = new_path.split("/")[-1]
                filenames_dict.setdefault(new_filename, list())
                if new_path not in filenames_dict[new_filename]:
                    filenames_dict[new_filename].append(new_path)

    return filenames_dict


def main():
    file_count = 0
    #filenames_dict = file_dict('mozilla-unified')
    filenames_dict = historical_file_dict('mozilla-unified')

    print(len(filenames_dict))
    print(filenames_dict)
    min_size = -1
    max_size = -1
    count = 0
    for value in tqdm(filenames_dict.values()):
        size = len(value)
        if min_size < 0:
            min_size = size
            max_size = size

        else:
            if size < min_size:
                min_size = size
            if size > max_size:
                max_size = size

        count += size

    avg_size = count/len(filenames_dict)

    print(f'min = {min_size}')
    print(f'max = {max_size}')
    print(f'avg = {avg_size}')
    print(f'keys = {len(filenames_dict)}')
    print(f'files = {file_count}')
    logging.info('Saving filenames dictionary')

    with open('filenames_history.json', 'w+') as json_file:
        json.dump(filenames_dict, json_file, indent=4)

    json_file.close()


if __name__ == '__main__':
    main()

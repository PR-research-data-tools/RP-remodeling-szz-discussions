from os import path
import json
from pydriller import RepositoryMining, Commit

from bugbug import repository
from libmozdata import vcs_map

import logging
from tqdm import tqdm


LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def main():

    merc_commit_file_mapping = dict()
    commit_file_mapping = dict()
    mercurials = list()

    for commit in tqdm(repository.get_commits()):
        merc_commit_file_mapping.setdefault(commit['node'], list()).extend(commit['files'])
        mercurials.append(commit['node'])

    git_commits = [commit for commit in vcs_map.mercurial_to_git(repo_dir='mozilla-unified',
                                                                 mercurial_hashes=mercurials)]
    for i in range(len(git_commits)):
        commit_file_mapping.setdefault(git_commits[i], list()).extend(merc_commit_file_mapping[mercurials[i]])

    logging.info('Starting Reading Files')
    for dataname in ['detangled_parsed', 'detangled_relaxed', 'detangled_strict',
                     'extrinsic_strict', 'extrinsic_relaxed', 'parsed_relaxed',
                     'parsed_strict', 'strict_strict', 'strict_relaxed',
                     'relaxed_relaxed', 'relaxed_strict', 'normal']:

        logging.info(f'Reading {dataname} dataset...')
        ''''
        with open(path.join('Datasets', 'no_empty_fix', f'{dataname}_dataset.json'), 'r') as dataset:
            my_data = json.load(dataset)
        dataset.close()
        '''
        with open(path.join('Datasets',
                            'Filtered',
                            'RelevantSample',
                            f'sample_filtered_{dataname}_dataset.json'), 'r') as dataset:
            my_data = json.load(dataset)
        dataset.close()
        id_map = dict()
        counter = 0
        logging.info(f'Composing new dataset for {dataname} data...')
        dataset_list = list()
        for el in tqdm(my_data):
            curr_id = ''
            file_list = el['files']
            fix_list = el['fix_commit_hash']
            issue_date = el['earliest_issue_date']
            bug_hashes = el['bug_commit_hash']
            all_modified_files = set()

            # for dataset starting with detangled: keep commit with shared files, discard commit with no file shared
            # for dataset starting with extrinsic: keep regular files plus files that do not appear in any commit
            # for normal dataset: keep regular files with regular commits
            # for the rest:
            #   1. See which files are not share by any commit (extr) and which appears (detang)
            #   2. Add extr files to each entry
            #   2. For each entry put files from the list of detangling, if any
            # if the resulting file list is empty, discard the entry

            for commit_hash in fix_list:
                new_file_list = list()
                modified_files = commit_file_mapping[commit_hash]
                if dataname == 'normal':
                    new_file_list = modified_files

                elif dataname.startswith('detangled'):
                    for filename in modified_files:
                        if filename in file_list:
                            new_file_list.append(filename)

                elif dataname.startswith('extrinsic'):
                    new_file_list.extend(modified_files)
                    if el['id'] != curr_id:
                        curr_id = el['id']
                        for commit_fix in fix_list:
                            all_modified_files.add(el for el in commit_file_mapping[commit_fix])

                    extrinsic_files = [el for el in file_list if el not in all_modified_files]
                    new_file_list.extend(extrinsic_files)

                else:
                    if el['id'] != curr_id:
                        curr_id = el['id']
                        for commit_fix in fix_list:
                            all_modified_files.add(el for el in commit_file_mapping[commit_fix])

                    extrinsic_files = [el for el in file_list if el not in all_modified_files]
                    detangling_files = [el for el in file_list if el not in extrinsic_files]
                    for filename in modified_files:
                        if filename in detangling_files:
                            new_file_list.append((filename))

                    new_file_list.extend(extrinsic_files)

                new_file_list = list(set(new_file_list))

                if new_file_list:
                    new_item = {
                            "id": counter,
                            "repo_name": "mozilla-unified",
                            "fix_commit_hash": commit_hash,
                            "files": new_file_list,
                            "bug_commit_hash": bug_hashes,
                            "earliest_issue_date": issue_date
                        }
                    dataset_list.append(new_item)
                    counter += 1

        ''''
        with open(path.join('Datasets', 'Extended', f'extended_{dataname}_dataset.json'), 'w+') as new_file:
            json.dump(dataset_list, new_file, indent=4)
        new_file.close()
        '''

        with open(path.join('Datasets',
                            'Extended',
                            'FilteredSample',
                            f'extended_filtered_sample_{dataname}_dataset.json'), 'w+') as new_file:
            json.dump(dataset_list, new_file, indent=4)
        new_file.close()

    return


if __name__ == '__main__':
    main()

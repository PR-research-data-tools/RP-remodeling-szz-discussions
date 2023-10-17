import json, csv
from os import path
from bugbug import repository, bugzilla, db
import pandas as pd

from libmozdata import vcs_map
import logging
from tqdm import tqdm


LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

#assert db.download(bugzilla.BUGS_DB)
#assert db.download(repository.COMMITS_DB)

'''
Entry Format:

[
    {   id: INTEGER,
        repo_name: STRING local path,
        fix_commit_hash: STRING commit hash,
        files = [STRING filepath]
        bug_commit_hash: [STRING commit hashes],
        earliest_issue_date: DATE yyyy-mm-ddThh:mm:ss','
            },
    ...
]

'''


def parse_string_list(string_list: str):
    out = string_list.replace('\'', '').replace('"', '').replace('[', '').replace(']', '').replace(' ', '').split(',')
    if len(out) == 1 and out[0] == '':
        out = list()

    return out

def main():
    strict_list = list()
    relaxed_list = list()
    repo_name = 'mozilla-unified'

    pr_mercurial_map = dict()
    mercurial_git = dict()
    mercurial_list = list()

    for mercurial_commit in tqdm(repository.get_commits()):
        if mercurial_commit['bug_id']:
            mercurial_hash = mercurial_commit['node']
            bug_id = mercurial_commit['bug_id']
            pr_mercurial_map.setdefault(bug_id, list()).append(mercurial_hash)
            mercurial_list.append(mercurial_hash)
        else:
            print(f"No bug id for {mercurial_commit['node']}")

    git_list = [git_hash for git_hash in vcs_map.mercurial_to_git(repo_name, mercurial_list)]
    assert len(git_list) == len(mercurial_list)
    print('asserted')
    for i in range(len(git_list)):
        mercurial_git[mercurial_list[i]] = git_list[i]

    with open(path.join('full_data.csv'), 'r', encoding="utf8") as csv_file:
        data_df = pd.read_csv(csv_file)
        data_df.set_index('fix_id')
        counter = 0

        # Normal Version
        normal_list = list()

        # Anti-Tangled Versions
        detangled_parsed_list = list()  # file in common between fix and references
        detangled_strict_list = list()  # same as before but the file has a unique match in the repo
        detangled_relaxed_list = list()  # same as before but the file is the most similar one into the repo

        # Anti-Extrinsic Versions
        extrinsic_strict_list = list()  # the file is not present in the fix but has a match in the repo
        extrinsic_relaxed_list = list()  # as before but the match is partial

        # Combined versions: {tangled}_{extrinsic}_list
        parsed_strict_list = list()
        parsed_relaxed_list = list()
        strict_strict_list = list()
        strict_relaxed_list = list()
        relaxed_strict_list = list()
        relaxed_relaxed_list = list()

        for bug in tqdm(bugzilla.get_bugs()):
            if data_df['fix_id'].eq(bug['id']).any():
                files = list()
                fix_id = bug['id']
                fix_hashes = list()
                if fix_id in pr_mercurial_map:
                    fix_hashes.extend([mercurial_git[mercurial_hash] for mercurial_hash in pr_mercurial_map[fix_id]])

                # Check if the record has the same fix_id of the bug_ticket
                record = data_df.iloc[counter]
                record2 = data_df.loc[data_df['fix_id'] == bug['id']]
                fix1 = int(record['fix_id'])
                fix2 = int(record2['fix_id'].values[0])

                assert fix1 == fix2
                counter += 1

                # Still using iloc otherwise I cannot use column name to extract values. Otherwise, I should map fixes
                bug_ids = record['bug_ids'][1:-1].replace(' ', '').split(',')
                bug_hashes = list()
                #bug_hashes = [mercurial_git[mercurial_hash]
                #              for mercurial_hash in pr_mercurial_map[bug_id]
                #              for bug_id in bug_ids]
                for bug_id in bug_ids:
                    if int(bug_id) in pr_mercurial_map:
                        for mercurial_hash in pr_mercurial_map[int(bug_id)]:
                            bug_hashes.append(mercurial_git[mercurial_hash])

                bug_hashes = list(set(bug_hashes))

                if not bug_hashes or not fix_hashes:
                    continue

                modified = parse_string_list(record['modified_files'])
                parsed_references = parse_string_list(record['parsed_references'])
                strict_repo_references = parse_string_list(record['strict_repo_references'])
                relaxed_repo_references = parse_string_list(record['relaxed_repo_references'])

                bug_files = record['bug_files']
                earliest_issue_date = bug['creation_time']

                if earliest_issue_date[-1] == 'Z':
                    earliest_issue_date = earliest_issue_date[:-1]

                # Anti-Tangled Versions

                detangled_parsed_file_list = list()   # file in common between fix and references
                detangled_strict_file_list = list()   # same as before but the file has a unique match in the repo
                detangled_relaxed_file_list = list()  # same as before but the file is the most similar one into the repo

                # Anti-Extrinsic Versions

                extrinsic_strict_file_list = list()   # the file is not present in the fix but has a match in the repo
                extrinsic_relaxed_file_list = list()  # as before but the match is partial

                # Combined Versions
                parsed_strict_file_list = list()
                parsed_relaxed_file_list = list()
                strict_strict_file_list = list()
                strict_relaxed_file_list = list()
                relaxed_strict_file_list = list()
                relaxed_relaxed_file_list = list()

                # Creating File Lists

                # Detangled versions
                # Detangled Parsed
                if set(modified).intersection(set(parsed_references)):
                    detangled_parsed_file_list = list(set(modified).intersection(set(parsed_references)))
                else:
                    detangled_parsed_file_list = modified

                # Detangled Strict
                if set(modified).intersection(set(strict_repo_references)):
                    detangled_strict_file_list = list(set(modified).intersection(set(strict_repo_references)))
                else:
                    detangled_strict_file_list = modified

                # Detangled Relaxed
                if set(modified).intersection(set(relaxed_repo_references)):
                    detangled_relaxed_file_list = list(set(modified).intersection(set(relaxed_repo_references)))
                else:
                    detangled_relaxed_file_list = modified

                # Extrinsic Versions
                # Extrinsic Strict
                extrinsic_strict_file_list = list(set(strict_repo_references).union(set(modified)))

                # Extrinsic Relaxed
                extrinsic_relaxed_file_list = list(set(relaxed_repo_references).union(set(modified)))


                # Combined Versions
                # Extrinsic Strict Versions
                if set(extrinsic_strict_file_list).issubset(set(modified)):
                    parsed_strict_file_list = detangled_parsed_file_list
                    strict_strict_file_list = detangled_strict_file_list
                    relaxed_strict_file_list = detangled_relaxed_file_list
                else:
                    parsed_strict_file_list = list(
                        (set(extrinsic_strict_file_list)-set(modified)).union(detangled_parsed_file_list))
                    strict_strict_file_list = list(
                        (set(extrinsic_strict_file_list) - set(modified)).union(detangled_strict_file_list))
                    relaxed_strict_file_list = list(
                        (set(extrinsic_strict_file_list) - set(modified)).union(detangled_relaxed_file_list))

                # Extrinsic Relaxed Versions
                if set(extrinsic_relaxed_file_list).issubset(set(modified)):
                    parsed_relaxed_file_list = detangled_parsed_file_list
                    strict_relaxed_file_list = detangled_strict_file_list
                    relaxed_relaxed_file_list = detangled_relaxed_file_list
                else:
                    parsed_relaxed_file_list = list(
                        (set(extrinsic_relaxed_file_list)-set(modified)).union(detangled_parsed_file_list))
                    strict_relaxed_file_list = list(
                        (set(extrinsic_relaxed_file_list)-set(modified)).union(detangled_strict_file_list))
                    relaxed_relaxed_file_list = list(
                        (set(extrinsic_relaxed_file_list)-set(modified)).union(detangled_relaxed_file_list))

                # Normal Item
                normal_item = {
                    'id': fix_id,
                    'repo_name': repo_name,
                    'fix_commit_hash': fix_hashes,
                    'files': modified,
                    'bug_commit_hash': bug_hashes,
                    'earliest_issue_date': earliest_issue_date,
                }

                normal_list.append(normal_item)

                # Detangled Parsed Item
                detangled_parsed_item = {
                    'id': fix_id,
                    'repo_name': repo_name,
                    'fix_commit_hash': fix_hashes,
                    'files': detangled_parsed_file_list,
                    'bug_commit_hash': bug_hashes,
                    'earliest_issue_date': earliest_issue_date,
                }
                detangled_parsed_list.append(detangled_parsed_item)

                # Detangled Strict Item
                detangled_strict_item = {
                    'id': fix_id,
                    'repo_name': repo_name,
                    'fix_commit_hash': fix_hashes,
                    'files': detangled_strict_file_list,
                    'bug_commit_hash': bug_hashes,
                    'earliest_issue_date': earliest_issue_date,
                }
                detangled_strict_list.append(detangled_strict_item)

                # Detangled Relaxed Item
                detangled_relaxed_item = {
                    'id': fix_id,
                    'repo_name': repo_name,
                    'fix_commit_hash': fix_hashes,
                    'files': detangled_relaxed_file_list,
                    'bug_commit_hash': bug_hashes,
                    'earliest_issue_date': earliest_issue_date,
                }
                detangled_relaxed_list.append(detangled_relaxed_item)

                # Extrinsic Strict Item
                extrinsic_strict_item = {
                    'id': fix_id,
                    'repo_name': repo_name,
                    'fix_commit_hash': fix_hashes,
                    'files': extrinsic_strict_file_list,
                    'bug_commit_hash': bug_hashes,
                    'earliest_issue_date': earliest_issue_date,
                }
                extrinsic_strict_list.append(extrinsic_strict_item)

                # Extrinsic Relaxed Item
                extrinsic_relaxed_item = {
                    'id': fix_id,
                    'repo_name': repo_name,
                    'fix_commit_hash': fix_hashes,
                    'files': extrinsic_relaxed_file_list,
                    'bug_commit_hash': bug_hashes,
                    'earliest_issue_date': earliest_issue_date,
                }
                extrinsic_relaxed_list.append(extrinsic_relaxed_item)

                # Parsed Strict Item
                parsed_strict_item = {
                    'id': fix_id,
                    'repo_name': repo_name,
                    'fix_commit_hash': fix_hashes,
                    'files': parsed_strict_file_list,
                    'bug_commit_hash': bug_hashes,
                    'earliest_issue_date': earliest_issue_date,
                }
                parsed_strict_list.append(parsed_strict_item)

                # Parsed Relaxed Item
                parsed_relaxed_item = {
                    'id': fix_id,
                    'repo_name': repo_name,
                    'fix_commit_hash': fix_hashes,
                    'files': parsed_relaxed_file_list,
                    'bug_commit_hash': bug_hashes,
                    'earliest_issue_date': earliest_issue_date,
                }
                parsed_relaxed_list.append(parsed_relaxed_item)

                # Strict Strict Item
                strict_strict_item = {
                    'id': fix_id,
                    'repo_name': repo_name,
                    'fix_commit_hash': fix_hashes,
                    'files': strict_strict_file_list,
                    'bug_commit_hash': bug_hashes,
                    'earliest_issue_date': earliest_issue_date,
                }
                strict_strict_list.append(strict_strict_item)

                # Strict Relaxed Item
                strict_relaxed_item = {
                    'id': fix_id,
                    'repo_name': repo_name,
                    'fix_commit_hash': fix_hashes,
                    'files': strict_relaxed_file_list,
                    'bug_commit_hash': bug_hashes,
                    'earliest_issue_date': earliest_issue_date,
                }
                strict_relaxed_list.append(strict_relaxed_item)

                # Relaxed Strict Item
                relaxed_strict_item = {
                    'id': fix_id,
                    'repo_name': repo_name,
                    'fix_commit_hash': fix_hashes,
                    'files': relaxed_strict_file_list,
                    'bug_commit_hash': bug_hashes,
                    'earliest_issue_date': earliest_issue_date,
                }
                relaxed_strict_list.append(relaxed_strict_item)

                # Relaxed Relaxed Item
                relaxed_relaxed_item = {
                    'id': fix_id,
                    'repo_name': repo_name,
                    'fix_commit_hash': fix_hashes,
                    'files': relaxed_relaxed_file_list,
                    'bug_commit_hash': bug_hashes,
                    'earliest_issue_date': earliest_issue_date,
                }
                relaxed_relaxed_list.append(relaxed_relaxed_item)

    csv_file.close()

    # Saving Datasets
    # Normal Version
    with open(path.join('Datasets', 'no_empty_fix', 'normal_dataset.json'), 'w+') as file:
        json.dump(normal_list, file, indent=4)
    file.close()

    # Anti-Tangled Versions
    with open(path.join('Datasets', 'no_empty_fix', 'detangled_parsed_dataset.json'), 'w+') as file:
        json.dump(detangled_parsed_list, file, indent=4)
    file.close()
    with open(path.join('Datasets', 'no_empty_fix', 'detangled_strict_dataset.json'), 'w+') as file:
        json.dump(detangled_strict_list, file, indent=4)
    file.close()
    with open(path.join('Datasets', 'no_empty_fix', 'detangled_relaxed_dataset.json'), 'w+') as file:
        json.dump(detangled_relaxed_list, file, indent=4)
    file.close()

    # Anti-Extrinsic Versions
    with open(path.join('Datasets', 'no_empty_fix', 'extrinsic_strict_dataset.json'), 'w+') as file:
        json.dump(extrinsic_strict_list, file, indent=4)
    file.close()
    with open(path.join('Datasets', 'no_empty_fix', 'extrinsic_relaxed_dataset.json'), 'w+') as file:
        json.dump(extrinsic_relaxed_list, file, indent=4)
    file.close()

    # Combined versions: {tangled}_{extrinsic}_list
    with open(path.join('Datasets', 'no_empty_fix', 'parsed_strict_dataset.json'), 'w+') as file:
        json.dump(parsed_strict_list, file, indent=4)
    file.close()
    with open(path.join('Datasets', 'no_empty_fix', 'parsed_relaxed_dataset.json'), 'w+') as file:
        json.dump(parsed_relaxed_list, file, indent=4)
    file.close()
    with open(path.join('Datasets', 'no_empty_fix', 'strict_strict_dataset.json'), 'w+') as file:
        json.dump(strict_strict_list, file, indent=4)
    file.close()
    with open(path.join('Datasets', 'no_empty_fix', 'strict_relaxed_dataset.json'), 'w+') as file:
        json.dump(strict_relaxed_list, file, indent=4)
    file.close()
    with open(path.join('Datasets', 'no_empty_fix', 'relaxed_strict_dataset.json'), 'w+') as file:
        json.dump(relaxed_strict_list, file, indent=4)
    file.close()
    with open(path.join('Datasets', 'no_empty_fix', 'relaxed_relaxed_dataset.json'), 'w+') as file:
        json.dump(relaxed_relaxed_list, file, indent=4)
    file.close()

    return


if __name__ == '__main__':
    main()

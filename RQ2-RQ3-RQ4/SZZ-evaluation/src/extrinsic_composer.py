import csv
import json
from os import path, listdir, curdir
import sys

import logging

import bugbug
from tqdm import tqdm
from bugbug import bugzilla, repository
from libmozdata import vcs_map

csv.field_size_limit(sys.maxsize)
LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def main(empty_fix: bool = True, empty_bug: bool = True, pr_level: bool = False, sample_set: bool = True):
    logging.info('')
    szz_versions = ['ag', 'b', 'ma', 'l', 'r']
    dataset_versions = ['e_r', 'e_s']
    #dataset_versions = ['d_p', 'd_r', 'e_r', 'e_s', 'p_r', 'p_s', 'r_r', 'r_s', 's_r', 's_s', 'n']

    #dataset_versions = ['n']

    version_mapping = {
        'd_p': "detangled_parsed",
        'd_r': "detangled_relaxed",
        'd_s': "detangled_strict",
        'e_r': "extrinsic_relaxed",
        'e_s': "extrinsic_strict",
        'p_r': "parsed_relaxed",
        'p_s': "parsed_strict",
        'r_r': "relaxed_relaxed",
        'r_s': "relaxed_strict",
        's_r': "strict_relaxed",
        's_s': "strict_strict",
        'n': "normal",

    }

    commit_mapping = dict()     # Git commit -> Mercurial Commit
    pr_mapping = dict()         # mercurial commits -> PR

    if pr_level:
        mercurial_commits = list()
        for commit in tqdm(repository.get_commits()):
            mercurial_commits.append(commit['node'])
            pr_mapping.setdefault(commit['node'], []).append(commit['bug_id'])

        git_commits = [git_hash for git_hash in vcs_map.mercurial_to_git(repo_dir='mozilla-unified',
                                                                         mercurial_hashes=mercurial_commits)]
        assert len(git_commits) == len(mercurial_commits)
        for i in range(len(mercurial_commits)):
            commit_mapping[git_commits[i]] = mercurial_commits[i]


    for ds in dataset_versions:
        for szz in tqdm(szz_versions):
            logging.info(f'Scanning results for {szz} in {ds} dataset...')
            if dataset_versions == 'e_s':
                paths = [path.join('out', f'{szz}', f'n'), path.join('out', f'{szz}', 'p_s')]
            else:
                paths = [path.join('out', f'{szz}', f'n'), path.join('out', f'{szz}', 'p_r')]

            if sample_set:
                merged_path = path.join('Datasets',
                                        'Filtered',
                                        'RelevantSample',
                                        f'sample_filtered_{version_mapping[ds]}_dataset.json')
            elif empty_fix and empty_bug:
                merged_path = path.join('Datasets',
                                        'with_empties',
                                        f'{version_mapping[ds]}_dataset.json')
            elif empty_fix and not empty_bug:
                merged_path = path.join('Datasets',
                                        'no_empty_bug',
                                        f'{version_mapping[ds]}_dataset.json')
            else:
                merged_path = path.join('Datasets',
                                        'no_empty_fix',
                                        f'{version_mapping[ds]}_dataset.json')

            with open(merged_path, 'r') as merged_file:
                merged_dataset = json.load(merged_file)
            merged_file.close()

            results = dict()

            for file_path in paths:
                file_list = listdir(file_path)
                for filename in file_list:
                    if filename.startswith('pr') or filename.startswith('sample'):
                        continue
                    json_path = path.join(file_path, filename)
                    # print(json_path)
                    with open(json_path, 'r') as json_file:
                        batch_res = json.load(json_file)
                    json_file.close()
                    for el in batch_res:
                        if el['fix_commit_hash'] not in results:
                            results[el['fix_commit_hash']] = el['inducing_commit_hash']
                        else:
                            res = results[el['fix_commit_hash']]
                            res.extend(el['inducing_commit_hash'])
                            results[el['fix_commit_hash']] = res

            composed_results = list()
            for bug in merged_dataset:
                if not empty_fix and not bug['fix_commit_hash']:
                    continue

                if not empty_bug and not bug['bug_commit_hash']:
                    continue

                inducing_commit_hash = list()
                for commit in bug['fix_commit_hash']:
                    if commit in results:
                        inducing_commit_hash.extend(results[commit])
                bug['inducing_commit_hash'] = list(set(inducing_commit_hash))

                if pr_level:
                    fix_pr = list()
                    bug_pr = list()
                    inducing_pr = list()

                    for fix_commit in bug['fix_commit_hash']:
                        fix_pr.extend(pr_mapping[commit_mapping[fix_commit]])

                    for bug_commit in bug['bug_commit_hash']:
                        bug_pr.extend(pr_mapping[commit_mapping[bug_commit]])

                    for inducing_commit in bug['inducing_commit_hash']:
                        if inducing_commit in commit_mapping:
                            mercurial_commit = commit_mapping[inducing_commit]
                            if mercurial_commit in pr_mapping:
                                inducing_pr.extend(pr_mapping[mercurial_commit])
                            else:
                                logging.info(f'Missing PR for {mercurial_commit}')
                                inducing_pr.append(mercurial_commit)
                        else:
                            logging.info(f'Missing mapping for {inducing_commit}')
                            inducing_pr.append(mercurial_commit)

                    fix_pr = [str(el) for el in set(fix_pr)]
                    bug_pr = [str(el) for el in set(bug_pr)]
                    inducing_pr = [str(el) for el in set(inducing_pr)]

                    bug['fix_commit_hash'] = fix_pr
                    bug['bug_commit_hash'] = bug_pr
                    bug['inducing_commit_hash'] = inducing_pr

                composed_results.append(bug)

            filename = f'{szz}_{ds}'
            if pr_level:
                filename = f'pr_{filename}'

            if sample_set:
                composed_out_path = path.join('out',
                                              f'{szz}',
                                              f'{ds}',
                                              f'sample_{filename}.json')

            elif empty_fix and empty_bug:
                composed_out_path = path.join('out',
                                              'out',
                                              f'{szz}',
                                              f'{ds}',
                                              f'{filename}_composed.json')
            elif empty_fix and not empty_bug:
                composed_out_path = path.join('out',
                                              'out',
                                              f'{szz}',
                                              f'{ds}',
                                              f'{filename}_no_empty_bug_composed.json')

            else:
                composed_out_path = path.join('out',
                                              'out',
                                              f'{szz}',
                                              f'{ds}',
                                              f'{filename}_no_empty_fix_composed.json')

            with open(composed_out_path, 'w+') as composed_out_file:
                json.dump(composed_results, composed_out_file, indent=4)
            composed_out_file.close()


if __name__ == "__main__":
    main(empty_bug=False, empty_fix=False, pr_level=True, sample_set=True)       # Change the setup here

# NLP-PySZZ
This is a branch of PySZZ, an open-source implementation of several versions of the SZZ algorithm for detecting bug-inducing commits. The project performs analysis on Mozilla BugZilla reports and experiments with different SZZ versions and datasets.

## Setup 
```
git clone https://github.com/fpetrulio/nlp_pyszz.git
```
Further details of the repository can be found in its README file. 

## Requirements
To run PySZZ you need:

- Python 3
- Git Cinnabar (https://github.com/glandium/git-cinnabar)
- srcML (https://www.srcml.org/) (i.e., the `srcml` command should be in the system path)
- git >= 2.23

## Setup
1. Clone this repository.
2. Run the following command to install the required python dependencies:
```bash
pip3 install --no-cache-dir -r requirements.txt
pip uninstall regex -y
pip install regex==2022.3.2
```

## Dataset
Run the following command to download `mozilla-unified` project by `git-cinnabar`
```
git clone hg::https://hg.mozilla.org/mozilla-unified
git config fetch.prune true
```
## Running an SZZ Version

To run a specific version of the SZZ algorithm, you can use the `main.py` script. Below is an example of how you might run the MA-SZZ version:

```bash
python3 main.py --version=MA_SZZ --other-options
```

## Run the tool
To run the tool, simply execute the following command where `../repositories/` points to the parent directory of Mozilla unified:
```
 python3 main.py /Datasets/Extended/extended_detangled_relaxed_dataset.json conf/rszz.yml ../repositories/
```
The command is detailed below:
```
python3 main.py /path/to/bug-fixes.json /path/to/configuration-file.yml /path/to/repo-directory
```
- `bug-fixes.json` contains a list of information about bug-fixing commits and (optionally) issues <sup>[1](#myfootnote1)</sup>. 
This is an example json that can be used with pyszz:
```
[
  {
    "repo_name": "amirmikhak/3D-GIF",
    "fix_commit_hash": "645496dd3c5c89faee9dab9f44eb2dab1dffa3b9"
    "best_scenario_issue_date": "2015-04-23T07:41:52"
  },
  ...
]
```

alternatively:

```
[
  {
    "repo_name": "amirmikhak/3D-GIF",
    "fix_commit_hash":   "645496dd3c5c89faee9dab9f44eb2dab1dffa3b9",
    "earliest_issue_date": "2015-04-23T07:41:52"
  },
  ...
]
```

without issue date <sup>[1](#myfootnote1)</sup>:

```
[
  {
    "fix_commit_hash": "30ae3f5421bcda1bc4ef2f1b18db6a131dcbbfd3",
    "repo_name": "grosa1/szztest_mod_change"
  },
  ...
]
```

- `configuration-file.yml` is one of the following, depending on the SZZ variant you want to run:
    - `conf/agszz.yaml`: runs AG-ZZ
    - `conf/lszz.yaml`: runs L-ZZ
    - `conf/rszz.yaml`: runs R-ZZ
    - `conf/maszz.yaml`: runs MA-ZZ
    - `conf/raszz.yaml`: runs RA-ZZ

- `repo-directory` is a folder which contains all the repositories that are required by `bug-fixes.json`, e.g. Mozilla-unified. This parameter is not mandatory. In the case of the `repo-directory` is not specified, pyszz will download each repo required by each bug-fix commit in a temporary folder. In the other case, pyszz searches for each required repository in the `repo-directory` folder. In our case, give path to Mozilla-unified. 
The directory structure must be the following:

``` bash
    .
    |-- repo-directory
    |   |-- repouser
    |       |-- reponame 
    .
```

To have different run configurations of SZZ variations, just create or edit the configuration files. The available parameters are described in each yml file. In order to use the issue date filter, you have to enable the parameter provided in each configuration file.

**N.B.** _the difference between `best_scenario_issue_date` and `earliest_issue_date` is described in our [paper](https://arxiv.org/abs/2102.03300). Simply, you can use `earliest_issue_date` if you have the date of the issue linked to the bug-fix commit._

**<a name="myfootnote1"><sup>1</sup></a>** You need to edit the flag `issue_date_filter` provided in the configuration files at `conf/` in order to enable/disable the issue date filter for SZZ.

## Testing
The `test` directory contains some usage examples of pyszz and test cases.
- `start_example1.sh`, `start_example2.sh` and `start_example3.sh` are example usages of pyszz;
- `start_test_lszz.sh` and `start_test_rszz.sh` are test cases for L-SZZ and R-SZZ; 
- `repos_test.zip` and `repos_test_with_issues.zip` contain some downloaded repositories to be used with `bugfix_commits_test.json` and `bugfix_commits_with_issues_test.json` , which are two examples of input json containing bug-fixing commits;
- `comment_parser` contains some test cases for the custom comment parser implemented in pyszz.

Run the test script to ensure that the repository is set up correctly:

```bash
python3 test.py
```
## `Tools`: It contains the tool Refactoring miner, required by one of the SZZ versions. 

## `pointer`: It is a checkpoint, it keeps track of the last batch processed by each SZZ variations since SZZ can take time to process the huge dataset. 
The batch needs to set to zero. 

## `szz`: 
  - `core`: APIs of SZZ

## `conf`: the configuration of each SZZ variation. They should be modified very carefully.
These configurations are mainly based on previous work by Rosa et al. We have adopted the new implementation of B-SZZ compared to their work, which is based on the recent work in this direction. 


## Data Extraction Strategies

The repository supports different data extraction strategies, such as 'strict', 'relax', or 'bug fixing commits' for gathering files mentioned in the bug reports.

## Performance Metrics

The performance of the SZZ algorithms is evaluated using Precision, Recall, and F-measure.

## License

This project is licensed under the terms specified in the `LICENSE` file.

## How to cite
```
@inproceedings{rosa2021evaluating,
  title={Evaluating SZZ Implementations Through a Developer-informed Oracle},
  author={Rosa, Giovanni and Pascarella, Luca and Scalabrino, Simone and Tufano, Rosalia and Bavota, Gabriele and Lanza, Michele and Oliveto, Rocco},
  booktitle={2021 IEEE/ACM 43rd International Conference on Software Engineering (ICSE)},
  pages={436--447},
  year={2021},
  organization={IEEE}
}
```

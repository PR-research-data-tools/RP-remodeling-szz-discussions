## Overview

This repository builds upon the NLP-PySZZ project to perform analysis on Mozilla BugZilla reports. It experiments with different SZZ versions and datasets and computes performance metrics such as Precision, Recall, and F-measure.

## Structure
```
    SZZ-evaluation/
        /Datasets/
        /src/
        /test/
        /out/  

     preliminary_analysis.ipynb
     full_data.csv
```
## Contents of the Replication Package
---
#### In `SZZ-evaluation` We proide the setup Guide for Evaluation SZZ performance   
   - `SZZ-evaluation/Datasets/`: Datasets for various file parsing strategies and SZZ variants
   - `SZZ-evaluation/src/`: Source code for evaluation of SZZ performance 
   - `SZZ-evaluation/test/`: Test cases to verify the evaluation setup
   - `SZZ-evaluation/out/`: Results of the evaluation for each version of SZZ. 

### `Datasets`: 
Since the datset from Mozilla is based on Bugs or Pull Requests (PRs) level, it can not be used directly for SZZ. SZZ requires data to be at commit level. 

   - `Datasets/Bug-PR-dataset`: It provides the dataset at the Bug or PR level. It contains the bug id, big fixing or introducing commits, the files mentioned files in bug discussion. Since these mentioned files in bug discussion depends on the parsing strategy (technique used to extract files from the bug discussion, e.g., relax, parsing), we provide various JSON files for various purposes (detangling or extrinsic). We provide a sample record: 
	```
	{
		repo_name: repository name,
		id: PR or Bug id,
		fix_commit_hash: commits involved in bug fix,
		files: the files mentioned in the bug discussion that are changed in a PR (at this level, we do not know the particular commit that fix the bug and modify which file). It is possible that some of these files are not modified in one or other commits in the PR. Therefore, some commits can be discarded for detagling purpose if they do not modify any of these mentioned files, 
		bug_commit_hash: bug-introducing commit,
		earliest_issue_date: date where the PRs is raised or the bug is discovered. 
	}
	```
   - `Datasets/Filtered-Bug-PR-dataset`: Previous work by Rosa et al., only considers the bugs that have at least one fix commit and one bug introducing commit. However, it is possible for a bug in a version control system to have only either of them,  fix commit or bug introducing commit.  To compare to this previous work, we filter the bugs that have both bug introducing and fixing commits.

   - `Datasets/Extended-commit-dataset`: This is just an expanded version of the Bug dataset. Since SZZ requires the data at the commit level, we exapnd each PR based on each commit of `fix_commit_hash`. The commits are only considered for detangled dataset if they have actually modified the mentioned files. In case of extrinsic, the PR level dataset is just expanded for all the commits and no commits are discarded in the process. 

   - `Datasets/Extended-commit-dataset/FilteredRelevantSample`: Due to computational constraints of GIT process, we run SZZ on a sample of dataset. This folder contains the final dataset of sample we used in our study to show various results. 

### Evaluation Setup Guide
### Requirements
- Python 3.9
- Git
- [Poetry](https://python-poetry.org/)
- [Git Cinnabar 0.5](https://github.com/glandium/git-cinnabar)
- To setup Mozilla, have a refer to the git-cinabar [tutorial](https://github.com/glandium/git-cinnabar/wiki/Mozilla:-A-git-workflow-for-Gecko-development) 

### Steps
1. Use poetry to automatically create a virtual environment for the project and install all dependencies by the following
commands in your terminal.
- Install poetry
```bash
pip3 install poetry
```

- Inside the project directory, install dependencies using run:
```bash
poetry install
```
or
```bash
poetry update
```
-- Some packages require Rust and Cargo. You can setup using:
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs/ | sh
```
Note: some users can get a problem with rs-parsepatch package. Try manually building the rs-parsepatch wheel for version 0.4.0
```bash
pip wheel --use-pep517 "rs-parsepatch==0.4.0"
```
-- Try again installing poetry:
```bash
poetry install
```
- Activate the Virtual Environment:
```bash
poetry shell
```

2. Use the [guide](https://github.com/glandium/git-cinnabar/wiki/Mozilla:-A-git-workflow-for-Gecko-development) of git
cinnabar for Mozilla and run the following command:
```bash
git clone hg::https://hg.mozilla.org/mozilla-unified
```
3. In the second cell of the Jupyter Notebook for the [analysis](\preliminary_analysis.ipynb), activate lines 21 and 22

## Key Files
- `/cmd`: run a version of szz on a dataset using the command line.
- `src/filepath_finder.py`: locating the mentioned files from bug disucssions or bug reports. 
	It contains a function filename_finder(text) that identify file paths or filenames within a given text.
- `src/filepath_miner.py`: Extracting file paths from repository (Mozilla in this case) to match them later on with the files mentioned in the bug discussion using the `similarity_checker.py`.
- `similarity_checker.py`: It checks the similarity between the file paths. 
- `filenames_history`: For various files found in the bug disucssion (mentioned files), it find all related files or file paths in the version control history of the repository.
- `/dataset_composer.py`: To create datasets at the commit-set level in the format proposed for [PySZZ](https://github.com/grosa1/pyszz).
- `szz_results_composer.py`: Since the results will be at commit granularity, use this file to bring them back to commit-set or PR granularity.
- `szz_evaluation.py`: Evaluate the results.
- `test/statistical_tests.py`: Contains code for performing statistical tests.
- `full_data.csv`: contains all the bugs in Mozilla which might or might not match our criteria of bugs (closed, and fixed).

## How to use this repository
---
- The first thing to do is to run [preliminary_analysis.ipynb](preliminary_analysis.ipynb). The Notebook will download
automatically updated data from Mozilla systems by the use of the BugBug library. In this way, the script creates the data
folder, containing a snapshot of Mozilla Data. If you want to keep those data and do not update them anymore for
consistency, deactivate rows 21 and 22 from the script:
```python
assert db.download(bugzilla.BUGS_DB)
assert db.download(repository.COMMITS_DB)
```
This will prevent any change to the current data snapshot.

- After the first execution of the Notebook, you can use [dataset_composer.py](dataset_composer.py) to create datasets at
the commit-set (or PR) level in the format proposed for [PySZZ](https://github.com/grosa1/pyszz). To bring them to commit
granularity, just run [dataset_extender.py](dataset_extender.py).
Then you can use NLPySZZ to run SZZ on the created datasets. Since the results will be at commit granularity, use the
[szz_results_composer.py](szz_results_composer.py) to bring them back to commit-set (or PR level) granularity.
In the end, run [szz_evaluation.py](szz_evaluation.py) to evaluate the results.

## License

This project is licensed under the terms specified in the `LICENSE` file.

__IMPORTANT NOTICE: results are organized in the [out](out) folder. Please, check the file paths in the scripts and the
correct file locations of your results before running the scripts__

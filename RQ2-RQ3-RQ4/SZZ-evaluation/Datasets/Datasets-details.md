Previous work by Rosa only considers the bugs that have at least one fix commit and one bug introducing commit. However, it is possible for a bug in a version control system to have only either of them,  fix commit or bug introducing commit. Therefore, we prepared various datasets depending on parsing strategies (extracting files from bug disucssions) and the fields of bug dataset.

- `with_empties`: All the bugs extracted from Mozilla since 2019.
{
'detangled_relaxed_dataset.json': 12472,
'detangled_parsed_dataset.json': 12472,
'normal_dataset.json': 12472,
'relaxed_relaxed_dataset.json': 12472,
'parsed_relaxed_dataset.json': 12472,
'extrinsic_relaxed_dataset.json': 12472,
}

- `no_empty_fix`: there is always a fix introducing commit for each bug. 
{
'detangled_relaxed_dataset.json': 10021,
'detangled_parsed_dataset.json': 10021,
'normal_dataset.json': 10021,
'relaxed_relaxed_dataset.json': 10021,
'parsed_relaxed_dataset.json': 10021,
'extrinsic_relaxed_dataset.json': 10021,
}

- `no_empty_bug`: there is always a bug introducing commit for each bug. 
{
'detangled_relaxed_dataset.json': 11879,
'detangled_parsed_dataset.json': 11879,
'normal_dataset.json': 11879,
'relaxed_relaxed_dataset.json': 11879,
'parsed_relaxed_dataset.json': 11879,
'extrinsic_relaxed_dataset.json': 11879,
}

- `Filtered`: where there are files modified in bug introducing and referenced in bug reports, if there are no files modified in bug introducing commits, such commits can not be traced by SZZ (also requirement of our FI-SZZ).
{'filtered_detangled_parsed_dataset.json': 8299,
'filtered_extrinsic_relaxed_dataset.json': 8299,
'filtered_relaxed_relaxed_dataset.json': 8299,
'filtered_normal_dataset.json': 8299,
'filtered_detangled_relaxed_dataset.json': 8299,
'filtered_parsed_relaxed_dataset.json': 8299,}

- `Filtered/RelevantSample`: these are the bug for our sample.
{
'sample_filtered_extrinsic_relaxed_dataset.json': 620,
'sample_filtered_normal_dataset.json': 620,
'sample_filtered_detangled_relaxed_dataset.json': 620,
'sample_filtered_parsed_relaxed_dataset.json': 620,
'sample_filtered_detangled_parsed_dataset.json': 620,
'sample_filtered_relaxed_relaxed_dataset.json': 620,}

`Extended`: all the bugs with entries on the level of fix introducing commits. This is just an expanded version of the Bug dataset. Since Szz requires the data at the commit level, we exapnd each PR based on each commit of `fix_commit_hash`. The commits are only considered for detangled dataset if they have actually modified the mentioned files. In case of extrinsic, the PR level dataset is just expanded for all the commits and no commits are discarded in the process. 
{'extended_relaxed_relaxed_dataset.json': 14356,
'extended_parsed_relaxed_dataset.json': 14356,
'extended_detangled_parsed_dataset.json': 13325,
'extended_normal_dataset.json': 14356,
'test.json': 1,
'extended_extrinsic_relaxed_dataset.json': 14356,
'extended_detangled_relaxed_dataset.json': 13837,} 

- `Extended/FilteredSample`: Due to computational constraints of GIT process, we run SZZ on a sample of dataset. These are the bug for the sample on the level of bug fixing commits.
{'extended_filtered_sample_detangled_relaxed_dataset.json': 796,
'extended_filtered_sample_parsed_relaxed_dataset.json': 847,
'extended_filtered_sample_relaxed_relaxed_dataset.json': 847,
'extended_filtered_sample_normal_dataset.json': 847,
'extended_filtered_sample_extrinsic_relaxed_dataset.json': 847,
'extended_filtered_sample_detangled_parsed_dataset.json': 777,
}
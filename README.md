## Replication Package for `On Refining the SZZ Algorithm with Bug Discussion Data`
This repository contains the replication package for the study `On Refining the SZZ Algorithm with Bug Discussion Data`.
It proposes a variant of SZZ that builds upon the NLP-PySZZ project to leverage developer discussion from bug reports and identify bug-introducing commits in a version control system. 
It analyzes Mozilla Bugzilla reports, experiments with different SZZ versions and datasets, and computes performance metrics such as Precision, Recall, and F-measure.

## Structure
```
RQ1/
    Manual_Analysis.xlsx

RQ2-RQ3-RQ4/
    SZZ-evaluation/
        /Datasets/
        /src/
        /test/
        /out/
        README.md
        full_data.csv
        preliminary_analysis.ipynb
        Revision-analysis.ipynb
 
    SZZ-new-variant/

```

## Contents of the Replication Package
---
### `RQ1/Manual_Analysis.xlsx`:
It contains the result of a manual analysis of why developers mention files in bug reports.

### `RQ2-RQ3-RQ4/`: 
Supplement material for answering the RQ-RQ4 questions.

#### `SZZ-evaluation`:
We provide the setup Guide for the Evaluation of SZZ performance. Check its README.md under this folder for more details.
   - `SZZ-evaluation/Datasets/`: Datasets for various file parsing strategies and SZZ variants
   - `SZZ-evaluation/src/`: Source code for evaluation of SZZ performance 
   - `SZZ-evaluation/test/`: Test cases to verify the evaluation setup
   - `SZZ-evaluation/out/`: Results of the evaluation for each version of SZZ.
   - `SZZ-evaluation/full_data.csv`: RoTEB Dataset
   - `SZZ-evaluation/preliminary_analysis.ipynb`: Preliminary analysis was done on the RoTEB dataset
   - `SZZ-evaluation/Revision-analysis.ipynb`:  Advanced analysis was done on the RoTEB dataset for the  

#### `SZZ-new-variant`: 
We provide the setup guide for running the new SZZ variant. Check its README.md for more details.

## License

This project is licensed under the terms specified in the `LICENSE` file.



## Replication Package for `On Refining the SZZ Algorithm with Bug Discussion Data`
This repository contains the replication package for the study `On Refining the SZZ Algorithm with Bug Discussion Data`.
It propose a variant of SZZ which builds upon the NLP-PySZZ project to leverage developer discussion from bug reports and identify bug-introducing commits in a version control system. 
It perform analysis on Mozilla BugZilla reports. It experiments with different SZZ versions and datasets and computes performance metrics such as Precision, Recall, and F-measure.

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
 
    SZZ-new-variant/

```

## Contents of the Replication Package
---
### `RQ1/Manual_Analysis.xlsx`:
contains the result of manual analysis on why developer mention files in bug reports?

### `RQ2-RQ3-RQ4/`: 
Supplement material for answering the RQ-RQ4 questions.

#### `SZZ-evaluation`:
We proide the setup Guide for Evaluation SZZ performance. Check its README.md for more details.
   - `SZZ-evaluation/Datasets/`: Datasets for various file parsing strategies and SZZ variants
   - `SZZ-evaluation/src/`: Source code for evaluation of SZZ performance 
   - `SZZ-evaluation/test/`: Test cases to verify the evaluation setup
   - `SZZ-evaluation/out/`: Results of the evaluation for each version of SZZ. 

#### `SZZ-new-variant`: 
We proide the setup Guide to run the new SZZ variant. Check its README.md for more details.

## License

This project is licensed under the terms specified in the `LICENSE` file.



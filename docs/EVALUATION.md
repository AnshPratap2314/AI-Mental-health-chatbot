# MindCare AI --- Evaluation

## 1. Scope

This evaluation measures ML and software behavior on the current
synthetic, non-clinical benchmark.

It does not establish clinical effectiveness, diagnostic accuracy, or
real-world crisis-detection performance.

## 2. Dataset

  Property                             Value
  --------------- --------------------------
  Total samples                        1,200
  Classes                                  6
  Samples/class                          200
  Train                                  840
  Validation                             180
  Test                                   180
  Language mix            English + Hinglish
  Type              Synthetic / non-clinical

Classes:

``` text
crisis
self_harm
negated
contextual
neutral
positive
```

## 3. Data Quality Checks

The evaluation includes:

-   exact duplicate checks
-   train/validation leakage checks
-   train/test leakage checks
-   near-duplicate analysis
-   independent challenge data
-   hard-negative safety cases

Recorded audit:

``` text
Exact duplicates: 0
Train → validation exact leakage: 0
Train → test exact leakage: 0
High-similarity train → validation pairs: 0
High-similarity train → test pairs: 0
```

## 4. Model

``` text
Input
 ↓
TF-IDF
 ↓
Logistic Regression
 ↓
Six-class prediction
```

The classifier uses unigram/bigram features, balanced class weighting
and a fixed random seed for reproducibility.

## 5. Canonical Test Results

  System                           Accuracy   Macro Precision   Macro Recall   Macro F1
  ------------------------------ ---------- ----------------- -------------- ----------
  Rule engine                        36.67%            86.81%         36.67%     35.25%
  TF-IDF + Logistic Regression         100%              100%           100%       100%
  Hybrid system                        100%              100%           100%       100%

Test size:

``` text
180
```

Canonical test errors:

``` text
0
```

## 6. Cross-Validation

5-fold cross-validation:

``` text
Accuracy:        1.0000 ± 0.0000
Macro Precision: 1.0000 ± 0.0000
Macro Recall:    1.0000 ± 0.0000
Macro F1:        1.0000 ± 0.0000
```

All five folds reported 1.0000 for the recorded metrics.

## 7. Independent Challenge Set

``` text
Samples: 20
Correct: 20
Accuracy: 1.0000
```

This is additional benchmark evidence, but the set remains small and
synthetic.

## 8. Hard-Negative Safety Set

Recorded result:

``` text
10 / 10 correct
```

The cases include negated, protective and contextual safety language.

## 9. Threshold Evaluation

At the selected 0.50 validation threshold:

``` text
Precision: 1.0000
Recall:    0.9667
F1:        0.9831
```

Recorded counts:

``` text
TN = 120
FP = 0
FN = 2
TP = 58
```

## 10. Error Analysis

The canonical test set recorded zero classification errors.

This should be interpreted alongside the limitations of the benchmark:

-   synthetic data
-   relatively small dataset
-   deliberately constructed classes
-   limited language distribution
-   no clinical population

## 11. Why 100% Is Not a Clinical Claim

A perfect benchmark can mean the current benchmark is well separated and
that the chosen representation performs well on those examples.

It does not prove:

-   clinical validity
-   real-world generalization
-   guaranteed crisis detection
-   absence of false negatives in real conversations
-   suitability for autonomous healthcare decisions

## 12. Reproducibility

A future release should record:

``` text
dataset version
dataset hash
random seed
Python version
scikit-learn version
training command
model artifact hash
evaluation command
evaluation timestamp
```

## 13. Future Evaluation

Future work, under appropriate governance:

1.  Larger independently curated datasets
2.  Expert-reviewed labels
3.  Out-of-distribution testing
4.  Calibration analysis
5.  Robustness testing
6.  Multilingual evaluation
7.  Adversarial testing
8.  Human review
9.  False-negative analysis
10. Distribution-drift monitoring

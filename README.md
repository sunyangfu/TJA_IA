[![Build Status](http://img.shields.io/travis/badges/badgerbadgerbadger.svg?style=flat-square)](https://travis-ci.org/badges/badgerbadgerbadger) 

# THA - Total Hip Arthroplasty
  
## THA NLP System
Process operative reports to classify a patient's status of approach, fixation and bearing surface
@author Sunyang Fu, Sunghwan Sohn, Hilal Maradit Kremers, Walter Kremers, Ahmad Pahlavan Tafti, Elham Sagheb Hossein Pour, Cody Wyles, Meagan Tibbo, David Lewallen, Daniel Berry
 
## CONFIGURATION:
INPUT_DIR: full directory path of input folder
OUTPUT_DIR: full directory path of output folder
OUTPUT_SUMMARY_DIR: full directory path of output summary folder
RULES_DIR: full directory path of 'TJA' folder

## INPUT:
 Input folder: the input folder contains a list of surgical reports 
 Input file: document level .txt file. The naming convention of each report would be unique identifier + surgery date. P.S. one patient may have multiple surgeries. 
 Input file preprocessing: replace all '/n' to '. '

## RUN:
 command line:
 ```
 ./runMedTagger-fit-tja.sh
```
## OUTPUT:
 raw folder: concept level finding
 summary folder: document level finding

## REFERENCE: 
Wyles CC, Tibbo ME, Fu S, Wang Y, Sohn S, Kremers WK, Berry DJ, Lewallen DG, Maradit-Kremers H. Use of Natural Language Processing Algorithms to Identify Common Data Elements in Operative Notes for Total Hip Arthroplasty. JBJS. 2019 Nov 6;101(21):1931-8.

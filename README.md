# Data Collection Sample Dataset Generator

A Python script to generate a sample dataset representing OEE production environment data. 
 
## Description

### Update! Broken, do not use!
 - (Aug. 18, 2025) There are some large flaws with the generated dataset. The time frame of 3rd shift
is currently 16hours. This is not realistic and needs corrected. This has prompted the need for a more
complete analysis to check for other problems.
 - (Aug. 18, 2025) The comparison between product id and lot number doesn't make a lot of sense for 
record keeping. This also needs corrected.

A script to generate a sample OEE (Overall Equipment Effectiveness) dataset. This dataset is intended
to represent a simulated production data collection system. The dataset covers 6 machines for 3 shifts, 
over 24hrs. Some degree of variation and randomness has been added in an attempt to make the data more 
realistic and simultaneously ensure sufficient points for analysis.

See the included sample, 'production_data.csv'

## Getting Started

If you just need a quick sample dataset download the sample output file, 'production_data.csv'
Or, download/clone the repository. 

### Dependencies

* base Conda environment
* Pandas (if not using Anaconda)

### Executing program

* No special instructions.
* Change variables as desired, run from terminal or inside your ide.
* A .csv file is automatically created in the same directory.

## Help

If you are trying to make changes to variables to get a desired result, first reduce the number of machines
to limit the output and speed up the process. The base script generates 2780 samples, so reducing the output
will significantly speed up iterative testing. Change the default value for num_machines in the function 
arguments at the top of the script.

```
def generate_production_data(start_date, num_machines=6):
```

## Authors

SituationUnknown(AAM1130)


## Version History

* 0.1
    * Initial Release

## License

This project is licensed under the Unlicence - see the LICENSE.md file for details

## Acknowledgments

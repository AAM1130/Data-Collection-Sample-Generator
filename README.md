# Data Collection Sample Dataset Generator

A Python script to generate a sample dataset representing OEE production environment data. 
 
## Description

### Update. Version 0.2
 - (Sep. 09, 2025) Completely revised script. Separate config file. More dynamic variation.

A script to generate a sample OEE (Overall Equipment Effectiveness) dataset. This dataset is intended
to represent a simulated production data collection system. The dataset covers a single order of a set 
number of parts produced by a single work cell of 1 or more machines. Some degree of variation and 
randomness has been added in an attempt to make the data more realistic and simultaneously ensure sufficient
points for analysis.

All variables intended for modification are changeable via the configuration file (config.toml). The
configuration file is intended to be 'human-readable' with comments added.

For example output see the included sample, 'production_data.csv'

## Getting Started

If you just need a quick sample dataset download the sample output file, 'production_data.csv'
Or, download/clone the repository. 

### Dependencies

* pandas
* toml

### Executing program

* Nearly all settings are available in config.toml. Save in the same directory as the script.
* Change variables in config.toml as desired, run the script from terminal or inside your ide.
* A .csv file is automatically created in the same directory. The name of the generated file is 
set in the config file.

## Help

* All variables intended for modification have been moved to config.toml. 
* 'total_parts' directly effects the total number of rows in the output (+ error entries)
* The generator stops iterating after the total_parts variable is met. 

### Notes:
* This script is intended to simulate data over hours or perhaps a few days, not long time frames.
* There are no controls in place to differentiate weekends or holidays. 

## Authors

SituationUnknown(AAM1130)


## Version History

* 0.2
    * Full revision of dynamic and constant variables
    * config.toml used for quick over-write of default variables and easy configuration.
    * NEEDS testing

* 0.1
    * Initial Release
    * schedule issues and lack of dynamic data

## License

This project is licensed under the Unlicence - see the LICENSE.md file for details

## Acknowledgments

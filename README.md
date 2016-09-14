Simple module to convert data table (CSV/SAS7BDAT/JSON) into National Death Index (NDI) format released under the MIT license.

## About ##
The formatting and validation convert supported data files into acceptable NDI datasets for submission. The validation is not intended to support an arbitrary NDI file, but one which has been generated by the included formatter.

### Disclaimer ###
No guarantee of any kind is made that this code produces the desired output. Please inspect your own data to ensure that it is correct, and contribute to improve the current formatter/validator.

### References ###
* National Center for Health Statistics. National Death Index user’s guide. Hyattsville, MD. 2013.
* Above cited is available at http://www.cdc.gov/nchs/data/ndi/NDI_Users_Guide.pdf

## Requirements ##
* Python 3.3+
* Optional packages:
    * dateutil: enables inference of date (for birthdate)
    * sas7bdat: enables parsing of sas7bdat files
    
## Prerequisites ##
1. A supported data file with information that needs to be converted to NDI format.
2. Each subject/record must have either...
    *  FIRST and LAST NAME and SOCIAL SECURITY NUMBER
    *  FIRST and LAST NAME and MONTH and YEAR OF BIRTH
    *  SOCIAL SECURITY NUMBER and full DATE OF BIRTH and SEX
4. Install Python 3.3+ 
    * installing Anaconda 3 Python distribution is recommended
    * Anaconda will include the dateutil library by default
5. (Optional) Install optional packages:
    * Install sas7bdat by running `pip install sas7bdat`
    * Install dateutil by running `pip install dateutil`
    * For issues with proxy, try the answers to this SO question: http://stackoverflow.com/questions/14149422/

## Doco ##

### Installation ###
Either with pip:

    pip install ndi_formatter
     
Or download the repository:
    
    git clone git@bitbucket.org:dcronkite/ndi_formatter.git
    cd ndi_formatter
    python setup.py install

### Basics ###
The best way to get started is to figure out which options you need to pass.

    # create a sample configuration file
    ndi-formatter --create-sample >> sample.config
    
    # see all arguments
    ndi-formatter --help
    
    # run with a config file
    ndi-formatter "@configfile.conf"

### Advanced ###
#### Multiple Columns ####
You can output multiple columns on most options (not names or birthdate due to complexities with how they are handled, and not id because that wouldn't make any sense) by inserting a comma-separated set of values to arguments.
 
If the columns have the same input, only one output will be produced. If the columns have different values, then multiple records will be output.

    # option to look at two columns for state of residence
    # if PRIMARY_STATE == SECONDARY_STATE, only one record will be output
    --state-of-residence=PRIMARY_STATE,SECONDARY_STATE

    
### Validation ###
Validation is done during formatting to ensure that patients are eligible to be submitted to NDI (unless suppressed by `--ignore-invalid-record` option).

Additional validation is available by including the [recommended] `--validate-generated-file VALIDATION_ERROR_FILE` option and to optionally supply a file. This will launch the validator on the NDI file generated by formatter.

Validation comes in two forms:
1. Is the data formatted correctly? (Done by validator)
2. Is the record eligibile for NDI review? (Done by both formatter and validator)
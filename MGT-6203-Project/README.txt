DESCRIPTION - Describe the package in a few paragraphs

This code implements 3 different strategies including: barbell, factor-based, and hybrid, and compare the results with SP500. Then we compare the results based on the cumulative return and Sharpe ratio for all those 3 portfolios and compare the results with the benchmark (SP500).

INSTALLATION - How to install and setup your code

Please install all the dependencies and libraries specified under the first cell and then call these libraries
# install.packages('IRkernel') 
# install.packages("rlang", type="binary",dependencies = TRUE)
# install.packages("magrittr", type="binary",dependencies = TRUE) # package installations are only needed the first time you use it
# install.packages("dplyr", type="binary",dependencies = TRUE)    # alternative installation of the %>%
# install.packages("tidyquant", type="binary",dependencies = TRUE)
# install.packages("lubridate", type="binary",dependencies = TRUE)
# install.packages("PerformanceAnalytics", type="binary",dependencies = TRUE)
# install.packages("xts", type="binary",dependencies = TRUE)
# install.packages("ggplot2", type="binary",dependencies = TRUE)
# install.packages("broom", type="binary",dependencies = TRUE)
# install.packages("tidyverse", type="binary",dependencies = TRUE)
# install.packages('timetk', type="binary",dependencies = TRUE)

EXECUTION - How to run a demo on your code

If you would like to run it on your local server,  please follow this steps:
1. Download the Jupyter/rmd code
2. Run the whole code, it will call all the libraries and collect the data and perform the analysis and shows the results and plots

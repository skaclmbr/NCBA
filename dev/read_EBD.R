# Retrieve records, save in text file
library(auk)
library(dplyr)

# path to the ebird data file -------------------------------------------
input_ebd <- auk_get_ebd_path()
input_sampling <- "/Volumes/eBird/ebd_sampling_relDec-2020"

# parameters ------------------------------------------------------------
<<<<<<< HEAD:dev_query_ebd.R
output_file <- "~/NCBA/Data/ebd_filtered.txt"
=======
output_file <- "/users/nmtarr/Documents/NCBA/Data/swwa_filtered.txt"
>>>>>>> dev_nate:dev/read_EBD.R
species <- c("Swainson's Warbler")
#state <- "US-NC"
country <- "US"
bbox <- "bbox = c(-91, 27, -75, 41)" # in decimal degrees
#date <- c("2018-07-01", "2019-12-31") # e.g. date = c("*-05-01", "*-06-30") for observations from May and June of any year.
date <- c("2015-01-01", "2021-12-31")
protocol <- ""
project <- ""
#distance <- c(0,3)
breeding <- ""
complete <- ""

# query -----------------------------------------------------------------
ebird_data <- input_file %>%
  # 1. reference file
  auk_ebd() %>%
  # 2. define filters
  auk_species(species=species) %>%
  auk_date(date=date) %>%
  auk_country(country=country) %>%
  auk_complete() %<%
  # 3. run filtering
  auk_filter(file = output_file, overwrite = TRUE) %>%
  # 4. read text file into r data frame
  read_ebd()

# display ---------------------------------------------------------------------
View(ebird_data)

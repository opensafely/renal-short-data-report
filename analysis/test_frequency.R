################################################################################################
# Produces histograms to show the frequency of eGFR and creatinine tests by year and risk group
# From monthly measures output, so only counts one test each month
#################################################################################################

library(tidyverse)

inputdir<-"output/joined/"  #path to where input files are

dir.create(here::here("output","figures"), showWarnings=FALSE, recursive=TRUE)

filenames<-list.files(inputdir, pattern = glob2rx("input_2*.csv.gz")) #list of relevant input files
filepaths<-paste0(inputdir,filenames)  #...and full paths

dates<-as.Date(substr(filenames,7,16))  #check these numbers for start stop are correct based on filenames

#read in the input files
data<-lapply(filepaths,read_csv, 
             col_types = cols(patient_id = col_integer(),
                              eGFR = col_logical(),
                              at_risk = col_logical(),
                              diabetes = col_logical(),
                              hypertension = col_logical()
                              creatinine = col_logical()
                              ))

######## first eGFR ##########################################################


#keep only those with eGFR measurement, and just the required variables
data1<-lapply(data,subset, eGFR==1, 
              select=c(patient_id, eGFR, at_risk, diabetes, hypertension))
#adding the date as a column
data2<-mapply(function(x,y) cbind(x, date=y), data1, dates, SIMPLIFY=FALSE)
#appending into one dataset
data3<-bind_rows(data2)
#adding year
data3$year<-format(data3$date, "%Y")

#counting the number of months with an eGFR test for each patient, all patients
count.all<-data3 %>% count(patient_id, year)
#plot histogram by year
p.all <- count.all %>%
  ggplot( aes(x=n)) +
  geom_histogram( alpha=0.6, position = 'identity', bins=13) +
  facet_wrap(~year, ncol=1) +
  ggtitle("Number of months with an eGFR test")
#saving
ggsave(
  plot= p.all,
  filename="months_with_eGFR_all.png", path=here::here("output", "figures"),
)

# # repeating for groups
# #need to redo counts as a person's status can change

#at_risk
count.at_risk<-data3 %>% count(patient_id, year, at_risk)
p.at_risk <- count.at_risk %>%
  ggplot( aes(x=n)) +
  geom_histogram( alpha=0.6, position = 'identity', bins=13) +
  facet_grid(year~at_risk)+
ggtitle("Number of months with an eGFR test by risk status")
#saving
ggsave(
  plot= p.at_risk,
  filename="months_with_eGFR_at_risk.png", path=here::here("output", "figures"))

#diabetes
count.diabetes<-data3 %>% count(patient_id, year, diabetes)
p.diabetes <- count.diabetes %>%
  ggplot( aes(x=n)) +
  geom_histogram( alpha=0.6, position = 'identity', bins=13) +
  facet_grid(year~diabetes)+
  ggtitle("Number of months with an eGFR test by risk status")
#saving
ggsave(
  plot= p.diabetes,
  filename="months_with_eGFR_diabetes.png", path=here::here("output", "figures"))

#hypertension
count.hypertension<-data3 %>% count(patient_id, year, hypertension)
p.hypertension <- count.hypertension %>%
  ggplot( aes(x=n)) +
  geom_histogram( alpha=0.6, position = 'identity', bins=13) +
  facet_grid(year~hypertension)+
  ggtitle("Number of months with an eGFR test by risk status")
#saving
ggsave(
  plot= p.hypertension,
  filename="months_with_eGFR_hypertension.png", path=here::here("output", "figures"))


  #################### now creatinine ###################################################


  #keep only those with creatinine measurement, and just the required variables
data1<-lapply(data,subset, creatinine==1, 
              select=c(patient_id, creatinine, at_risk, diabetes, hypertension))
#adding the date as a column
data2<-mapply(function(x,y) cbind(x, date=y), data1, dates, SIMPLIFY=FALSE)
#appending into one dataset
data3<-bind_rows(data2)
#adding year
data3$year<-format(data3$date, "%Y")

#counting the number of months with an creatinine test for each patient, all patients
count.all<-data3 %>% count(patient_id, year)
#plot histogram by year
p.all <- count.all %>%
  ggplot( aes(x=n)) +
  geom_histogram( alpha=0.6, position = 'identity', bins=13) +
  facet_wrap(~year, ncol=1) +
  ggtitle("Number of months with an creatinine test")
#saving
ggsave(
  plot= p.all,
  filename="months_with_creat_all.png", path=here::here("output", "figures"),
)

# # repeating for groups
# #need to redo counts as a person's status can change

#at_risk
count.at_risk<-data3 %>% count(patient_id, year, at_risk)
p.at_risk <- count.at_risk %>%
  ggplot( aes(x=n)) +
  geom_histogram( alpha=0.6, position = 'identity', bins=13) +
  facet_grid(year~at_risk)+
ggtitle("Number of months with a creatinine test by risk status")
#saving
ggsave(
  plot= p.at_risk,
  filename="months_with_creat_at_risk.png", path=here::here("output", "figures"))

#diabetes
count.diabetes<-data3 %>% count(patient_id, year, diabetes)
p.diabetes <- count.diabetes %>%
  ggplot( aes(x=n)) +
  geom_histogram( alpha=0.6, position = 'identity', bins=13) +
  facet_grid(year~diabetes)+
  ggtitle("Number of months with a creatinine test by risk status")
#saving
ggsave(
  plot= p.diabetes,
  filename="months_with_creat_diabetes.png", path=here::here("output", "figures"))

#hypertension
count.hypertension<-data3 %>% count(patient_id, year, hypertension)
p.hypertension <- count.hypertension %>%
  ggplot( aes(x=n)) +
  geom_histogram( alpha=0.6, position = 'identity', bins=13) +
  facet_grid(year~hypertension)+
  ggtitle("Number of months with a creatinine test by risk status")
#saving
ggsave(
  plot= p.hypertension,
  filename="months_with_creat_hypertension.png", path=here::here("output", "figures"))
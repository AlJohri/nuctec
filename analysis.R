library("dplyr")
library("ggplot2")

# Note to self
# grouping by school, subject, course_id, catalog_num, title is kind of wrong
# you need to be grouping by JUST course_id and accounting for the differences in
# school, subject, catalog_num, and title <- these change (ever so slightly)

# in addition, grouping by school, subject, instructor is wrong since
# professors can teach in multiple subjects

# Use RStudio Preview 0.99 (it can sort the data frame in view!)

dat <- read.csv("ctecs.csv")

dat_summary_by_course <- dat %>% group_by(school, subject, course_id, catalog_num, title) %>%
  summarise(num_sections = length(id),
            avg_goodness = mean(question1_average_rating),
            avg_learned = mean(question2_average_rating),
            avg_challenged = mean(question3_average_rating),
            avg_easiness = mean(easiness)) %>% 
  filter(num_sections > 3) %>% ungroup()

dat_summary_by_instructor <- dat %>% group_by(school, subject, instructor) %>%
  summarise(num_sections = length(id),
            avg_instruction = mean(question0_average_rating),
            avg_stimulated = mean(question4_average_rating)) %>% 
  filter(num_sections > 3) %>% ungroup()

##############################################################################

# SESP
View(head(dat_summary_by_course %>% filter(school == "SESP" & 
  subject == "TEACH_ED" | subject == "LOC" | subject == "HDPS" | subject == "SOC_POL") %>% 
    arrange(desc(avg_challenged)), n = 50))


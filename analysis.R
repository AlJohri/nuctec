library("dplyr")
library("ggplot2")

dat <- read.csv("ctec.csv")

# Note to self
# grouping by school, subject, course_id, catalog_num, title is kind of wrong
# you need to be grouping by JUST course_id and accounting for the differences in
# school, subject, catalog_num, and title <- these change (ever so slightly)

overall_rating_of_instruction <- dat %>% group_by(instructor) %>%
  summarise(avg_instruction = mean(question0_average_rating), num_sections = length(id)) %>%
  filter(num_sections > 3) %>% ungroup() %>% filter(!is.na(avg_instruction))

overall_rating_of_course <- dat %>% group_by(school, subject, course_id, catalog_num, title) %>%
  summarise(avg_goodness = mean(question1_average_rating), num_sections = length(id)) %>%
  filter(num_sections > 3) %>% ungroup() %>% filter(!is.na(avg_goodness))

amount_learned_in_course <- dat %>% group_by(school, subject, course_id, catalog_num, title) %>%
  summarise(avg_learned = mean(question2_average_rating), num_sections = length(id)) %>%
  filter(num_sections > 3) %>% ungroup() %>% filter(!is.na(avg_learned))

amount_challenged_by_course <- dat %>% group_by(school, subject, course_id, catalog_num, title) %>%
  summarise(avg_challenged = mean(question3_average_rating), num_sections = length(id)) %>%
  filter(num_sections > 3) %>% ungroup() %>% filter(!is.na(avg_challenged))

amount_stimulated_by_professor <- dat %>% group_by(instructor) %>%
  summarise(avg_stimulated = mean(question4_average_rating), num_sections = length(id)) %>%
  filter(num_sections > 3) %>% ungroup() %>% filter(!is.na(avg_stimulated))

overall_easiness_of_course <- dat %>% group_by(school, subject, course_id, catalog_num, title) %>%
  summarise(avg_easiness = mean(easiness), num_sections = length(id)) %>%
  filter(num_sections > 3) %>% ungroup() %>% filter(!is.na(avg_easiness))

##############################################################################

View(head(overall_rating_of_instruction %>% arrange(avg_instruction), n = 30))
View(head(overall_rating_of_instruction %>% arrange(desc(avg_instruction)), n = 30))

View(head(overall_rating_of_course %>% arrange(avg_goodness), n = 30))
View(head(overall_rating_of_course %>% arrange(desc(avg_goodness)), n = 30))

View(head(amount_learned_in_course %>% arrange(avg_learned), n = 30))
View(head(amount_learned_in_course %>% arrange(desc(avg_learned)), n = 30))

View(head(amount_challenged_by_course %>% arrange(avg_challenged), n = 30))
View(head(amount_challenged_by_course %>% arrange(desc(avg_challenged)), n = 30))

View(head(amount_stimulated_by_professor %>% arrange(avg_stimulated), n = 30))
View(head(amount_stimulated_by_professor %>% arrange(desc(avg_stimulated)), n = 30))

View(head(overall_easiness_of_course %>% arrange(avg_easiness), n = 30))
View(head(overall_easiness_of_course %>% arrange(desc(avg_easiness)), n = 30))

##############################################################################

View(head(overall_rating_of_course %>% filter(school == "WCAS") %>% arrange(avg_goodness), n = 50))
View(head(overall_rating_of_course %>% filter(school == "WCAS") %>% arrange(desc(avg_goodness)), n = 50))

View(head(amount_challenged_by_course %>% filter(school == "WCAS") %>% arrange(avg_challenged), n = 50))
View(head(amount_challenged_by_course %>% filter(school == "WCAS") %>% arrange(desc(avg_challenged)), n = 50))

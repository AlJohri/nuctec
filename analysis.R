library("dplyr")
library("ggplot2")

# Note to self
# grouping by school, subject, course_id, catalog_num, title is kind of wrong
# you need to be grouping by JUST course_id and accounting for the differences in
# school, subject, catalog_num, and title <- these change (ever so slightly)

# in addition, grouping by school, subject, instructor is wrong since
# professors can teach in multiple subjects

# Use RStudio Preview 0.99 (it can sort the data frame in view!)

# Perhaps when i group by course, i should also add instructor in the mix

ctecs <- read.csv("ctecs.csv")

ctecs_by_course <- ctecs %>% group_by(school, subject, course_id, catalog_num, title) %>%
  summarise(num_sections = length(id),
            avg_goodness = mean(question1_average_rating),
            avg_learned = mean(question2_average_rating),
            avg_challenged = mean(question3_average_rating),
            avg_easiness = mean(easiness),
            avg_hardness = mean(hardness),
            something = mean(easiness) - mean(hardness),
            easy_a_ness = mean(easy_a)) %>% 
  filter(num_sections > 3) %>% ungroup()

ctecs_by_instructor <- ctecs %>% group_by(school, subject, instructor) %>%
  summarise(num_sections = length(id),
            num_terms = length(unique(term)),
            avg_instruction = mean(question0_average_rating),
            avg_stimulated = mean(question4_average_rating)) %>% 
  filter(num_sections > 3) %>% ungroup()

ctecs_by_course_and_instructor <- ctecs %>% group_by(school, subject, course_id, catalog_num, title, instructor) %>%
  summarise(num_sections = length(id),
            avg_instruction = mean(question0_average_rating),
            avg_goodness = mean(question1_average_rating),
            avg_learned = mean(question2_average_rating),
            avg_challenged = mean(question3_average_rating),
            avg_stimulated = mean(question4_average_rating),
            avg_easiness = mean(easiness),
            avg_hardness = mean(hardness),
            something = mean(easiness) - mean(hardness)) %>% 
  filter(num_sections > 3) %>% ungroup()

# View(ctecs_by_course_and_instructor %>% filter(grepl('^(2|3)', catalog_num)))

##############################################################################

# SESP
View(head(dat_summary_by_course %>% filter(school == "SESP" & 
  subject == "TEACH_ED" | subject == "LOC" | subject == "HDPS" | subject == "SOC_POL") %>% 
    arrange(desc(avg_challenged)), n = 50))

##############################################################################

# Can we compare how long a professor has been here to how good they are?

reg1 <- lm(num_terms ~ avg_instruction,data=ctecs_by_instructor)
par(cex=.8)
plot(ctecs_by_instructor$num_terms, ctecs_by_instructor$avg_instruction)
abline(reg1)
summary(reg1)

##############################################################################

# library("e1071")
# library("tm")
# library("slam")

# ctecs_by_course_with_essays <- ctecs %>% group_by(school, subject, course_id, catalog_num, title) %>%
#   summarise(num_sections = length(id),
#             essays = paste(essay, sep="\n", collapse = ""),
#             avg_goodness = mean(question1_average_rating),
#             avg_learned = mean(question2_average_rating),
#             avg_challenged = mean(question3_average_rating),
#             avg_easiness = mean(easiness),
#             avg_hardness = mean(hardness)) %>% 
#   filter(num_sections > 3) %>% ungroup()

# # http://handsondatascience.com/TextMiningO.pdf

# # http://stackoverflow.com/questions/23446578/naive-bayes-classification-with-r
# # http://stackoverflow.com/questions/21163207/document-term-matrix-for-naive-bayes-classfier-unexpected-results-r

# toSpace <- content_transformer(function(x, pattern) gsub(pattern, " ", x))
# y <- ctecs_by_course_with_essays$avg_easiness > mean(ctecs_by_course_with_essays$avg_easiness)
# control <- list(stopwords = FALSE, removePunctuation = TRUE, removeNumbers = TRUE, minDocFreq = 2)
# docs <- Corpus(VectorSource(ctecs_by_course_with_essays$essays))
# docs <- tm_map(docs, content_transformer(tolower))
# docs <- tm_map(docs, toSpace, "/")

# dtm <- DocumentTermMatrix(docs, control)
# freq <- colSums(as.matrix(dtm))
# ord <- order(freq)
# freq[head(ord)]
# freq[tail(ord)]

# m <- t(as.matrix(dtm))
# write.csv(m, file="dtm.csv")

# rowTotals <- apply(dtm , 1, sum)
# dtm <- dtm[rowTotals> 0, ]

# classifier <- naiveBayes(as.matrix(t(dtm)), as.factor(y))
# table(predict(classifier, y), y)

# results <- predict(object=classifier,newdata=as.factor(y));


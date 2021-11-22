#reference: https://jesuscaro.org/portfolio/austrev/
#https://www.tidytextmining.com/sentiment.html
library(readr)
library(dplyr)
library(tidytext)
library(stringr)
library(ggplot2)
library(plotly)
library(reshape2)
library(wordcloud)
library(tidyr)
library(igraph)
library(ggraph)
library(widyr)

PorQueNo<- read.csv(file = 'C:/Users/lesli/pythonProject2/Business Analytics/PorQueNo.csv')

#Rename the "text" column since text in R is a function
names(PorQueNo)[names(PorQueNo) == 'text'] <- "review" 
colnames(PorQueNo)

#Need to remove some of the important stop_words from list

View(stop_words)
#look at most used stop_words
review_stop_words <- PorQueNo %>%
  select(review_id, business_id, review_stars, review) %>%
  unnest_tokens(word, review) %>%
  filter(word %in% stop_words$word,
         str_detect(word, "^[a-z']+$"))

review_stop_words %>%
  count(word, sort = TRUE) %>%
  filter(n > 600) %>%
  mutate(word = reorder(word, n)) %>%
  ggplot(aes(n, word)) +
  geom_col() +
  labs(y = NULL)

review_stop_words %>%
  count(word, sort = TRUE)%>%
  filter(n > 400)

#modify list of stop_words
StopWords<-stop_words%>%
  filter(!stop_words$word %in% c('long','little','order','small','high','great','good','place','inside'))

#remove stopwords and custom stop words
custom_stop <- tribble(~word, ~ lexicon, "por", "que", "portland", "food","pretty","pqn","porque" )
custom_stop <- StopWords %>% bind_rows(custom_stop)

custom_stop$word %>%
  tail(n = 1000)


########################
#head(PorQueNo)

#Notice this converts to one-row-per-term-per-document: the tidy text form. 
#In this cleaning process we've also removed "stopwords" 
#and things that are formatting (e.g. "--") rather than a word.

review_words <- PorQueNo %>%
  select(review_id, business_id, review_stars, review) %>%
  unnest_tokens(word, review) %>%
  filter(!word %in% custom_stop$word,
         str_detect(word, "^[a-z']+$"))

review_words


#look at most popular words
review_words %>%
  count(word, sort = TRUE) %>%
  filter(n > 600) %>%
  mutate(word = reorder(word, n)) %>%
  ggplot(aes(n, word)) +
  geom_col() +
  labs(y = NULL)

review_words %>%
  count(word, sort = TRUE)

#get sentiments for reviews################################################

#tokenize each word, filter out stop words, and join nrc sentiment dictionary. 
PorQue_Sentiment <- PorQueNo %>% 
  unnest_tokens(word, review) %>% 
  anti_join(custom_stop, by = "word") %>% 
  inner_join(get_sentiments("nrc"), by = "word") 

head(PorQue_Sentiment)

#Select only the star rating, word and sentiment of the word, group by the star 
#rating and count the sentiment. 
PorQue_Sentiment %<>% 
  select(review_stars, word, sentiment) %>% 
  group_by(review_stars) %>% 
  count(sentiment) 
head(PorQue_Sentiment)

# group by the star rating (1,3,5) and find the percentage of each sentiment term. Filter out 2 & 4

#notice the plots below have increased joy and positive as rating goes up, whereas as rating goes down, 
#we get increased negative emotions, like disgust, fear, and anger

PorQue_Sentiment %<>% 
  group_by(review_stars) %>% 
  mutate(SentPerc = n/sum(n) * 100) %>% 
  filter(review_stars %in% c(1,3,5))
# Apply arbitrary values to valence for color fill
PorQue_Sentiment[PorQue_Sentiment$sentiment %in% c("anger", "disgust", "fear", "negative", "sadness"),"valence"] <- -1
PorQue_Sentiment[PorQue_Sentiment$sentiment %in% c("anticipation", "joy", "positive", "trust"),"valence"] <- 1
PorQue_Sentiment[PorQue_Sentiment$sentiment %in% c("surprise"),"valence"] <- 0
# plot
sentplot <- ggplot(PorQue_Sentiment, aes(sentiment, SentPerc, fill = valence)) + facet_wrap(~review_stars) + geom_col() +scale_fill_gradient(low='#d6634d', high='#3961a0') + theme(axis.text.x = element_text(angle = 45, hjust = 1, vjust = 0.5)) 
ggplotly(sentplot)

#comparison cloud##########################################

review_words %>%
  inner_join(get_sentiments("bing")) %>%
  count(word, sentiment, sort = TRUE) %>%
  acast(word ~ sentiment, value.var = "n", fill = 0) %>%
  comparison.cloud(colors = c("gray20", "gray80"),
                   max.words = 50)



#NGRAMS#########################################################

PorQueNo_bigrams <- PorQueNo %>%
  unnest_tokens(bigram, review, token = "ngrams", n = 2)

#drop stopwords
bigrams_separated <- PorQueNo_bigrams %>%
  separate(bigram, c("word1", "word2"), sep = " ")

bigrams_filtered <- bigrams_separated %>%
  filter(!word1 %in% custom_stop$word) %>%
  filter(!word2 %in% custom_stop$word)

# new bigram counts:
bigram_counts <- bigrams_filtered %>% 
  count(word1, word2, sort = TRUE)

bigrams_united <- bigrams_filtered %>%
  unite(bigram, word1, word2, sep = " ")

bigrams_united


####TRI-GRAMS (there's not many)

PorQueNo_trigrams <- PorQueNo %>%
  unnest_tokens(trigram, review, token = "ngrams", n = 3)

#drop stopwords
trigrams_separated <- PorQueNo_trigrams %>%
  separate(trigram, c("word1", "word2","word3"), sep = " ") %>%
  filter(!word1 %in% custom_stop$word,
         !word2 %in% custom_stop$word,
         !word3 %in% custom_stop$word)%>%
  count(word1, word2, word3, sort = TRUE)

trigrams_united <- trigrams_separated %>%
  unite(trigram, word1, word2, word3, sep = " ")

trigrams_united
#####################################################################
#tell how often words are preceded by a word like "not"
bigrams_separated %>%
  filter(word1 == "not") %>%
  count(word1, word2, sort = TRUE)

'For example, the most common sentiment-associated word to follow "not" was 
"worth", which would normally have a (positive) score of 2.'
AFINN <- get_sentiments("afinn")

not_words <- bigrams_separated %>%
  filter(word1 == "not") %>%
  inner_join(AFINN, by = c(word2 = "word")) %>%
  count(word2, value, sort = TRUE)

'It's worth asking which words contributed the most in the "wrong" direction. 
To compute that, we can multiply their value by the number of times they appear
(so that a word with a value of +3 occurring 10 times has as much impact as a 
word with a sentiment value of +1 occurring 30 times). We visualize the result
with a bar plot (Figure 4.2).'

not_words %>%
  mutate(contribution = n * value) %>%
  arrange(desc(abs(contribution))) %>%
  head(20) %>%
  mutate(word2 = reorder(word2, contribution)) %>%
  ggplot(aes(n * value, word2, fill = n * value > 0)) +
  geom_col(show.legend = FALSE) +
  labs(x = "Sentiment value * number of occurrences",
       y = "Words preceded by \"not\"")

#negation terms
negation_words <- c("not", "no", "never", "without")

negated_words <- bigrams_separated %>%
  filter(word1 %in% negation_words) %>%
  inner_join(AFINN, by = c(word2 = "word")) %>%
  count(word1, word2, value, sort = TRUE)
  
negated_words %>%
  mutate(contribution = n * value) %>%
  arrange(desc(abs(contribution))) %>%
  head(20) %>%
  mutate(word2 = reorder(word2, contribution)) %>%
  ggplot(aes(n * value, word2, fill = n * value > 0)) +
  geom_col(show.legend = FALSE) +
  labs(x = "Sentiment value * number of occurrences",
       y = "Words preceded by negation term")

################################################################
#Visualizing networks
# original counts
bigram_counts

# filter for only relatively common combinations
bigram_graph <- bigram_counts %>%
  filter(n > 20) %>%
  graph_from_data_frame()

bigram_graph

set.seed(2017)

ggraph(bigram_graph, layout = "fr") +
  geom_edge_link() +
  geom_node_point() +
  geom_node_text(aes(label = name), vjust = 1, hjust = 1)

set.seed(2020)

a <- grid::arrow(type = "closed", length = unit(.15, "inches"))

ggraph(bigram_graph, layout = "fr") +
  geom_edge_link(aes( ), colour ='grey',show.legend = TRUE,
                 arrow = a, end_cap = circle(.07, 'inches')) +
  geom_node_point(color = "lightblue", size = 5) +
  geom_node_text(aes(label = name), vjust = 1, hjust = 1) +
  theme_void()

#words that co-occur####################################
PorQue_section_words <- PorQueNo %>%
  mutate(section = row_number() %/% 10) %>%
  filter(section > 0) %>%
  unnest_tokens(word, review) %>%
  filter(!word %in% custom_stop$word)

PorQue_section_words

word_pairs <- PorQue_section_words %>%
  pairwise_count(word, section, sort = TRUE)

word_pairs


#FUNCTION TO Count & visualize bigrams (same as above but now it's a function, so more condensed) 
#from https://www.tidytextmining.com/ngrams.html********************************************

count_bigrams <- function(dataset) {
  dataset %>%
    unnest_tokens(bigram, review, token = "ngrams", n = 2) %>%
    separate(bigram, c("word1", "word2"), sep = " ") %>%
    filter(!word1 %in% custom_stop$word,
           !word2 %in% custom_stop$word) %>%
    count(word1, word2, sort = TRUE)
}


visualize_bigrams <- function(bigrams) {
  set.seed(2016)
  a <- grid::arrow(type = "closed", length = unit(.15, "inches"))
    
bigrams %>%
  graph_from_data_frame() %>%
  ggraph(layout = "fr") +
  geom_edge_link(aes(),colour ='grey', show.legend = TRUE, arrow = a,
                 end_cap = circle(.07, 'inches')) +
  geom_node_point(color = "lightblue", size = 5) +
  geom_node_text(aes(label = name), vjust = 1, hjust = 1) +
  theme_void()
}

PorQue_bigrams<-PorQueNo %>%
  count_bigrams()

PorQue_bigrams %>%
  filter(n > 10,
         !str_detect(word1, "\\d"),
         !str_detect(word2, "\\d")) %>%
  visualize_bigrams()

#######################
#Call functions

PorQue_bigrams %>%
  filter(word1 == "tacos" | word2 == "tacos") %>%
  filter(n > 5) %>%
  visualize_bigrams()

PorQue_bigrams %>%
  filter(word1 == "salad" | word2 == "salad") %>%
  filter(n > 1) %>%
  visualize_bigrams()

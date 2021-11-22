import pandas as pd
import seaborn as sns
import spacy

nlp = spacy.load('en_core_web_sm')
import scattertext

import nltk
from nltk.corpus import stopwords
pd.set_option('display.max_columns', None)
# Analyzing Yelp Dataset with Scattertext spaCy
# https://towardsdatascience.com/analyzing-yelp-dataset-with-scattertext-spacy-82ea8bb7a60e
# count restaurants and reviews
path = r"C:\Users\lesli\pythonProject2\Business Analytics\Yelp_Mexican_Restaurant_csv.csv"
df = pd.read_csv(path)
# group the ratings
sns.histplot(df['review_stars'])

# consolodate reviews to high and low
df['rating'] = df['review_stars'].replace(
    {1: 'Low Rating', 2: 'Low Rating', 3: 'Low Rating',
     4: 'High Rating', 5: 'High Rating'})

'''Next, we will use the function below to:
1) Set up our corpus, a collection of texts from the dataset
2) Get term frequency and scaled f-score
3) Create data frames in descending order for High Rating & Low Rating'''

#remove more stop words
#import from natural language Toolkit

stopWords = set(stopwords.words('english'))
nlp.Defaults.stop_words |= stopWords

#pull the restaurant with the most reviews
most_reviews=df.groupby('name').size().max()
num_reviews=df.groupby('name').size()
print(num_reviews[num_reviews==num_reviews.max()])

#rerun, this time only keeping ratings for "Por Qué No? Taqueria" restaurant (2425 reviews)
df_por_que_no = df[df['name']=='Por Qué No? Taqueria']
pd.crosstab(df_por_que_no['review_stars'], df_por_que_no['text'].count())

def term_freq(df_yelp):
    corpus = (scattertext.CorpusFromPandas(df_yelp,
                                           category_col='rating',
                                           text_col='text',
                                           nlp=nlp)
              .build()
              .remove_terms(nlp.Defaults.stop_words, ignore_absences=True)
              )
    df = corpus.get_term_freq_df()
    df['High_Rating_Score'] = corpus.get_scaled_f_scores('High Rating')
    df['Low_Rating_Score'] = corpus.get_scaled_f_scores('Low Rating')
    df['High_Rating_Score'] = round(df['High_Rating_Score'], 2)
    df['Low_Rating_Score'] = round(df['Low_Rating_Score'], 2)

    df_high = df.sort_values(by='High Rating freq',
                             ascending=False).reset_index()
    df_low = df.sort_values(by='Low Rating freq',
                            ascending=False).reset_index()
    return df_high, df_low, corpus


#save file
#html_file_name = "MexicanRestaurantsPortland-Yelp-Review-Scattertext.html"
#open(html_file_name, 'wb').write(html.encode('utf-8'))
high_scores, low_scores, corpus = term_freq(df_por_que_no)

'''Understanding the Scoring System
Scattertext uses scaled f-score, which takes into account the category-specific precision and term frequency. 
While a term may appear frequently in both categories (High and Low rating), the scaled f-score determines whether 
the term is more characteristic of a category than others (High or Low rating).
For example, while the term park is frequent in both High and Low rating, the scaled f-score concludes park is 
more associated with High 0.90 than Low 0.10 rating. Thus, when a review includes the term park it is more 
characteristic of a High rating category.'''
print(high_scores.sort_values('High_Rating_Score', ascending = False)[['term','High_Rating_Score','Low_Rating_Score']].head(20))
print(low_scores.sort_values('Low_Rating_Score', ascending = False)[['term','High_Rating_Score','Low_Rating_Score']].head(20))

'''Scattertext Visualization
Understanding Scattertext plot
On the right side there are the top rated terms and an unordered list of terms under characteristic. 
If we click on the term, it will show us the specific reviews that were inside the dataset, indicating as 
Low or High rating. We can also manually search for a term on the bottom left-hand side.
From the scatter plot, we get a quick glance at the terms used in the reviews. 
The red dots on the right side of the plot indicate terms that are more associated with a High rating while 
blue dots on the left side indicate terms that are more associated with a Low rating.'''
corpus_dataframe = df_por_que_no

html = scattertext.produce_scattertext_explorer(
                   corpus,
                   category='Low Rating',
                   category_name='Low Rating',
                   not_category_name='High Rating',
                   width_in_pixels=1000,
                   metadata=corpus_dataframe['name'])

#save filehtml_file_name = "Por_Que_Non-Yelp-Review-Scattertext.html"
#open(html_file_name, 'wb').write(html.encode('utf-8'))


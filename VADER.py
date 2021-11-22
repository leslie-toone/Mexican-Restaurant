import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
import numpy as np
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
sid = SentimentIntensityAnalyzer()
from wordcloud import WordCloud

pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', 2000)

path = r"C:\Users\lesli\pythonProject2\Business Analytics\Yelp_Mexican_Restaurant_csv.csv"
df = pd.read_csv(path)

'''only keep Por Que No'''
df = df[df['name']=='Por Qué No? Taqueria']
# group the ratings
sns.histplot(df['review_stars'])
print(df['review_stars'].value_counts())

#pie chart of star reviews for Por Que No
group_names=df['review_stars'].value_counts().index
group_counts = ['{0:0.0f}'.format(value) for value in df['review_stars'].value_counts()]
group_percentages = ['{0:.1%}'.format(value) for value in df['review_stars'].value_counts() / np.sum(df['review_stars'].value_counts())]
labels = [f'{v1} Stars\n {v2}' for v1, v2 in zip(group_names, group_counts)]
fig = plt.figure(figsize=(10, 7))

sizes  = df['review_stars'].value_counts()
plt.pie(sizes, labels = labels,autopct='%1.1f%%') # autopct='%1.1f%%' gives you percentages printed in every slice.
plt.axis('equal')  # Ensures that pie is drawn as a circle.
plt.title("Review Stars", fontsize = 18)
plt.show()

# consolodate reviews to high and low and neutral
df['rating'] = df['review_stars'].replace(
    {1: 'Low Rating', 2: 'Low Rating', 3: 'Neutral Rating',
     4: 'High Rating', 5: 'High Rating'})

df['rating'].value_counts()

#pie chart of consolodated groups
labels=df['rating'].value_counts().index
group_names=df['rating'].value_counts().index
group_counts = ['{0:0.0f}'.format(value) for value in df['rating'].value_counts()]
group_percentages = ['{0:.1%}'.format(value) for value in df['rating'].value_counts() / np.sum(df['rating'].value_counts())]
labels = [f'{v1} Stars\n {v2}' for v1, v2 in zip(group_names, group_counts)]

fig = plt.figure(figsize=(10, 7))
#labels = ['negative', 'neutral', 'positive']
sizes  = df['rating'].value_counts()
plt.pie(sizes, labels = labels,autopct='%1.1f%%') # autopct='%1.1f%%' gives you percentages printed in every slice.
plt.axis('equal')  # Ensures that pie is drawn as a circle.
plt.title("Review Stars", fontsize = 18)
plt.show()

#We don't need to remove stop words since Word Cloud already does that for us
#using SentimentIntensityAnalyzer from vader we get a polarity score that measures sentiment strength
# based on the input text. Positive values are positive valence, negative value are negative valence. We use this score
#to make our wordcloud

df['scores'] = df['text'].apply(lambda text: sid.polarity_scores(text))

'''Now will call out compound as a separate column and make a pie chart.'''
df['compound']  = df['scores'].apply(lambda score_dict: score_dict['compound'])
#We want to pull out the really strong text to see what needs to be improved, that's why use .5 cutoff
df['summary']= np.select([df['compound'] < -0.5, df['compound'] > 0.5], ['Negative','Positive'],default='Neutral')

print(df[['compound','summary']])
print(df['summary'].value_counts())

#labels=df['summary'].value_counts().index
group_names=df['summary'].value_counts().index
group_counts = ['{0:0.0f}'.format(value) for value in df['summary'].value_counts()]
group_percentages = ['{0:.1%}'.format(value) for value in df['summary'].value_counts() / np.sum(df['summary'].value_counts())]
labels = [f'{v1} Review\n {v2}' for v1, v2 in zip(group_names, group_counts)]

fig = plt.figure(figsize=(10, 7))
#labels = ['negative', 'neutral', 'positive']
sizes  = df['summary'].value_counts()
plt.pie(sizes, labels = labels,autopct='%1.1f%%') # autopct='%1.1f%%' gives you percentages printed in every slice.
plt.axis('equal')  # Ensures that pie is drawn as a circle.
plt.title("Review Sentiment", fontsize = 18)
plt.show()

#convert data_frame into a CSV file
csv_name= r"C:\Users\lesli\pythonProject2\Business Analytics\PorQueNo.csv"
df.to_csv(csv_name, index=False)

'''create a word cloud based on Vader Sentiment Polarity Score
https://towardsdatascience.com/detecting-bad-customer-reviews-with-nlp-d8b36134dc7e'''

high_star=df[df['compound']>.5]
high_review = " ".join(review for review in high_star.text)

low_star=df[df['compound']<-.5]
low_review = " ".join(review for review in low_star.text)

def show_wordcloud(data, title=None,color=None):
    wc=wordcloud = WordCloud(
        background_color='white',
        colormap=color,
        max_words=200,
        max_font_size=40,
        scale=3,
        random_state=42
    ).generate(str(data))

    fig = plt.figure(1, figsize=(10, 10))
    plt.axis('off')
    plt.title(title, fontsize=32)

    plt.imshow(wordcloud)
    plt.show()


# print wordcloud
show_wordcloud(low_review,'Negative Reviews')

show_wordcloud(high_review,'Positive Reviews',"Dark2")


#print(df.text[df['review_stars']<=3])

'https://towardsdatascience.com/detecting-bad-customer-reviews-with-nlp-d8b36134dc7e'
#highest positive sentiment reviews
print(df.sort_values('compound', ascending = False)[["summary","compound","text"]].head(5))

# highest negative sentiment reviews
print(df.sort_values('compound', ascending = True)[["summary","compound","text"]].head(5))

#THIS CODE HANDY IF YOU WANT TO FILTER REVIEWS AND PRINT ONLY CERTAIN COLUMNS
#print(df[df['review_stars']<=3].sort_values('compound', ascending = False)[["summary","compound","text"]].head(10))

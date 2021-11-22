'''https://towardsdatascience.com/converting-yelp-dataset-to-csv-using-pandas-2a4c8f03bd88'''
#https://www.yelp.com/dataset/documentation/main

import pandas as pd

#Contains business data including location data, attributes, and categories
business_json_path =r"C:\Users\lesli\pythonProject2\Business Analytics\yelp_dataset\yelp_academic_dataset_business.json"
df_b = pd.read_json(business_json_path, lines=True)
#drop businesses that are closed
# 1 = open, 0 = closed
df_b = df_b[df_b['is_open']==1]

#find Mexican restaurants in portland

df_b = df_b[(df_b['categories'].str.contains('Restaurants')) &(df_b['categories'].str.contains('Mexican')) & (df_b['city']=='Portland')]

pd.set_option('display.max_columns', None)
df_b.sort_values(by=['review_count'])
#print(df_b.head())

drop_columns = ['hours','is_open']
df_b = df_b.drop(drop_columns, axis=1)

#Contains full review text data including the user_id that wrote the review and the business_id the review is written for.
#In this dataset of review.json, there are more than 6 million reviews (rows).
# Reducing the chunk size might be easier to load and check the results faster.
business_review_json_path = r'C:\Users\lesli\pythonProject2\Business Analytics\yelp_dataset\yelp_academic_dataset_review.json'
size = 1000000
#Identifying the data type of each column can reduce memory usage.
review = pd.read_json(business_review_json_path, lines=True,
                      dtype={'review_id':str,'user_id':str,
                             'business_id':str,'stars':int,
                             'date':str,'text':str,'useful':int,
                             'funny':int,'cool':int},
                      chunksize=size)
#By merging only the relevant businesses to the review file, the final dataset will only consist of reviews from those businesses.
chunk_list = []
for chunk_review in review:
    # Drop columns that aren't needed
    chunk_review = chunk_review.drop(['useful','funny','cool'], axis=1)
    # Renaming column name to avoid conflict with business overall star rating
    chunk_review = chunk_review.rename(columns={'stars': 'review_stars'})
    # Inner merge with edited business file so only reviews related to the business remain
    chunk_merged = pd.merge(df_b, chunk_review, on='business_id', how='inner')
    # Show feedback on progress
    print(f"{chunk_merged.shape[0]} out of {size:,} related reviews")
    chunk_list.append(chunk_merged)
# After trimming down the review file, concatenate all relevant data back to one dataframe
df = pd.concat(chunk_list, ignore_index=True, join='outer', axis=0)

#convert data_frame into a CSV file
csv_name= "Yelp_Mexican_Restaurant_csv.csv"
df.to_csv(csv_name, index=False)

print(len(df),df.columns)
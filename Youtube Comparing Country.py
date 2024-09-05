### IMPORTING LIBRARY AND SETTINGS
import pandas as pd
import numpy as np
from googleapiclient.discovery import build
import matplotlib.pyplot as plt
import seaborn as sns
import isodate

sns.set(style = "whitegrid")

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 100)
pd.set_option('display.width', 500)
pd.set_option('display.float_format', lambda x: '%.3f' % x)

API_KEY = 'AIzaSyDiBwDE5CWvaD2wWj3MNmiw8loGMknm9eQ'


#### READING DATA AND EXPLORATORY DATA ANALYSIS
""" USA """
trending_videos_USA = pd.read_csv('datasets/sample_projects/trending_videos_USA.csv')
print(trending_videos_USA.head())

trending_videos_USA.isnull().sum()
trending_videos_USA.info()

descriptive_stats = trending_videos_USA[['view_count', 'like_count', 'comment_count']].describe()
print(descriptive_stats)

# for trending 200 videos these columns have the value 0
trending_videos_USA.dislike_count.value_counts()
trending_videos_USA.favorite_count.value_counts()

# filling NA values
trending_videos_USA['description'].fillna('No description', inplace = True)

# convert `published_at` to datetime
trending_videos_USA['published_at'] = pd.to_datetime(trending_videos_USA['published_at'])

# convert tags from string representation of list to actual list
trending_videos_USA['tags'] = trending_videos_USA['tags'].apply(lambda x: eval(x) if isinstance(x, str) else x)

# Number of channels with more than one trending video
video_by_channel = (trending_videos_USA.
                    groupby("channel_title")["video_id"]
                    .count()
                    .reset_index()
                    .sort_values("video_id", ascending = False))
more_trend_channel = video_by_channel[video_by_channel["video_id"] > 1].reset_index(drop = True)
print(more_trend_channel.head(),
      "\n------------------------------------------",
      "\nNumber of channels with more than one trending video:",
      more_trend_channel['channel_title'].nunique())

""" GERMANY """
trending_videos_DE = pd.read_csv('datasets/sample_projects/trending_videos_DE.csv', encoding = "utf-8")
print(trending_videos_DE.head())

trending_videos_DE.isnull().sum()
trending_videos_DE.info()

descriptive_stats = trending_videos_DE[['view_count', 'like_count', 'comment_count']].describe()
print(descriptive_stats)

# for trending 200 videos these columns have the value 0
trending_videos_DE.dislike_count.value_counts()
trending_videos_DE.favorite_count.value_counts()

# filling NA values
trending_videos_DE['description'].fillna('No description', inplace = True)

# convert `published_at` to datetime
trending_videos_DE['published_at'] = pd.to_datetime(trending_videos_USA['published_at'])

# convert tags from string representation of list to actual list
trending_videos_DE['tags'] = trending_videos_DE['tags'].apply(lambda x: eval(x) if isinstance(x, str) else x)

# Number of channels with more than one trending video
video_by_channel = (trending_videos_DE.
                    groupby("channel_title")["video_id"]
                    .count()
                    .reset_index()
                    .sort_values("video_id", ascending = False))
more_trend_channel = video_by_channel[video_by_channel["video_id"] > 1].reset_index(drop = True)
print(more_trend_channel.head(),
      "\n------------------------------------------",
      "\nNumber of channels with more than one trending video:",
      more_trend_channel['channel_title'].nunique())


### 1- CATEGORIES
youtube = build('youtube', 'v3', developerKey = API_KEY)

def get_category_mapping():
    request = youtube.videoCategories().list(
        part = 'snippet',
        regionCode = 'US'
    )
    response = request.execute()
    category_mapping = {}
    for item in response['items']:
        category_id = int(item['id'])
        category_name = item['snippet']['title']
        category_mapping[category_id] = category_name
    return category_mapping


# get the category mapping
category_mapping = get_category_mapping()
print(category_mapping)

trending_videos_USA['category_name'] = trending_videos_USA['category_id'].map(category_mapping)
trending_videos_DE['category_name'] = trending_videos_DE['category_id'].map(category_mapping)

dataframes = [trending_videos_USA, trending_videos_DE]
for df in dataframes:
    # Views, Likes, and Comments by Categories
    category_engagement = (df
                           .groupby('category_name')[['view_count', 'like_count', 'comment_count']]
                           .mean()
                           .sort_values(by = 'view_count', ascending = False))

    fig, axes = plt.subplots(1, 3, figsize = (18, 10))

    # view count by category
    sns.barplot(y = category_engagement.index, x = category_engagement['view_count'], ax = axes[0], palette = 'viridis')
    axes[0].set_title('Average View Count by Category')
    axes[0].set_xlabel('Average View Count')
    axes[0].set_ylabel('Category')

    # like count by category
    sns.barplot(y = category_engagement.index, x = category_engagement['like_count'], ax = axes[1], palette = 'viridis')
    axes[1].set_title('Average Like Count by Category')
    axes[1].set_xlabel('Average Like Count')
    axes[1].set_ylabel('')

    # comment count by category
    sns.barplot(y = category_engagement.index, x = category_engagement['comment_count'], ax = axes[2],
                palette = 'viridis')
    axes[2].set_title('Average Comment Count by Category')
    axes[2].set_xlabel('Average Comment Count')
    axes[2].set_ylabel('')

    plt.tight_layout()
    plt.show()


### 2- DURATION
# convert ISO 8601 duration to seconds
""" USA """
trending_videos_USA['duration_seconds'] = (trending_videos_USA['duration']
                                           .apply(lambda x: isodate.parse_duration(x).total_seconds()))

trending_videos_USA['duration_minutes'] = trending_videos_USA['duration_seconds'] / 60

trending_videos_USA['duration_range'] = (pd.cut(trending_videos_USA['duration_seconds'],
                                                bins = [0, 300, 900, 1800, 3600,
                                                        trending_videos_USA['duration_seconds'].max()],
                                                labels = ['0-5 min', '5-15 min', '15-30 min', '30-60 min', '60 plus']))
""" GERMANY """
trending_videos_DE['duration_seconds'] = (trending_videos_DE['duration']
                                          .apply(lambda x: isodate.parse_duration(x).total_seconds()))

trending_videos_DE['duration_minutes'] = trending_videos_DE['duration_seconds'] / 60

trending_videos_DE['duration_range'] = (pd.cut(trending_videos_DE['duration_seconds'],
                                               bins = [0, 300, 900, 1800, 3600,
                                                       trending_videos_DE['duration_seconds'].max()],
                                               labels = ['0-5 min', '5-15 min', '15-30 min', '30-60 min', '60 plus']))
for df in dataframes:
    length_engagement = df.groupby('duration_range')[
        ['view_count', 'like_count', 'comment_count']].mean()

    fig, axes = plt.subplots(1, 3, figsize = (18, 8))

    # view count by duration range
    sns.barplot(y = length_engagement.index, x = length_engagement['view_count'], ax = axes[0], palette = 'magma')
    axes[0].set_title('Average View Count by Duration Range')
    axes[0].set_xlabel('Average View Count')
    axes[0].set_ylabel('Duration Range')

    # like count by duration range
    sns.barplot(y = length_engagement.index, x = length_engagement['like_count'], ax = axes[1], palette = 'magma')
    axes[1].set_title('Average Like Count by Duration Range')
    axes[1].set_xlabel('Average Like Count')
    axes[1].set_ylabel('')

    # comment count by duration range
    sns.barplot(y = length_engagement.index, x = length_engagement['comment_count'], ax = axes[2], palette = 'magma')
    axes[2].set_title('Average Comment Count by Duration Range')
    axes[2].set_xlabel('Average Comment Count')
    axes[2].set_ylabel('')

    plt.tight_layout()
    plt.show()


### 3- TAGS
trending_videos_USA['tag_count'] = trending_videos_USA['tags'].apply(len)
trending_videos_DE['tag_count'] = trending_videos_DE['tags'].apply(len)


### 4- PUBLISH HOUR
trending_videos_USA['publish_hour'] = trending_videos_USA['published_at'].dt.hour
trending_videos_DE['publish_hour'] = trending_videos_DE['published_at'].dt.hour


### 5- TITLE LENGTHS
trending_videos_USA["title_length"] = trending_videos_USA["title"].str.len()
trending_videos_DE["title_length"] = trending_videos_DE["title"].str.len()


### 6- CAPTION
""" USA """
trending_videos_USA.caption.value_counts()
trending_videos_USA.groupby("caption")["view_count"].mean()
trending_videos_USA.groupby("caption")["like_count"].mean()
trending_videos_USA.groupby("caption")["comment_count"].mean()

""" GERMANY """
trending_videos_DE.caption.value_counts()
trending_videos_DE.groupby("caption")["view_count"].mean()
trending_videos_DE.groupby("caption")["like_count"].mean()
trending_videos_DE.groupby("caption")["comment_count"].mean()

for df in dataframes:
    # create a pivot table
    pivot_table = df.pivot_table(index = 'caption',
                                 values = ['view_count', 'like_count', 'comment_count'],
                                 aggfunc = np.mean)

    # 1e3 = 1000, so the data is displayed in thousands scale
    pivot_table_scaled = pivot_table / 1e3

    # create a heatmap
    plt.figure(figsize = (8, 6))
    sns.heatmap(pivot_table_scaled, annot = True, fmt = ".1f", cmap = 'viridis')
    plt.title('Heatmap of Metrics by Caption at Thousands Scale')
    plt.show()


### ADDING COUNTRY INFO
trending_videos_USA["Country"] = "USA"
trending_videos_DE["Country"] = "GERMANY"

data = pd.concat([trending_videos_USA, trending_videos_DE], ignore_index = True)
data.to_csv("datasets/sample_projects/USA_DE_Youtube.csv", index = False)

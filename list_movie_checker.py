# Simple program to webscrape a list on www.icheckmovies.com and cross reference
# whether the movie is available to stream on a specific region of Netflix and/or
# Amazon Prime Video, by cross referencing with www.justwatch.com using the API.

import requests
import bs4
import re
from justwatch import JustWatch

movies = []
years = []
movie_dict = {}
rank = 0

checklist = "https://www.icheckmovies.com/lists/imdbs+top+250/"

# Request webpage of icheckmovies list.

res_movie_list = requests.get(checklist)

# Beautiful Soup scrape movie names and add to movies list.

movie_soup = bs4.BeautifulSoup(res_movie_list.text, features="html.parser")
movie_titles = movie_soup.find_all("h2")
movie_years = movie_soup.find_all(title=re.compile("year"))

for movie_year in movie_years:
    years.append(movie_year.get_text(strip=True))

for movie_title in movie_titles:
    movies.append(movie_title.get_text(strip=True))

del movies[0]
del years[0]

movie_dict = dict(zip(movies, years))

# Loop through movies list, searching for each movie in the justwatch API,
# then finding out if it's available to stream for free and where.
# If it is, it's printed.  Otherwise, it's ignored.

just_watch = JustWatch(country="GB")

for key, value in movie_dict.items():
    results = just_watch.search_for_item(query=key)
    rank += 1

    for result in results["items"]:
        try:
            if result["title"] == key and result["original_release_year"] == int(value):
                length = len(result["offers"])
                for i in range(length):
                    if result["offers"][i]["provider_id"] == 8:
                        print(f"{rank}.\t {key} is available on Netflix.")
                        break
                    if result["offers"][i]["provider_id"] == 9:
                        print(f"{rank}.\t {key} is available on Amazon Prime Video.")
                        break
        except (IndexError, KeyError):
            pass

print("\nDone!")


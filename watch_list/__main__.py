#! /usr/local/bin/python3

# Simple program to webscrape a list on www.icheckmovies.com and cross reference
# whether the movie is available to stream on a specific region of Netflix and/or
# Amazon Prime Video, by cross referencing with www.justwatch.com using the API.

import re
import sys
import datetime

import bs4
import requests
from justwatch import JustWatch
from requests.exceptions import HTTPError


def main():

    movies = []
    years = []
    movie_dict = {}
    save_info = []
    rank = 0

    checklist = input(
        '\nPlease enter the full webaddress of the www.icheckmovies.com list (including "https")\n\n'
    )

    # Request webpage of icheckmovies list.

    try:
        res_movie_list = requests.get(checklist)
    except (HTTPError, Exception):
        print(
            "\nWeb address invalid.  Either it was typed in wrong or the icheckmovies is down.\n"
        )
        sys.exit()

    # Beautiful Soup scrape movie names and release year.

    movie_soup = bs4.BeautifulSoup(res_movie_list.text, features="html.parser")
    movie_titles = movie_soup.find_all("h2")
    movie_years = movie_soup.find_all(title=re.compile("year"))

    # Adds film name to a list.  If the film is not in English (ie, has its
    # English name in the 'aka' field), adds the 'aka' name instead. This makes
    # sure all the names are the English names.

    for element in movie_titles:
        aka = (
            element.next_element.next_element.next_element.next_element.next_element.next_element.next_element.next_element.next_element.next_element.next_element
        )
        if aka.name == "em":
            movies.append(aka.get_text(strip=True))
        else:
            movies.append(element.get_text(strip=True))

    # Adds years to a seperate list, but each year at the same index number as the
    # corresponding film in the film list, so they match.

    for movie_year in movie_years:
        years.append(movie_year.get_text(strip=True))

    # Deletes first item in both lists since it's useless data, and creates a dictionary
    # of film as key, year as value.

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
                if result["title"] == key and result["original_release_year"] == int(
                    value
                ):
                    length = len(result["offers"])
                    for i in range(length):
                        if result["offers"][i]["provider_id"] == 8:
                            save_info.append(streaming_details(rank, key, "Netflix"))
                            break
                        if result["offers"][i]["provider_id"] == 9:
                            save_info.append(
                                streaming_details(rank, key, "Amazon Prime Video")
                            )
                            break
                        if result["offers"][i]["provider_id"] == 38:
                            save_info.append(
                                streaming_details(rank, key, "BBC iPlayer")
                            )
                            break
                        if result["offers"][i]["provider_id"] == 103:
                            save_info.append(streaming_details(rank, key, "All4"))
                            break
            except (IndexError, KeyError):
                pass

    print("\nDone!\n")
    save_to_file(save_info, checklist)


def streaming_details(rank, film, service):
    text_to_save = f"{rank}.\t {film} is available on {service}."
    print(text_to_save)
    return text_to_save


def save_to_file(movies_to_save, checklist_name):
    save_date = datetime.datetime.now()
    save_file_question = input(
        "Would you like to save this to a .txt file? (y/n)\n\n"
    ).lower()
    if save_file_question == "y":
        file_name = input(
            "\nPlease enter a filename:\n(Note: If a file with the same file name already exists in the same location as the program, it will be overwritten)\n\n"
        )
        with open(f"{file_name}.txt", "w") as f:
            f.write(
                f"{checklist_name}\n\nFilms available for streaming as of: {save_date.strftime('%c')}\n\n"
            )
            for name in movies_to_save:
                f.writelines(f"{name}\n")
            print(f'\n\nFile successfully written as "{file_name}.txt"!\n')
            sys.exit()
    else:
        sys.exit()


if __name__ == "__main__":
    main()

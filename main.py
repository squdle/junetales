#!/usr/bin/env python
# June tales
# Generate some information for the June tales group.

import os
from collections import Counter
import re
import argparse
import json


def average_word_length(words):
    """
    Find the average length from a list of words.

    Args:
        words (str[]): List of words to average.

    Returns:
        float : Average word length.
    """
    return sum(len(w) for w in words) / len(words)


def most_common_words(filepath, num=10, ignore=None):
    """
    Find the most common words in a text.

    Args:
        filepath (str): relative or abs file path of the text.
        num=10 (int): number of top words to find.

    Returns:
        (Counter) Counter object of the top n occuring words.
    """
    ignore = ignore or []
    with open(filepath, "r") as file: 
        words = [
            re.sub("[^a-zA-Z-]", "", w.lower()).strip('-')
            for w in file.read().split()
        ]
        return Counter(words)


def learn_ignore(filepath, ignore_filepath, num=10, ignore=None, above_average=False):
    words_counts = most_common_words(filepath, num).most_common()
    words = iter(word for word, count in words_counts)
    prompt = "Ignore word : {0} ? (y/n  Default no)\n"
    ignore = ignore or []
    i = 0
    for word in words:
        if word in ignore:
            continue
        if above_average and len(word) < above_average:
            continue
        yes_no = input(prompt.format(word))
        if yes_no.lower() == "y":
            ignore.append(word)
        if i >= num:
            break
        i += 1
    with open(ignore_filepath, "a") as file: 
        file.write(" ".join(ignore) + " ")
        

def get_words(filepath):
    """
    Get a list of words from a file

    Args:
        filepath (str): File to read words from

    Returns:
        str[] : List of words from the input file. None if no file found.
    """
    try:
        with open(filepath, "r") as file:
            return file.read().split()
    except IOError:
        return None


def get_args():
    """
    This function parses and return arguments passed in
    """
    # Assign description to the help doc
    parser = argparse.ArgumentParser(
        description=__doc__)
    # File(s) to get data for.
    parser.add_argument('files', nargs='+', default="file.txt")
    # Optionally ignore a list of specific words.
    parser.add_argument('-i', '--ignore', type=str, help='Ignore list file name', required=False)
    parser.add_argument('-l', '--learn', type=int, help='Lean to ignore specific words', required=False, default=False)
    parser.add_argument('-n', '--show-numbers', action="store_true", help='Show number of word occurances', required=False, default=False)
    parser.add_argument('-a', '--above-average', action="store_true", help='Only find words that are above the average word lenth', required=False, default=False)
    parser.add_argument('-H', '--html', action="store_true", help='Generate html', required=False, default=False)
    # Array for all arguments passed to script
    args = parser.parse_args()
    # Assign args to variables
    files = args.files
    ignore = args.ignore
    learn = args.learn
    above_average = args.above_average
    show_numbers = args.show_numbers
    generate_html = args.html
    # Return all variable values
    return files, ignore, learn, show_numbers, above_average, generate_html


def generate_html_header(name):
    """
    Generate H1 name from filename

    Args:
        name (str): filename to generate name from

    Returns:
        str : Formatted name
    """
    name = name.split("/")[-1]
    return "<h1>{0}</h1>".format(name).replace(".txt", "").replace("_", " ").upper()


def generate_html(results):
    """
    Turn results of a text into a html output

    Args:
        results (str): program results

    Returns:
        str : html formatted output
    """

    config = {}
    with open("config.json", 'r') as file:
        config = json.load(file)

    results = [line.split() for line in results.splitlines()[:config["words"]]]

    max_count = float(results[0][1])

    output = ""

    output += "<h2>"
    for site, search in config["sites"].items():
        prefix = search["prefix"]
        postfix = search["postfix"]
        seperator = search["seperator"]
        max_words = search["max_words"]

        keywords = seperator.join([w for w, c in results][:max_words])
        query = "{0}{1}{2}".format(prefix, keywords, postfix)
        output += "<a href='{0}'>{1}</a>\n".format(query, site)
    output += "</h2>"

    for word, count in results:
        size = float(count) / max_count * 4 + 0.8
        output += "<p style='font-size:{0}em;display:inline-block;line-height:1.8em;margin:0;'>| {1} </p>\n".format(size, word, count)
    
    output += "<hr>"
    return output


def process_text(
        filepaths,
        ignore_filepath=False,
        learn=False,
        show_numbers=False,
        above_average=False
    ):
    """
    Get the most frequent words in a text.

    Args:
        filepaths (str[]): list of filepaths to process
        ignore_filepath (str): optional file containing list of words to ignore
        learn (bool): If True generate a list of words to ignore (default false)
        show_numbers (bool): If True number of word occurance will be output (default False)
        above_average (bool): if True only words above average length will be output (default False)

    Returns:
        (str) Most frequent words in text(s), or None in learn mode.
    """
    ignore = get_words(ignore_filepath) if ignore_filepath else []

    output=""

    if isinstance(filepaths, str):
        filepaths = [filepaths]

    for filepath in filepaths:
        if learn:
            # Learn words to ignore.
            learn_ignore(filepath, "ignore.txt", learn, ignore, above_average)
        else:
            # Output most common words
            words_counts = most_common_words(filepath)
            if above_average:
                words = [w for w, c in words_counts.most_common()]
                average_length = average_word_length(words)
            for word, count in words_counts.most_common():
                if word in ignore:
                    continue
                elif above_average and len(word) < average_length:
                    continue
                elif show_numbers:
                    output += "".join((word, " ", str(count), "\n"))
                else:
                    output += "".join((word, "\n"))
    return output


def main():
    """
    Main entry point for June tales
    """
    args = get_args()
    filepaths = args[0]
    ignore_filepath = args[1]
    learn = args[2]
    show_numbers = args[3]
    above_average = args[4]
    html = args[5]
    
    if not html:
        output = process_text(
            filepaths,
            ignore_filepath,
            learn,
            show_numbers,
            above_average
        )
        print(output)
    else:
        for text in filepaths:
           output = ""
           output += generate_html_header(text)
           result = process_text(
               text,
               show_numbers=True,
               above_average=above_average
           )
           output += generate_html(result)
           print(output)


if __name__ == "__main__":
    main()



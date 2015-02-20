#!/usr/bin/env python

#
# A Bot to download bollywood songs from the internet
# @author Kiran Gangadharan
#
import requests
import sys
import os
import signal
from BeautifulSoup import BeautifulSoup
from progressbar import *

def handle_quit(signum, stack):
    print '\nExiting...'
    sys.exit(0)

signal.signal(signal.SIGINT, handle_quit)

def movie_finder(base_url, movie_name):
    found = False
    movie_list_url = ''.join([base_url, movie_name[0].lower(), "_list.html"])
    print 'Checking...'
    response = requests.get(movie_list_url)
    parser = BeautifulSoup(response.content)
    links = parser.findAll('a')
    possible_matches = []
    for link in links:
        movie = link.text.replace("\n", "").replace("\t", "").replace("&nbsp;", "")
        movie_short_name = movie.split('-')[0].strip()
        if movie_name.lower() in movie_short_name.lower():
            possible_matches.append(link)
            found = True
    return found, possible_matches


def songs_finder(base_url, movie):
    print 'Querying movie page for songs...'
    link_attrs = movie.get('href')
    songs_url = ''.join([base_url, link_attrs])
    res = requests.get(songs_url)
    sparser = BeautifulSoup(res.content)
    songs = sparser.findAll('a')
    for link in songs[:]:
        if 'songid' not in unicode(link.get('href')):
            songs.remove(link)
    return songs


def download_song(song, dir_path):
    print "Downloading {0}.mp3 Please wait...".format(song.text)
    try:
        file_path = os.path.join(dir_path, (song.text + '.mp3'))
        file = open(file_path, 'wb')
    except Exception, e:
        print "Error occured:", e
        sys.exit(1)
    res = requests.get(song.get('href'))
    size = float(res.headers['content-length'])
    mbSize = 1024 * 1024    #used for conversion to Mb
    TotalSize = (size)/mbSize

    from urllib import quote

    actual_url = quote(res.url, safe="%/:.")
    res = requests.get(actual_url, stream=True)

    widgets = ['Test: ', Percentage(), ' ', Bar(">"), ' ', ETA(), ' ', FileTransferSpeed()]
    progress = ProgressBar(widgets=widgets,maxval=TotalSize)
    progress.start()

    count = 0
    for block in res.iter_content(1024):
        if not block:
            break
        file.write(block)
        count += 1024
        progress.update(count/mbSize)
    file.close()
    progress.finish()
    print 'Downloaded {0}'.format(song.text)


def main():
    print "=" * 50
    print "Song Bot"
    print "=" * 50
    movie_name = raw_input("Movie Name: ")
    base_url = 'http://www.songspk.name/'
    found = False

    if not movie_name:
        print "Movie name cannot be empty"
        sys.exit(1)

    found, possible_matches = movie_finder(base_url, movie_name.lower())
    if found:
        print 'Movie found'
        #Let user select a movie in case of multiple matches
        if len(possible_matches) > 1:
            print 'We have found multiple matches...'
            for num, single_match in enumerate(possible_matches):
                print num + 1, single_match.text.replace("\n", "").replace("\t", "").replace("&nbsp;", "")
            try:
                choice = int(raw_input("Enter which movie you want to proceed with: ")) - 1
                movie = possible_matches[choice]
            except (ValueError, IndexError):
                print 'Invalid input. Exiting...'
                sys.exit(1)
        else:
            movie = possible_matches[0]
        #Getting songs page for selected movie
        songs = songs_finder(base_url, movie)
        #Showing song list and asking user to select a song to download
        print 'Following songs found...'
        for num, song in enumerate(songs):
            print num + 1, song.text

        try:
            track_no = int(raw_input("Enter the song number you want to download(0 to download all): "))

            resp = raw_input("Do you want to create folder '%s'?(y)" %movie.text) 
            if resp.strip().lower() in ('y', 'yes'):
                dir_path  = os.path.join(os.getcwd(), movie.text) 
                if os.path.isdir(dir_path):
                    print "Directory '%s' already exist. Skipping..."%(dir_path)
                else:
                    os.mkdir(dir_path)
            else:
                dir_path = os.getcwd()
            if track_no == 0:
                for song in songs:
                    #call downloader function
                    download_song(song, dir_path)
            else:
                download_song(songs[track_no - 1], dir_path)
            print 'Download complete'

        except (ValueError, IndexError):
            print 'Invalid input. Exiting...'
            sys.exit(1)
    else:
        print "Movie not found"


if __name__ == '__main__':
    main()

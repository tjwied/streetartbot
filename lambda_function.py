#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-

#system imports
import json
#import boto3
#from botocore.exceptions import ClientError
import tempfile
import os
import subprocess
from six.moves.html_parser import HTMLParser
import random
from collections import defaultdict
from twython import Twython, TwythonError
import html

h = HTMLParser()
try:
    # load json metadata from S3 bucket into JSON
    # data = s3.get_object(Bucket=bucket_name, Key=key)
    with open('/home/pi/Desktop/art/metadata/art_metadata.json') as f: 
        json_data = json.loads(f.read())
except Exception as e:
    print(e)
    raise e

print("Got keys")

indexed_json = defaultdict()

for value in json_data:
    artist = value['artistName']
    title = value['title']
    title = html.unescape(title)
    title = html.unescape(title)
    year = value['year']
    values = [artist, title, year]

    # return only image name at end of URL
    find_index = value['image'].rfind('/')
    img_suffix = value['image'][find_index + 1:]
    img_link = img_suffix

    try:
        indexed_json[img_link].append(values)
    except KeyError:
        indexed_json[img_link] = (values)

# Shuffle images
single_image_metadata = random.choice(list(indexed_json.items()))

url = single_image_metadata[0]
painter = single_image_metadata[1][0]
title= single_image_metadata[1][1]
year = single_image_metadata[1][2]

#print(url, painter, title,year)

# Connect to Twitter via Twython

CONSUMER_KEY = '' 
CONSUMER_SECRET = ''
ACCESS_KEY = '' 
ACCESS_SECRET = ''

try:
    twitter = Twython(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET)
    #print(twitter)
except TwythonError as e:
    print(e)

#Try tweeting
try:

    tmp_dir = '/home/pi/Desktop/art/pics/'
    # subprocess.call('rm -rf /tmp/*', shell=True)
    path = os.path.join(tmp_dir, url)
    #print(path)

    # Try to match URL in filepath to URL in metadata; if it doesn't work, try another one
    for i in range(0, 3):
            try:
                #print("file moved to /tmp")
                print(os.listdir(tmp_dir))

                with open(path, 'rb') as img:
                    #print("Path", path)
                    twit_resp = twitter.upload_media(media=img)
                    twitter.update_status(status="\"%s\"\n%s, %s" % (title, painter, year),
                                          media_ids=twit_resp['media_id'])
            except ClientError as e:
                if e.response['Error']['Code'] == 'ResourceNotFoundException':
                    continue
            break


except TwythonError as e:
    print(e)




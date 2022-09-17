import os
import json
from dotenv import load_dotenv
import googleapiclient.discovery

load_dotenv()

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

api_service_name = "youtube"
api_version = "v3"
DEVELOPER_KEY = os.getenv('YOUTUBE_API_KEY')

YOUTUBE = googleapiclient.discovery.build(
    api_service_name, api_version, developerKey = DEVELOPER_KEY)

MAX_COMMENT_RESULTS = 100
MAX_VIDEOS_RESULTS = 50

def reqPlaylistVideos(playlistId):
    request = YOUTUBE.playlistItems().list(
        part="contentDetails",
        maxResults=MAX_VIDEOS_RESULTS,
        playlistId=playlistId
    )

    response = request.execute()
    
    videos = []
    for item in response['items']:
        videoId = item['contentDetails']['videoId']
        videos.append(videoId)
    
    return videos



def reqCommentThreads(videoId, pageToken=None):
    request = YOUTUBE.commentThreads().list(
        part="snippet,replies",
        maxResults=MAX_COMMENT_RESULTS,
        textFormat="plainText",
        videoId=videoId, 
        pageToken = pageToken,
    )

    response = request.execute()
    return response

def filterJSON(response):
    items = response['items']

    comments_data = []
    for item in items:
        try:
            comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
            comment = comment.replace('\n', ' ')
            comments_data.append(comment)

            if 'replies' in item:
               comment_replies= item['replies']['comments']
               for reply in comment_replies:
                    comment_reply = reply['snippet']['textDisplay']
                    comment_reply = comment_reply.replace('\n', ' ')
                    comments_data.append(comment_reply)
        except KeyError:
            print('textDisplay Key not Found!!')

    return comments_data

def main():

    choice = int(input('''Wanna give videoID(0) or playlistID(1) ?\nChoose either (0 or 1): '''))
    
    contentType = input('Enter type of content: ')

    Id = None
    rawResponse = []
    finalData = []

    if choice:
        Id = input('Enter playListID: ')
        videoIds = reqPlaylistVideos(Id)
        for vID in videoIds:
            try:
                response = reqCommentThreads(vID)
                rawResponse.append(response)
                data = filterJSON(response)
                finalData.extend(data)
            except:
                pass
    else:
        Id = input('Enter videoID: ')
        response = reqCommentThreads(Id)
        rawResponse.append(response)
        data = filterJSON(response)
        finalData.extend(data)

    try:
        totalPages = response['pageInfo']['totalResults']
        for _ in range(totalPages):
            
            if 'nextPageToken' not in response:
                break

            nextPageToken = response['nextPageToken']
            try:
                response = reqCommentThreads(Id, nextPageToken)
                rawResponse.append(response)
                data = filterJSON(response)
                finalData.extend(data)
            except:
                pass

    except KeyError:
        print('totalResults Key not Found!!')

    """ with open(contentType + '_' +  Id + '.json', 'w', encoding='utf-8') as outfile:
        json.dump(rawResponse, outfile) """

    with open(contentType + '_' +  Id + '.txt', 'w', encoding='utf-8') as outfile:
        for line in finalData:
            outfile.write("%s\n" % line)

if __name__ == "__main__":
    main()

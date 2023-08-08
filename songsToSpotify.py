import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
import spotipy
import pprint
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()
os.system("cls")

date = input("Which year do you want to travel to? Type the date in this format YYYY-MM-DD: ")

URL = "https://www.billboard.com/charts/hot-100/"+date
response = requests.get(URL)

webPage = response.text
soup = BeautifulSoup(webPage,"html.parser")


songDiv = soup.find_all(name="div",class_="o-chart-results-list-row-container");
    
songName=[]
for i in range(0,len(songDiv)):
    songName.append(songDiv[i].find(name="h3",class_="c-title").getText().replace('\t','').replace('\n',''))

songArtist=[]
for i in range(0,len(songDiv)):
    
    songArt = songDiv[i].find(name="span",class_="lrv-u-display-block").getText().replace('\t','').replace('\n','')
    
    songArtList = [songArt]
    
    
    if(songArt.find(" Featuring ")!=-1):
        songArtList=songArt.split(" Featuring ")
        songArtist.append(songArtList)
    elif(songArt.find(" With ")!=-1):
        songArtList=songArt.split(" With ")
        songArtist.append(songArtList)
    # elif(songArt.find(" & ")!=-1):
    #     songArtList=songArt.split(" & ")
    #     songArtist.append(songArtList)
    else:
        songArtist.append(songArtList)


sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=os.getenv("CLIENT_ID"),
                                               client_secret=os.getenv("CLIENT_SECRET"),
                                               redirect_uri="http://example.com",
                                               scope="playlist-modify-private",
                                               show_dialog=True,
                                               cache_path="token.txt",
                                               username=os.getenv("USER_ID")))

user_id = sp.current_user()["id"]

songURIs = []
count=0
count_avail=0
for i in range(0,len(songName)):
    countArtist=len(songArtist[i])
    artistFound=0
    
    for j in range(0,len(songArtist[i])):
        if(countArtist!=0):
            
                
            result = sp.search(q=f"{songName[i]} {songArtist[i][j]}",type='track',limit=1)
            
            countArtist=countArtist-1
            
            
            if(songArtist[i][j].find("&")!=-1):
                
                try:
                    if artistFound==0:
                        songN=result["tracks"]["items"][0]["uri"]
                        songURIs.append(songN)
                        artistFound=1
                except IndexError:
                    songArtist[i]=songArtist[i][j].split(" & ")
                    
                    count_and_art=len(songArtist[i])
                    
                    for k in range (0,len(songArtist[i])):
                        if artistFound==0:
                            result = sp.search(q=f"{songName[i]} {songArtist[i][k]}",type='track',limit=1)
                            try:
                                count_and_art=count_and_art-1
                                songN=result["tracks"]["items"][0]["uri"]
                                songURIs.append(songN)
                                artistFound=1
                            except IndexError:
                                if count_and_art==0:
                                    artistFound=0
                                else:
                                    continue         
            else:
                try:
                    if artistFound==0:
                        songURIs.append(result["tracks"]["items"][0]["uri"])
                        count_avail=count_avail+1
                        artistFound=1
                except IndexError:
                    artistFound=0
                    continue
                
    if artistFound==0:
        count=count+1
        print(f"{count}. {songName[i]} by {songArtist[i]} | doesn't exist in Spotify. Skipped.")
        
    artistFound==0

playlist = sp.user_playlist_create(user=os.getenv("USER_ID"),name=f"{date} Billboard 100",public=False)

sp.playlist_add_items(playlist_id=playlist["id"],items=songURIs)
print("Playlist Added...")
from pytube import YouTube
import os
import requests

# Create a function to download the scrapped data.
def download_scrapped_data(scrapped_data_queue, search_query, scrapped_videos_count, scrapped_channels_count, downloaded_data):
    '''
    This function downloads the scrapped content and stores it into the disk.
    Args:
        scrapped_data_queue:     It is a queue that contains the URLs of the videos, thumbnails, and channels profile pictures, etc.
        search_query:            The (searched query text) name of the person whose videos need to be downloaded.
        scrapped_videos_count:   The total number of videos scrapped (or being scrapped) from the web. 
        scrapped_channels_count: The total number of channels from the web, from which we have scrapped (or being scrapped) content.
        downloaded_data:         It is a queue to store the paths of downloaded video, thumbnails, and channel profile pictures, etc.
    '''
    
    # Check if the output directory does not exist. 
    if not os.path.exists(search_query):
        
        # Create the output directory.
        os.mkdir(search_query)
    
    # Change the current working directory to the output directory.
    os.chdir(search_query)
    
    # Initalize a variable to store the downloaded videos count.
    download__videos_data_count=0
    
    # Initalize a variable to store the downloaded channel's content count.
    download__channels_data_count=0
    
    # Iterate until all the videos and channels content are not downloaded.
    while download__videos_data_count<scrapped_videos_count or download__channels_data_count<scrapped_channels_count:
        
        # Check if the queue contains any element(s).
        if not scrapped_data_queue.empty():
            
            # Get an element from the queue.
            data = scrapped_data_queue.get()
            
            # Check if the element (dictionary) contains a 'Video Info' key.
            if 'Video Info' in data:
                
                # Get the video information.
                video_data = data['Video Info']
                
                # Download the video.
                video_path = download_video(video_data['Video URL'])
                                                
                # Download the thumbnail.
                thumbnail_path = download_image(video_data['Thumbnail URL'], f"{os.path.split(video_path)[-1].split('.')[0]}-thumbnail", image_dir='thumbnails')
                
                # Store the downloaded video path and thumbnail path into the downloaded_data queue.
                downloaded_data.put({'Video Info': {'Video URL': video_data['Video URL'], 'Video Path': video_path, 'Thumbnail Path': os.path.join(search_query, thumbnail_path)}})
                
                # Increment the downloaded videos counter.
                download__videos_data_count+=1
            
            # Check if the element (dic) contains a 'Channel Info' key.
            if 'Channel Info' in data:
                
                # Get the channel data.
                channel_data = data['Channel Info']
                
                # Initialize a list to store the videos thumbnails_paths path.
                thumbnails_paths = []
                
                # Initialize a list to store the videos path.
                videos_paths = []
                
                # Specify the channel name placeholder, we are iterating upon.
                channel_name = f'Channel-{download__channels_data_count}'
                
                # Get the videos urls of the channel.
                videos_urls = channel_data['Videos URLs']
                
                 # Iterate over the videos thumbnails urls of the channel.
                for index, thumbnail_url in enumerate(channel_data['Thumbnails URLs']):
                                        
                    # Download the video, we are iterating upon and store it's path into the list.
                    thumbnails_paths.append(download_image(thumbnail_url, f"video-{index}-thumbnail", image_dir=f'{channel_name}-data'))
                
                # Iterate over the videos urls of the channel.
                for video_url in videos_urls:
                    
                    # Download the video, we are iterating upon and store it's path into the list.
                    videos_paths.append(download_video(video_url, video_dir=f'{channel_name}-data'))
                
                # Download the profile picture of the channel.    
                profile_pic_path = download_image(channel_data['Channel Profile Picture'], image_name=f'{channel_name}-profile-picture', image_dir=f'{channel_name}-data')
                
                # Store the downloaded channel url, videos paths and profile picture path into the downloaded_data queue.
                downloaded_data.put({'Channel Info': {'Channel URL': channel_data['Channel URL'], 
                                                      'Profile Picture Path': os.path.join(search_query, profile_pic_path),
                                                      'Videos Paths': videos_paths, 
                                                      'Thumbnails Paths': thumbnails_paths, 
                                                      }})
                
                # Increment the downloaded channel's content counter.
                download__channels_data_count+=1
            
    # Change the current working directory back to the orginal working directory.
    os.chdir('..')
    
# Create a helper function to download a video.   
def download_video(video_url, video_dir='videos'):
    video_path = None
    if not os.path.exists(video_dir):
        os.mkdir(video_dir)
    os.chdir(video_dir)
    youtubeObject = YouTube(video_url)
    youtubeObject = youtubeObject.streams.get_highest_resolution()
    try:
        video_path = youtubeObject.download()
        print(f"{video_url} is downloaded successfully")
    except:
        print(f"An error has occurred to download {video_url}.")
    os.chdir('..')
    return video_path

# Create a helper function to download an image. 
def download_image(image_url, image_name, image_dir):
    if not os.path.exists(image_dir):
        os.mkdir(image_dir)
    image_path = f'{os.path.join(image_dir, image_name)}.jpg'
    image_data = requests.get(image_url).content
    with open(image_path, 'wb') as handler:
        handler.write(image_data)
    return image_path
import requests
from pytube import Playlist
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from helper_modules.YoutubeScraper.helper import is_section_available, calculate_playlists_videos, scroll_in_section



def extract_playlist_section(wait, driver, n_result, screen_height):
    '''
        This function will extract the Videos urls and thumbnails from the VIDEOS, LIVE and SHORTS section.

        Arguments:
            driver:                 Chrome web driver object will help to scrape the results.
            wait:                   Web driver wait instance to perform explicit waiting.
            n_result:               Number of videos which will be extracted.
            screen_height:          Screen height of the window will be used for scrolling.

        Returns:
            videos:                 List of Channel Videos urls.
            thumbnail_urls:         List of Channel Videos thumbnails.
    '''

    # Initialize empty list to store the videos in the playlists.
    videos = []

    # Initialize empty list to store the thumbnails of the playlist videos.
    thumbnail_urls = []

    # Check if playlist section has content or not.
    has_playlist_section, playlist_section_no = is_section_available(
        wait, driver, "Playlists")

    if has_playlist_section:

        # Find channel videos button and click on it.
        wait.until(EC.element_to_be_clickable(
            (By.XPATH, '//*[@id="tabsContent"]/tp-yt-paper-tab['+str(playlist_section_no)+']')))
        playlist_section = driver.find_element(By.XPATH,
                                               '//*[@id="tabsContent"]/tp-yt-paper-tab['+str(playlist_section_no)+']')
        playlist_section.click()

        # Check if there is no playlist in the channel.
        no_playlist = False
        try:
            driver.implicitly_wait(3)
            driver.find_element(
                By.XPATH, '//*[@id="contents"]/ytd-message-renderer')
            no_playlist = True
        except:
            no_playlist = False

        # Check if channel contains any playlist.
        if no_playlist == False:
            
            # Find the playlist section name.
            wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="label-text"]')))
            label_text = driver.find_element(By.XPATH, '//*[@id="label-text"]')

            # Initialize the playlist videos and continuation element xpath.
            if label_text.text == "Created playlists":

                # Initialize playlist elements and continuation element xpath.
                channel_playlist_xpath = '//ytd-item-section-renderer//ytd-grid-playlist-renderer'
                continuation_playlist_element_xpath = '//ytd-section-list-renderer//ytd-item-section-renderer//ytd-grid-renderer//ytd-continuation-item-renderer'
                
                # Find playlists in the channel.
                wait.until(EC.presence_of_all_elements_located((By.XPATH, channel_playlist_xpath)))
                playlists = driver.find_elements(By.XPATH, channel_playlist_xpath)
                
                # Calculate the total videos of the playlists.
                total_playlists_videos = calculate_playlists_videos(playlists)

                # Scroll down, if more videos required.
                playlists = scroll_in_section(
                    wait, driver, total_playlists_videos, n_result, screen_height, channel_playlist_xpath, continuation_playlist_element_xpath, playlists, True)

            else:
                # Initialize playlist elements and continuation element xpath.
                channel_playlist_xpath = '//ytd-item-section-renderer[1]//ytd-shelf-renderer//ytd-grid-playlist-renderer'

            # Find playlists in the channel.
            wait.until(EC.presence_of_all_elements_located((By.XPATH, channel_playlist_xpath)))
            playlists = driver.find_elements(By.XPATH, channel_playlist_xpath)
            
            # Find the videos urls of the playlists by using the pytube Playlist object.
            for playlist in playlists:

                driver.execute_script(
                    "arguments[0].scrollIntoView();", playlist)

                # Locate to the playlist video title element to find the playlist url.
                playlist_title = playlist.find_element(By.ID, 'video-title')

                # Find the videos urls in the playlist using pytube.
                playlist_info = Playlist(playlist_title.get_attribute("href"))
                playlist_videos_urls = playlist_info.video_urls

                # Store the found videos urls.
                for url in playlist_videos_urls:
                    
                    # Extract the video id from the video url.
                    video_id = url.split('=')[1]

                    # Set up the video thumbnail using the video id.
                    thumbnail_url = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"

                    # Check if the thumbnail url is available.
                    response = requests.get(thumbnail_url)
                    if response.status_code == 404:
                        thumbnail_url = f"https://img.youtube.com/vi/{video_id}/0.jpg"
                    
                    # Store the thumbnail url in the list.
                    thumbnail_urls.append(thumbnail_url)

                    # Store the video url in the list.
                    videos.append(url)

                # if required videos found, then break.
                if len(videos) >= n_result:
                    videos = videos[:n_result]
                    thumbnail_urls = thumbnail_urls[:n_result]
                    break

    return videos, thumbnail_urls

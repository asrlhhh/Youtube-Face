from helper_modules.YoutubeScraper.playlist_tab import extract_playlist_section
from helper_modules.YoutubeScraper.channel_tab import extract_section


def extract_channel_videos(wait, driver, n_channel_videos_url, screen_height):
    '''
        This function will extract the Channel Videos urls and their thumbnails from the VIDEOS,
        PLAYLISTS, LIVE and SHORTS sections.

        Arguments:
            driver:                 Chrome web driver object will help to scrape the results.
            wait:                   Web driver wait instance to perform explicit waiting.
            n_channel_videos_url:   Top n number of channel videos, which will be extracted.
            screen_height:          Screen height of the window will be used for scrolling.

        Returns:
            videos:                 List of Channel Videos urls.
            thumbnail_urls:         List of Channel Videos thumbnails.
    '''

    # Extract the channel videos from the videos section.
    videos, thumbnail_urls = extract_section(wait, driver, "Videos", n_channel_videos_url, screen_height, 'thumbnail')
    
    # Wait for the page load.
    driver.implicitly_wait(3)

    if len(videos) < n_channel_videos_url:

        # Extract videos from playlist, if required videos are not available in the videos section.
        rem_videos, rem_thumbnail_urls = extract_playlist_section(
            wait, driver, n_channel_videos_url - len(videos), screen_height)
        
        # Concatenate the videos urls extracted from the playlists section.
        videos += rem_videos

        # Concatenate the thumbnails.
        thumbnail_urls += rem_thumbnail_urls

        # Initialize list to store the section names which contain channel videos.
        sections = ["Shorts", "Live"]

        # Extract the channel videos from the sections in the list, if required.
        for section in sections:
            if len(videos) < n_channel_videos_url:

                # Wait for page laod.
                driver.implicitly_wait(3)

                rem_videos, rem_thumbnail_urls = extract_section(wait, driver, section, n_channel_videos_url - len(videos), screen_height, 'thumbnail')
        
                # Concatenate the videos urls extracted from the playlists section.
                videos += rem_videos

                # Concatenate the thumbnails.
                thumbnail_urls += rem_thumbnail_urls

    return videos, thumbnail_urls

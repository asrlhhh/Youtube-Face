from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException
from helper_modules.YoutubeScraper.helper import is_section_available, scroll_in_section

def extract_section(wait, driver, section_name, n_result, screen_height, video_thumbnail_element):
    '''
        This function will extract the Videos urls and thumbnails from the VIDEOS, LIVE and SHORTS section.

        Arguments:
            driver:                 Chrome web driver object will help to scrape the results.
            wait:                   Web driver wait instance to perform explicit waiting.
            section_name:           Name of the section from the videos will be extracted.
            n_result:               Number of videos which will be extracted.
            screen_height:          Screen height of the window will be used for scrolling.
            video_thumbnail_element: Web element ID from which the video url will be extracted.

        Returns:
            videos:                 List of Channel Videos urls.
            thumbnail_urls:         List of Channel Videos thumbnails.
    '''
    # Initialize empty list to store the videos of the current channel.
    videos = []

    #Initialize empty list to store the thumbnails of the videos.
    thumbnail_urls = []

    # Check if Videos section has content or not.
    has_section, section_no = is_section_available(
        wait, driver, section_name)

    if has_section:

        # Find the video button and click.
        wait.until(EC.element_to_be_clickable(
            (By.XPATH, '//*[@id="tabsContent"]/tp-yt-paper-tab['+str(section_no)+']')))
        section = driver.find_element(By.XPATH,
                                                '//*[@id="tabsContent"]/tp-yt-paper-tab['+str(section_no)+']')
        section.click()

        # Check if there is no videos in the VIDEOS section.
        no_videos = False
        try:
            driver.implicitly_wait(2)
            driver.find_element(
                By.XPATH, '//*[@id="contents"]/ytd-message-renderer')
            no_videos = True
        except:
            no_videos = False

        # Extract videos if available.
        if no_videos == False:
        
            # Initialize video elements and continuation element xpath.
            if section_name == "Videos" or section_name == "Live":

                videos_xpath = '//ytd-rich-item-renderer//ytd-rich-grid-media'
                continuation_element_xpath = '//*[@id="contents"]/ytd-continuation-item-renderer'

            elif section_name == "Shorts":

                videos_xpath = '//ytd-rich-item-renderer//ytd-rich-grid-slim-media'
                continuation_element_xpath = '//*[@id="contents"]/ytd-continuation-item-renderer'

            else:
                videos_xpath = ""
                continuation_element_xpath = ""
                
            # Extract the channel videos elements.
            wait.until(EC.presence_of_all_elements_located(
                (By.XPATH, videos_xpath)))
            channel_videos = driver.find_elements(
                By.XPATH, videos_xpath)

            # Scroll down in the Videos section to load more videos, if required.
            channel_videos = scroll_in_section(
                wait, driver, len(
                    channel_videos), n_result, screen_height, videos_xpath, continuation_element_xpath, channel_videos
            )

            # Extract channel videos urls from channel videos Web elements.
            for video in channel_videos:
                try:
                    driver.execute_script(
                        "arguments[0].scrollIntoView();", video)

                    # Extract video url.
                    wait.until(EC.presence_of_element_located(
                        (By.ID, video_thumbnail_element)))
                    channel_video_url = video.find_element(By.ID, video_thumbnail_element)

                    # Extract the video thumbnail.
                    thumbnail_url = video.find_element(By.TAG_NAME, 'img')

                    # Store the thumbnails.
                    thumbnail_urls.append(thumbnail_url.get_attribute("src"))

                    # Store urls.
                    videos.append(channel_video_url.get_attribute('href'))

                    if len(videos) >= n_result:
                        videos = videos[:n_result]
                        thumbnail_urls = thumbnail_urls[:n_result]
                        break

                except StaleElementReferenceException as st:
                    pass

    return videos, thumbnail_urls
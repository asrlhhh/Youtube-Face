from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from helper_modules.YoutubeScraper.channel_videos import extract_channel_videos
from helper_modules.YoutubeScraper.helper import sort_search_results


def scrap_channels(extracted_data, driver, wait, n_channel_results, n_channel_videos_url, sort_videos):
    '''
        This function will scrape the youtube search results i.e.
         Channel URLS, Channel Videos, Channel Videos thumbnails and Channel Profile Pictures.

        Arguments:
            extracted_data:         The queue to store the output extrated URLs.
            driver:                 Chrome web driver object will help to scrape the results.
            wait:                   Web driver wait instance to perform explicit waiting.
            n_channel_results:      Top n number of channel results which will be extracted.
            n_channel_videos_url:   Top n number of channel videos, which will be extracted.
            sort_videos     :       Sort option, which will sort the search results.
    '''
    
    # Sort the channel search results on the basis of videos sort option.
    if sort_videos == "relevance":
        sort_search_results(wait, driver, ["Video", "Channel"])
    else:
        sort_search_results(wait, driver, ["Video", "Relevance", "Channel"])   

    # Check if results exists for the given search text by using the No result web element.
    no_results = False
    try:
        driver.find_element(
            By.XPATH, '//*[@id="contents"]/ytd-background-promo-renderer/yt-icon')
        no_results = True
    except:
        no_results = False
    
    # Search channels if channel results exist.
    if no_results == False:

        # Return the window screen height.
        screen_height = driver.execute_script("return window.screen.height;")

        # Set the scroll down size initial value.
        scroll_size = 1

        # Extract search results Channel elements list by using tag name.
        wait.until(EC.presence_of_all_elements_located(
            (By.TAG_NAME, 'ytd-channel-renderer')))
        channels = driver.find_elements(By.TAG_NAME, 'ytd-channel-renderer')

        # Iterate until desired number of channels loaded into the DOM.
        while len(channels) < n_channel_results:

            # Check for the 'No results' element.
            end = driver.find_element(By.ID, 'message').is_displayed()

            # Scroll down search results to access maximum results in the DOM.
            driver.execute_script(
                f"window.scrollTo(0, {screen_height}*{scroll_size});")

            # wait for the channels to load.
            wait.until(EC.presence_of_all_elements_located(
                (By.TAG_NAME, 'ytd-channel-renderer')))
            channels = driver.find_elements(By.TAG_NAME, 'ytd-channel-renderer')

            # Stop the scroll down by breaking a loop, if no result available.
            if end == True:
                break

            # Increment the scroll size.
            scroll_size += 1

        # Initialize to count the number of extracted results.
        channel_count = 0

        # Initialize a flag to check the availability of all required top n results.
        is_all_results_available = False

        # Initialize empty list to store the channels urls.
        channels_urls = []

        # Extract the search channels urls.
        for channel in channels:

            # Move to current channel.
            driver.execute_script("arguments[0].scrollIntoView();", channel)

            # Extract channel url.
            wait.until(EC.presence_of_element_located((By.ID, 'main-link')))
            channel_url = channel.find_element(By.ID, 'main-link')

            channels_urls.append(channel_url.get_attribute("href"))

        print("Extracting Channel Details ...")

        # Extract the Youtube channel search results.
        for channel in channels_urls:
            
            # Move to the channel page.
            driver.get(channel)

            # Wait until channel page loads.
            wait.until(EC.presence_of_element_located(
                (By.XPATH, '//*[@id="contentContainer"]')))

            # Extract the channel profile picture.
            wait.until(EC.presence_of_element_located(
                (By.XPATH, '//*[@id="channel-header-container"]/yt-img-shadow/img')))
            channel_profile = driver.find_element(By.XPATH, '//*[@id="channel-header-container"]/yt-img-shadow/img')
            profile_picture = channel_profile.get_attribute("src")

            # Check if there is no content in the channel.
            no_content = False
            try:
                driver.implicitly_wait(3)
                driver.find_element(By.XPATH, '//*[@id="contents"]/ytd-message-renderer')
                no_content = True
            except:
                no_content = False

            # Initialize empty list to store the channel videos.
            videos = []
            
            # Initialize empty list to store the videos thumbnails.
            thumbnails_urls = []

            # Check if channel contains any content.
            if no_content == False:
                
                # Extract channel Videos.
                videos, thumbnails_urls = extract_channel_videos(wait, driver, n_channel_videos_url, screen_height)
                        
            extracted_data.put({'Channel Info': {"Channel URL":channel,
                                                 "Channel Profile Picture": profile_picture,
                                                 "Videos URLs": videos,
                                                 "Thumbnails URLs": thumbnails_urls}})

            # Break if required number of results have been extracted.
            if n_channel_results-1 == channel_count:
                is_all_results_available = True
                break

            # Increment the counter.
            channel_count += 1

        # Check if required top n results are available or not.
        if is_all_results_available == False:
            print(channel_count, " Channel results available for this search text.")

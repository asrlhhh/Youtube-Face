from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException

# --------------------------------------------------------------------------------------------------#
def is_section_available(wait, driver, section_name):
    '''
        This function will check whether the given section name exists in the channel or not.

        Arguments:
            driver:                 Chrome web driver object will help to scrape the results.
            wait:                   Web driver wait instance to perform explicit waiting.
            section_name:           Name of the section which will be checked.

        Returns:
            has_section:            Returns bool value whether the section exists or not.
            found_section_no:       Returns the section number in the channel tabs.
    '''
    # Wait for the channel menus buttons to be present.
    wait.until(EC.presence_of_all_elements_located(
        (By.XPATH, '//*[@id="tabsContent"]/tp-yt-paper-tab')))
    sections = driver.find_elements(
        By.XPATH, '//*[@id="tabsContent"]/tp-yt-paper-tab')

    # Initially set section to False.
    has_section = False

    # Channel Section counter
    section_no = 1

    # Initialize to store the founded section number.
    found_section_no = 0

    # Check if there exists given category in the channel.
    for section in sections[:len(sections)-2]:
        try:
            # Find the section name tag.
            divEle = section.find_element(By.TAG_NAME, 'div')
            
            # Check if found section name matches with the given section name.
            if divEle.get_attribute("innerHTML").strip() == section_name:

                has_section = True
                found_section_no = section_no

        except StaleElementReferenceException as st:
            pass

        section_no += 1

    return has_section, found_section_no

# --------------------------------------------------------------------------------------------------#
def calculate_playlists_videos(playlists):
    '''
        This function will calculate the total Videos in the given list of playlists.

        Arguments:
            playlists:         List of playlists web elements.

        Returns:
            total_videos:      Returns the total videos in the given list of playlists. 
    '''
    # Initialize to store the total videos in all playlists of the channel.
    total_videos = 0

    # Calculating the videos in the playlists.
    for playlist in playlists:

        # Find the number of videos in the playlist.
        side_panel = playlist.find_element(
            By.TAG_NAME, 'ytd-thumbnail-overlay-side-panel-renderer')
        side_panel_value = side_panel.find_element(
            By.TAG_NAME, 'yt-formatted-string').text

        if side_panel_value != '':
            
            # Youtube playlist shows only top 200 videos, if it has more than 200 videos.
            # Check if it is greater than thousand or 200, then set it's value to 200.
            if (len(side_panel_value) > 1) and (side_panel_value[-1] == 'K' or int(side_panel_value) > 200):
                value = 200
            else:
                value = int(side_panel_value)
            total_videos += value

    return total_videos

# --------------------------------------------------------------------------------------------------#
def scroll_in_section(wait, driver, videos_len, n_videos, screen_height, xpath, noContentXpath, videosList, isPlaylist=False):
    '''
        This function will perform scrolling in the different sections, if required.

        Arguments:
            driver:               Chrome web driver object will help to scrape the results.
            wait:                 Web driver wait instance to perform explicit waiting.
            videos_len:           Length of the found videos.
            n_videos:             Length of the required videos.
            screen_height:        Screen height of the window will be used for scrolling.
            xpath:                Xpath of the channel videos web elements.
            noContentXpath:       Xpath of the channel videos continuation element to check whether more 
                                    videos available or not.
            videosList:           List of Channel videos web elements.
            isPlaylist:           Flag to check whether the section to be scrolled is playlist or not.

        Returns:
            videosList:           Returns the list of Section videos after scrolling.
    '''
    # Reset the scrollSize value.
    scrollSize = 1

    # Initialize to keep scroll and set it to False.
    keepScroll = False

    # Scroll down the videos of the channel, if required.
    while videos_len < n_videos:
        # Check if more videos available or not.
        try:
            isMore = driver.find_element(By.XPATH, noContentXpath)
            keepScroll = True
        except:
            keepScroll = False

        # Scroll down search results to access maximum results in the DOM.
        driver.execute_script(
            f"window.scrollTo(0, {screen_height * scrollSize});")

        # Wait for the elements to load a bit.
        driver.implicitly_wait(2)

        # Extract the channel videos elements.
        wait.until(EC.presence_of_all_elements_located((By.XPATH, xpath)))
        videosList = driver.find_elements(By.XPATH, xpath)

        # Update videos length after scrolling.
        videos_len = len(videosList)

        # Update found videos length by calculating from the thumbnails, if playlist.
        if isPlaylist:
            total_videos = calculate_playlists_videos(videosList)
            videos_len = total_videos

        if keepScroll == False:
            break
        scrollSize += 1

    return videosList

# --------------------------------------------------------------------------------------------------#
def sort_search_results(wait, driver, link_texts):
    '''
        This function will perform scrolling in the different sections, if required.

        Arguments:
            driver:               Chrome web driver object will help to interact with the web elements.
            wait:                 Web driver wait instance to perform explicit waiting.
            link_texts:           List of the filter panel options which needs to be clicked.
    '''
    for link_text in link_texts:
        
        # Wait until filter button is clickable
        wait.until(EC.element_to_be_clickable((By.XPATH,
                                                '//*[@id="container"]/ytd-toggle-button-renderer')))

        # Find filter button and click.
        sort_button = driver.find_element(By.XPATH,
                                            '//*[@id="container"]/ytd-toggle-button-renderer')
        sort_button.click()

        # Wait until link text is clickable.
        wait.until(EC.element_to_be_clickable((By.LINK_TEXT, link_text)))
            
        # Find the link text element and click.
        button = driver.find_element(By.LINK_TEXT, link_text)
        button.click()

        # Wait until search filter panel collapse.
        wait.until(EC.invisibility_of_element_located((By.ID, 'collapse-content')))

# --------------------------------------------------------------------------------------------------#
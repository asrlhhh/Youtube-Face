# Import Required libraries
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from helper_modules.YoutubeScraper.ytb_channels_scraper import scrap_channels
from helper_modules.YoutubeScraper.helper import sort_search_results


# ------------------------------------------------------------------------------------------------------#
def scrap_data(search_text, extracted_data, n_videos_results=10, sort_videos="relevance", n_channel_results=10, n_channel_videos_url=5):
    '''
        This function will scrape the youtube search Videos URLS, Thumbnails, 
        Channel URLS, Channel Videos, Channel Video thumbnails and Channel Profile Pictures.

        Arguments:
            search_text:            Text which will be searched on youtube to get the results.
            extracted_data:         The queue to store the output extrated URLs.
            n_videos_results:       Top n number of video results which will be extracted.
            sort_videos     :       Sort option, which will sort the search results.
            n_channel_results:      Top n number of channel results which will be extracted.
            n_channel_videos_url:   Top n number of channel videos, which will be extracted.
    '''

    # Set chrome service options and initialize the chrome web driver.
    options = webdriver.ChromeOptions()
    options.add_argument("disable-infobars")
    options.add_argument("--disable-extensions")
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    driver.maximize_window()

    # Load the youtube url in chrome browser.
    driver.get("https://www.youtube.com/")

    # Initialize web driver explicit wait instance.
    wait = WebDriverWait(driver, 30)

    try:
        # Wait until the search bar is not visible.
        wait.until(EC.visibility_of_element_located((By.NAME, "search_query")))

        # Find search bar and click it, pass search text parameter value in it.
        search_element = driver.find_element(By.NAME, "search_query")
        search_element.click()
        search_element.send_keys(search_text)

        # Get the current url of the page.
        current_url = driver.current_url

        # Wait until search button is clickable.
        wait.until(EC.element_to_be_clickable((By.ID, "search-icon-legacy")))

        # Find the search button icon and click it.
        search_icon = driver.find_element(By.ID, "search-icon-legacy")
        search_icon.click()

        # click until url of the page changes.
        while driver.current_url == current_url:
            search_icon.click()

        # Initialize sort options list on the basis of sort_videos parameter.
        if sort_videos == "relevance":

            link_texts = ["Video"]
            
        elif sort_videos == "upload-time":

            link_texts = ["Video", "Upload date"]
            
        elif sort_videos == "popularity":
            
            link_texts = ["Video", "View count"]
        else:
            print("Please Enter Valid Sort Option !!!")
            link_texts = []

        # Sort the search results of the given search text.
        sort_search_results(wait, driver, link_texts)

        # Check if results exists for the given search text by using the No result web element.
        no_results = False
        try:
            driver.find_element(
                By.XPATH, '//*[@id="contents"]/ytd-background-promo-renderer/yt-icon')
            no_results = True
        except:
            no_results = False

        if no_results == False:

            # Return the window screen height.
            screen_height = driver.execute_script("return window.screen.height;")

            # Set the scroll down multiplier.
            scroll_size = 1

            # Extract search results videos elements list by using tag name.
            wait.until(EC.presence_of_all_elements_located(
                (By.TAG_NAME, 'ytd-video-renderer')))
            videos = driver.find_elements(By.TAG_NAME, 'ytd-video-renderer')

            # Iterate until desired number of videos loaded into the DOM.
            while len(videos) < n_videos_results:

                # Check for the 'No results' element.
                end = driver.find_element(By.ID, 'message').is_displayed()

                # Scroll down search results to access maximum results in the DOM.
                driver.execute_script(
                    f"window.scrollTo(0, {screen_height}*{scroll_size});")

                # wait for the videos to load.
                wait.until(EC.presence_of_all_elements_located(
                    (By.TAG_NAME, 'ytd-video-renderer')))
                videos = driver.find_elements(By.TAG_NAME, 'ytd-video-renderer')

                # Stop the scroll down by breaking a loop, if no result available.
                if end == True:
                    break

                # Increment the scroll size.
                scroll_size += 1

            # Count the number of extracted results.
            count = 0

            # flag to check the availability of all required top n results.
            is_all_results_available = False

            print("Extracting Video Details from Search Results ...")

            # Extract the Youtube search results.
            for video in videos:
                try:
                    # Move to current video.
                    driver.execute_script("arguments[0].scrollIntoView();", video)

                    # Extract Video URL.
                    wait.until(EC.presence_of_element_located((By.ID, 'video-title')))
                    title = video.find_element(By.ID, 'video-title')

                    # Extract video thumbnail.
                    wait.until(EC.presence_of_element_located((By.TAG_NAME, 'img')))
                    thumbnail = video.find_element(By.TAG_NAME, 'img')

                    # # Store the results in output queue.            
                    extracted_data.put({'Video Info': {"Thumbnail URL": thumbnail.get_attribute('src'),
                                                       "Video URL": title.get_attribute('href')}})

                    # Break if required number of results have been extracted.
                    if n_videos_results-1 == count:
                        is_all_results_available = True
                        break

                    # Increment the counter.
                    count += 1

                except StaleElementReferenceException as st:
                    pass

            # Check if required top n results are available or not.
            if is_all_results_available == False:
                print(count, " videos results available for this search text.")

            # Scroll to the top page.
            driver.execute_script("window.scrollTo(0,-document.body.scrollTop)")
        
         # Extract detials like channels urls, channel profile images and their videos urls.
        scrap_channels(extracted_data, driver, wait, n_channel_results, n_channel_videos_url, sort_videos)

    # Handle Exception and return empty output list.
    except Exception as ex:
        print("Session Timedout. Check you Internet Connection or Try to re-run the function.")
        return [], []
    finally:
        # Close the browser and destory the web driver.
        driver.quit()
# ------------------------------------------------------------------------------------------------------#


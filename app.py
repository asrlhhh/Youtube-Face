import argparse
import multiprocessing
from helper_modules.YoutubeScraper.ytb_videos_scraper import scrap_data
from helper_modules.data_downloader import download_scrapped_data
from helper_modules.face_recognition import recogize_face
import os

if __name__ == '__main__':
    
    # Initialize the queues to store the scrapped data urls and downloaded data paths.
    scrapped_urls = multiprocessing.Queue()
    downloaded_data = multiprocessing.Queue()

    parser = argparse.ArgumentParser()
    parser.add_argument('--person_name', type=str, help='The name of the person whose videos need to be extracted.')
    parser.add_argument('--images_paths', type=str, action='append', default="images/XYZ", help='The paths of the images of the person (whose videos need to be extracted)')
    parser.add_argument('--scrap_videos_count', type=int, default=10, help='The total number of videos to scrap from the web.')
    parser.add_argument('--scrap_channels_count', type=int, default=10, help='The total number of channels from the web, from we want to scrap content.')
    parser.add_argument('--sort_videos_by', type=str, default='relevance', help='It specifies whether to sort the videos by "relevance", "upload-time" or "popularity" or  before scrapping.')
    parser.add_argument('--skip_duration_in_secs', type=float, default=0, help='The size of the skip duration in seconds after every frame during face verfication process on videos.')
    parser.add_argument('--faces_comparision_threshold', type=float, default=0.2, help='The max allowed distance threshold between two faces encodings to delare that both encodings are of the same person.')
    parser.add_argument('--show_stream', default=False, type=lambda x: (str(x).lower() == 'true'), help='A boolean value that is if set to true the video stream is also shown, while processing the videos.')
    
    # Read arguments from command line
    args = parser.parse_args()
    
    # Create a porcess to perform the web scrapping.
    process_1 = multiprocessing.Process(target=scrap_data, args=(args.person_name, scrapped_urls, args.scrap_videos_count, args.sort_videos_by, args.scrap_channels_count)) 
    
    # Start the process.
    process_1.start()
    
    # Create another porcess to download the data.
    process_2 = multiprocessing.Process(target=download_scrapped_data, args=(scrapped_urls, args.person_name, args.scrap_videos_count, args.scrap_channels_count, downloaded_data))
    
    # Start the process.
    process_2.start()

    images_paths = [os.path.join(args.images_paths,x) for x in os.listdir(args.images_paths)]
    
    # Create another porcess to process the data.
    process_3 = multiprocessing.Process(target=recogize_face, args=(downloaded_data, args.scrap_videos_count, args.scrap_channels_count, args.person_name, args.images_paths,  args.faces_comparision_threshold, args.skip_duration_in_secs, args.show_stream))
    
    # # Start the process.
    process_3.start()
    
    # Wait for the processes to end.
    process_1.join()
    process_2.join()
    process_3.join()
    
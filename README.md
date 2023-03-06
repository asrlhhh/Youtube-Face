# facial-recognition-on-youtube-videos

## What is this script doing

Given a person's name and couple of his/her profile images, the script will retrieve top N Youtube videos containing the individual. 

- Todo: add timestamps of each video

## Setting up the environment

1. First of all, Install [Python](https://www.python.org/) in your system and clone this repository.

**Note that** we tested and developed this application using Python 3.9.15 so if you are installing python from scratch to run this application we recommend you to install the same version.

2. Then open the cloned repository directory in command line and just run the following commands:

```bash
  pip install --upgrade pip
  pip install -r requirements.txt
```

It will install all the required libraries in your system.


## How to run the application

Create the image folder and put arbitrary number of images in the folder.

Just open the cloned repository directory in command line and run the following command with the arguments of your choice:

```bash
  python app.py --person_name "XYZ" --images_paths "images/XYZ" --scrap_videos_count 5 --scrap_channels_count 3  --sort_videos_by "relevence" --skip_duration_in_secs 30 --faces_comparision_threshold 0.4 --show_stream True
```

Arguments:
  * person_name:                The name of the person whose videos need to be extracted.
  * images_paths:               The paths of the images of the person (whose videos need to be extracted)
  * scrap_videos_count:         The total number of videos to scrap from the web.
  * scrap_channels_count:       The total number of channels from the web, from we want to scrap content.
  * sort_videos_by:             It specifies whether to sort the videos by "relevance", "upload-time" or "popularity" or  before scrapping.
  * skip_duration_in_secs:      The size of the skip duration in seconds after every frame during face verfication process on videos.
  * faces_comparision_theshold: The max allowed distance threshold [0,1] between two faces encodings to declare that both encodings are of the same person. Greater the video, the more lenient is the comparision criteria.
  * show_stream:                A boolean value that is if set to true the video stream is also shown, while processing the videos.
from deepface import DeepFace
from deepface.commons import distance as dst
import os
import cv2
import json
import numpy as np
   
# Load the Face Recognition model. 
face_recogntion_model = DeepFace.build_model('Facenet512')

# Create a function to perform the face recognition process.
def recogize_face(downloaded_data, scrapped_videos_count, scrapped_channels_count, person_name, images_paths, faces_comparision_theshold, skip_duration_in_secs, show_steam):
    '''
    This function extracts the videos and images path as soon as they get downloaded and performs the facial recognition on them.
    Args:
        downloaded_data:            It is a queue that contains the paths of downloaded videos, thumbnails, and channels profile pictures, etc.
        scrapped_videos_count:      The total number of videos scrapped (or being scrapped) from the web. 
        scrapped_channels_count:    The total number of channels from the web, from which we have scrapped (or being scrapped) content.
        person_name:                The name of the person whose videos need to be verified through facial recognition.
        images_paths:               The paths of the images of the person (whose videos need to be verified) stored in the disk.
        faces_comparision_theshold: The max allowed distance threshold between two faces encodings to delare that both encodings are of the same person.
        skip_duration_in_secs:      The size of the skip duration in seconds after every frame during face verfication process on videos.
        show_steam:                 A boolean value that is if set to true the video stream is also shown, while processing the videos.
    '''
    
    # Iniitlaize a dictionary to store the output.
    json_data = {"Videos Results":[], 'Channels Results': []}
    
    # Register the person and display the success message.
    person_encodings_file_path = register_user(user_name=person_name, user_images_paths=images_paths)
    print(f'{person_name} Registered Sucessfully')
    
    # Initalize a variable to store the processed videos count.
    processed_videos_count=0
    
    # Initalize a variable to store the processed channels count.
    processed_channels_count = 0
    
    # Iterate until all the videos and channels are not processed.
    while processed_videos_count<scrapped_videos_count or processed_channels_count<scrapped_channels_count:
        
        # Check if the queue contains any element(s).
        if not downloaded_data.empty():
            
            # Get an element from the queue.
            data = downloaded_data.get()
            
            # Check if the element (dictionary) contains a 'Video Info' key.
            if 'Video Info' in data:
                
                # Initalize a variable to store the video verify status.
                video_verified = False
                
                # Get the video information.
                video_data = data['Video Info']
                
                # Get the video url.
                video_url = video_data['Video URL']
                
                # Get the video thumbnail path.
                thumbnail_path = video_data['Thumbnail Path']
                
                # Check if the thumbnail of the video contains the person, we are interested in.
                if verfify_face_on_image(thumbnail_path, person_name, person_encodings_file_path, faces_comparision_theshold):
                    
                    # Set the video verify status to True.
                    video_verified = True
                    # print(f'{video_url} verified by processing the thumbnail.')
                
                # Otherwise.
                else:
                    
                    # Get the path of the video.
                    video_path = video_data['Video Path']

                    # Check if the video contains the person, we are interested in.
                    if verfify_face_on_video(video_path, person_name, person_encodings_file_path, faces_comparision_theshold, skip_duration_in_secs, show_steam):
                        
                        # Set the video verify status to True.
                        video_verified = True
                        # print(f'{video_url} verified by processing the video.')
                        
                # Store the results in the output dictionary.
                json_data['Videos Results'].append({video_url: 'This Video Contains the Person.' if video_verified else 'This Video does not Contain the Person.'})
                
                # Create a json file and store the output results.
                json_object = json.dumps(json_data, indent=4) 
                with open(os.path.join(person_name, f'{person_name}_output.json'), "w") as outfile:
                    outfile.write(json_object)
                        
                # Increment the processed videos counter.
                processed_videos_count+=1
                        
            # Check if the element (dic) contains a 'Channel Info' key.
            if 'Channel Info' in data:
                
                # Initalize a variable to store the channel verify status.
                channel_verified = False
                
                # Get the channel data.
                channel_data = data['Channel Info']
                
                #  Get the channel url.
                channel_url = channel_data['Channel URL']
                
                # Get the channel profile picture path.
                profile_pic_path = channel_data['Profile Picture Path']
                
                # Check if the profile picture of the channel contains the person, we are interested in. 
                if verfify_face_on_image(profile_pic_path, person_name, person_encodings_file_path, faces_comparision_theshold):
                    
                    # Set the channel verify status to True.
                    channel_verified = True
                    # print(f'{video_url} verified by processing the profile picture.')
                
                # Otherwise.
                else:
                    
                    # Get the paths of the downloaded videos thumbnails of the channel.
                    thumbnails_paths = channel_data['Thumbnails Paths']
                    
                    # Get the paths of the downloaded videos of the channel.
                    videos_paths = channel_data['Videos Paths']
                    
                    # Initalize a variable to store the verified videos count of the channel.
                    videos_verified = 0
                    
                    # Iterate over the videos.
                    for video_index, video_path in enumerate(videos_paths):
                        
                        # Check if the thumbnail of the video contains the person, we are interested in.
                        if verfify_face_on_image(thumbnails_paths[video_index], person_name, person_encodings_file_path, faces_comparision_theshold):
                            
                            # Increment the channel verified videos count.
                            videos_verified+=1
                        
                        # Check if the video contains the person, we are interested in.
                        elif verfify_face_on_video(video_path, person_name, person_encodings_file_path, faces_comparision_theshold, skip_duration_in_secs, show_steam):
                            
                            # Increment the channel verified videos count.
                            videos_verified+=1
                            
                    # Check if the verified videos count is > 1/3 of the total videos.
                    if videos_verified>len(videos_paths)/3:
                        
                        # Set the channel verify status to True.
                        channel_verified = True
                        
                # if channel_verified:
                #     print(f'{channel_url} verified.')
                    
                # Store the results in the output dictionary.
                json_data['Channels Results'].append({channel_url: 'This Channel Contains the Person in its Content.' if channel_verified else 'This Channel does not Contain the Person in its Content.'})
                
                # Create a json file and store the output results.
                json_object = json.dumps(json_data, indent=4) 
                with open(os.path.join(person_name, f'{person_name}_output.json'), "w") as outfile:
                    outfile.write(json_object)
                    
                # Increment the processed channels counter.
                processed_channels_count+=1    

# Create a helper function to register a new person into the database.
def register_user(user_name, user_images_paths, database_dir='database'):
    if not os.path.exists(database_dir): 
        os.makedirs(database_dir)
    database_dict = {}
    database_dict[user_name]=[]
    user_images_paths = list(user_images_paths)
    for image_path in user_images_paths:
        facial_embeddings = DeepFace.represent(img_path=image_path, model=face_recogntion_model, enforce_detection=True,detector_backend='mtcnn', align=True, normalization='Facenet')
        database_dict[user_name].append(facial_embeddings)
    output_file_path = os.path.join(database_dir, f'{user_name}.json')
    with open(output_file_path, "w") as outfile:
        outfile.write(json.dumps(database_dict, indent=2))  
    return output_file_path
    
# Create a helper function to verify a face on an image.    
def verfify_face_on_image(image_path, user_name, person_encodings_file_path, threshold=0.2):
    with open(person_encodings_file_path, 'r') as openfile:
        database_dict = json.load(openfile)
    image = cv2.imread(image_path)
    try:
        image_facial_embeddings = DeepFace.represent(image, model=face_recogntion_model, enforce_detection=True,detector_backend='mtcnn', align=True, normalization='Facenet')
        for known_encodings in database_dict[user_name]:
            distance = np.float64(dst.findCosineDistance(image_facial_embeddings, known_encodings))
            if distance<threshold:
                return True
    except:
        print("Face not Detected in the Thumbnail.") 
    return False

# Create a helper function to verify a face on a video. 
def verfify_face_on_video(video_path, user_name, person_encodings_file_path, threshold, skip_duration_in_secs, display=True):
    with open(person_encodings_file_path, 'r') as openfile:
        database_dict = json.load(openfile)
    video_reader = cv2.VideoCapture(video_path)
    video_fps = video_reader.get(cv2.CAP_PROP_FPS)
    total_frames = int(video_reader.get(cv2.CAP_PROP_FRAME_COUNT))
    skip_duration_in_frames = video_fps*skip_duration_in_secs
    if skip_duration_in_frames>total_frames:
        print(f'Failed to process {video_path}, as skip duration is greater than the total video duration.')
        return False
    if display:
        cv2.namedWindow('Video', cv2.WINDOW_NORMAL)
    face_verified_count = 0
    processed_frames_count = 0
    while processed_frames_count*skip_duration_in_frames<total_frames:
        video_reader.set(cv2.CAP_PROP_POS_FRAMES, processed_frames_count*skip_duration_in_frames)
        ret, frame = video_reader.read()
        if not ret:
            break
        try:
            frame_facial_embeddings = DeepFace.represent(frame, model=face_recogntion_model, enforce_detection=True, detector_backend='mtcnn', align=True, normalization='Facenet')
            for known_encodings in database_dict[user_name]:
                distance = np.float64(dst.findCosineDistance(frame_facial_embeddings, known_encodings))
                if distance<=threshold:
                    face_verified_count+=1
                    break
        except:
            pass
            # print(f"Face not Detected in a Frame of the video: {video_path}.")
        processed_frames_count+=1
        if display:                                      
            cv2.imshow('Video', frame)
            k = cv2.waitKey(1) & 0xFF    
            if(k == ord('q')):
                break
    print(f'Face Verified in {face_verified_count} frames.')
    if face_verified_count>processed_frames_count/10:
        return True
    return False
import os
import cv2
from moviepy.editor import VideoFileClip
from moviepy.video.fx.all import speedx

# Define function to normalize the videos framerates
def normalize_framerates(
    source_folder_path: str='./videos',
    destination_folder_path: str='./normalized_videos',
    new_frame_rate: float=30,
    new_bitrate: str='15000k',
    new_width: int=1080,
    new_height: int=1920,
    encoding_codec: str='libx264',
    encoding_preset: str='ultrafast',
    encoding_threads: int=2) -> None:

    print('Executing normalize_framerates()...')

    # Try to get a list of files in the folder
    try:
        video_files = os.listdir(source_folder_path)
    except:
        print('Could not get a list of files in the video source folder.')
        return
    
    # Loop through the video files
    for video_file in video_files:

        # Try to open the video file
        try:
            video = VideoFileClip(source_folder_path + '/' + video_file)
        except:
            continue
        
        # Set the output extension
        output_filename = 'normalized_' + video_file[:-4] + '.mp4'

        # Get the width and height of the video
        width, height = video.size
        # Get the video rotation
        rotation = video.rotation

        # If the new aspect ratio mode is different from the video aspect ratio and the video rotation is 0 then rotate the video 90 degrees
        if (new_width / new_height > 1) ^ (width / height > 1) and rotation == 0:
            video = video.rotate(90)

        # Resize the video to have the width and height values specified
        video = video.resize((new_width, new_height))
        
        # Calculate the original duration of  the video
        original_duration = video.duration
        
        # Create a new normalized video file
        normalized_video = speedx(video, factor=new_frame_rate/video.fps, final_duration=original_duration)

        # Check if the normalized folder exists and create it if it doesn't
        if not os.path.exists(destination_folder_path):
            os.mkdir(destination_folder_path)

        # Write the normalized video file to the destination folder
        normalized_video.write_videofile(destination_folder_path + '/' + output_filename, codec=encoding_codec, preset=encoding_preset, threads=encoding_threads, fps=new_frame_rate, bitrate=new_bitrate)

        # Close the video file
        video.close()

# Define function to get the video files keyframes (frist_brightness_change, ending_frame)
def get_video_files_keyframes(
    source_folder_path: str='./normalized_videos',
    brightness_difference_ratio_threshold: int=5,
    brightness_difference_threshold: int=10) -> dict:

    print('Executing get_video_files_keyframes()...')

    # Try to get a list of files in the folder
    try:
        video_files = os.listdir(source_folder_path)
    except:
        print('Could not get a list of files in the normalized video folder.')
        return

    # Create an empty dictionary to save the keyframes
    videos_keyframes = {}

    # Loop through the video files
    for video_file in video_files:

        # Try to open the video file
        try:
            video = cv2.VideoCapture(source_folder_path + '/' + video_file)
        except:
            continue

        print('Analyzing video: ' + video_file)

        # Read the first frame
        ret, previous_frame = video.read()

        # Start the frame count
        frame_number = 1

        # Set an initial previous difference value high to start
        previous_difference = 1000

        # Loop through the frames in the video
        while True:
            
            # Read the next frame
            ret, current_frame = video.read()

            # Check if a frame was successfully read
            if not ret:
                break

            # Increment the frame count
            frame_number += 1

            # Convert the previous frame to grayscale
            previous_frame_gray = cv2.cvtColor(previous_frame, cv2.COLOR_BGR2GRAY)

            # Convert the current frame to grayscale
            current_frame_gray = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)

            # Calculate the difference between the previous and current frames
            difference = cv2.absdiff(previous_frame_gray, current_frame_gray)

            # Calculate the average of the difference
            current_difference = cv2.mean(difference)[0]

            # Get the difference ratio between the current and previous frame if previous difference is greater than 0
            if previous_difference > 0:
                brightness_difference_ratio = current_difference / previous_difference
            else:
                brightness_difference_ratio = 0
            
            # Check if the average difference is greater than a threshold
            if brightness_difference_ratio > brightness_difference_ratio_threshold and current_difference > brightness_difference_threshold:
                videos_keyframes[video_file] = {
                    'first_brightness_change': frame_number,
                    'ending_frame': video.get(cv2.CAP_PROP_FRAME_COUNT)
                }
                # Break the loop as the first_brightness_change has been found
                break

            # Update the previous frame
            previous_frame = current_frame

            # Update the previous difference
            previous_difference = current_difference

        # Release the video file
        video.release()

    # Print the keyframes
    print(videos_keyframes)

    # Return the keyframes
    return videos_keyframes

# Define function to synchronize the video files to start at the first_brightness_change and have the same length
def synchronize_normalized_videos(
    source_folder_path: str='./normalized_videos',
    destination_folder_path: str='./synchronized_videos',
    videos_keyframes: dict={},
    source_frame_rate: float=30,
    start_offset_seconds: float=0) -> None:

    print('Executing synchronize_normalized_videos()...')

    # Check if the videos_keyframes dictionary is empty
    if not videos_keyframes:
        print('The videos_keyframes dictionary is empty.')
        return

    # Calculate the start frame offset based on the source_frame_rate and the start_offset_seconds variables
    start_frame_offset = int(source_frame_rate * start_offset_seconds)

    # Calculate the duration of the videos in frames based on the video with the longest duration from the first_brightness_change keyframe + start_frame_offset
    synchronized_duration = min(videos_keyframes[video_key]['ending_frame'] - (videos_keyframes[video_key]['first_brightness_change'] + start_frame_offset) for video_key in videos_keyframes.keys())

    # Loop through the video files and rewrite them adjusted (synchronized) to the destination folder
    for video_file in videos_keyframes.keys():

        # Try to open the video file
        try:
            video = cv2.VideoCapture(source_folder_path + '/' + video_file)
        except:
            print('Could not open video: ' + video_file)
            continue

        # Get the video properties
        video_fps = video.get(cv2.CAP_PROP_FPS)
        video_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
        video_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # Set the starting frame
        video.set(cv2.CAP_PROP_POS_FRAMES, videos_keyframes[video_file]['first_brightness_change'] + start_frame_offset)

        # Check if the synchronized folder exists and create it if it doesn't
        if not os.path.exists(destination_folder_path):
            os.makedirs(destination_folder_path)

        # Try to create a VideoWriter object
        try:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            writer = cv2.VideoWriter(destination_folder_path + '/' + 'synchronized_' + video_file[11:], fourcc, video_fps, (video_width, video_height))
        except:
            continue

        # Read and write the frames until the synched duration is reached
        frame_count = 0
        while video.isOpened() and frame_count < synchronized_duration:
            
            # Read the next frame
            ret, frame = video.read()
            
            # Check if a frame was successfully read
            if not ret:
                break

            # Write the frame
            writer.write(frame)
            frame_count += 1

        # Release the video file
        video.release()
        writer.release()

def main() -> None:

    # Normalize the video files framerates
    normalize_framerates(source_folder_path='./videos',
                         destination_folder_path='./normalized_videos',
                         new_frame_rate=30,
                         new_bitrate='15000k',
                         new_width=1080,
                         new_height=1920,
                         encoding_codec='libx264',
                         encoding_preset='ultrafast',
                         encoding_threads=2)
    
    # Get the keyframes
    videos_keyframes = get_video_files_keyframes(source_folder_path='./normalized_videos',
                              brightness_difference_ratio_threshold=5,
                              brightness_difference_threshold=20)
    
    # Adjust the normalized video files to start at the first_brightness_change + start_frame_offset and have the same length
    synchronize_normalized_videos(source_folder_path='./normalized_videos',
                                  destination_folder_path='./synchronized_videos',
                                  videos_keyframes=videos_keyframes,
                                  source_frame_rate=30,
                                  start_offset_seconds=0)
    
if __name__ == "__main__":
    main()

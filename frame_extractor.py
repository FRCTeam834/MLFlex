# Written by Christian Piper
# First Robotics Team 834
# Created: 8/25/20

# Import libaries
import cv2
import os

def main():
    convert_video("test_video.mp4", "/home/cap1sup/Desktop/Robotics/MLFlex/testing/", "/home/cap1sup/Desktop/Robotics/MLFlex/testing/video_frames", 3, True)

def convert_video(video_filename, input_path, output_path, frame_skip, feedback):

    # Read the video
    video = cv2.VideoCapture(os.path.join(input_path, video_filename))

    # Split the extension off of the video filename
    raw_video_filename, video_file_ext = os.path.splitext(video_filename)

    # Get the total number of frames
    total_frames = count_frames(video)

    # Create a frame counter
    current_frame = 0

    # Loop continuously, looking for frames
    while True:

        # Skip over the frames we don't need
        for frame_skip_count in range(frame_skip):
            print()

            # Read the frame
            grabbed, frame = video.read()

            # Increment the frame counter
            current_frame = current_frame + 1

        # Check to see if the video isn't over
        if grabbed:

            # Create a filename for the image
            image_name = os.path.join(output_path, raw_video_filename + "_" + str(current_frame) + ".jpg")

            # Save the image
            cv2.imwrite(image_name, frame)
            print()

            # Provide feedback
            if feedback:
                print("Creating... " + image_name + "   Progress: " + str(current_frame / frame_skip) + " out of " + str(total_frames))
        
        # Video is over, time to break
        else:
            break
    
    # Release all of the space back
    video.release()
    cv2.destroyAllWindows()

def count_frames(openCV_video):

	# Initialize the total number of frames read
	total_frames = 0

	# Loop over the frames of the video
	while True:

		# Grab the current frame
		(grabbed, frame) = openCV_video.read()
	 
		# Check to see if we have reached the end of the video
		if not grabbed:
			break

		# Increment the total number of frames read
		total_frames += 1

	# Return the total number of frames in the video file
	return total_frames


main()
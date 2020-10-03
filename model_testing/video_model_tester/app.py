# Written by Christian Piper
# First Robotics Team 834
# Created: 10/2/20

# Import libraries
import edgeiq
import time
import cv2
import os

# Parameters
model = "CAP1Sup/test_2021_crop_flip_images"
source_video_file = "C:\\Users\\xmanp\\Desktop\\GitHub\\MLFlex\\testing\\Goal.mp4"
confidence = 0.15

def main():

    # Log time for statistics
    start_time = time.time()

    # Load the models for processing
    obj_detect = edgeiq.ObjectDetection(model)
    obj_detect.load(engine=edgeiq.Engine.DNN)

    # Print out useful info
    print("Engine: {}".format(obj_detect.engine))
    print("Accelerator: {}\n".format(obj_detect.accelerator))
    print("Model:\n{}\n".format(obj_detect.model_id))
    print("Labels:\n{}\n".format(obj_detect.labels))

    # Open the Video file
    source_video = cv2.VideoCapture(source_video_file)

    # Create a frame counter
    current_frame = 1

    # Get the FPS of the original video file
    source_video_framerate = source_video.get(cv2.CAP_PROP_FPS)

    # Print that we're counting the frames
    print("Beginning to count frames of source video")

    # Count the number of frames in the source video
    source_video_frame_count = count_frames(cv2.VideoCapture(source_video_file))

    # Split the source file path
    source_video_file_path_head, source_video_file_path_tail = os.path.split(source_video_file)

    # Split the extension of the source video
    raw_source_video_filename, source_video_ext = os.path.splitext(source_video_file_path_tail)

    # Create the new file path of the annotated video
    annotated_video_file_path = os.path.join(source_video_file_path_head, raw_source_video_filename + "_annotated" + source_video_ext)

    # Create a new video writer
    with edgeiq.VideoWriter(annotated_video_file_path, fps = source_video_framerate, codec = 'MJPG') as video_writer:

        # Loop through the frames of the video
        while(source_video.isOpened()):
            
            # Read the next frame from the video
            ret, frame = source_video.read()

            # If we're at the end, break because we're finished
            if ret == False:
                break

            # Run model over the frame
            results = obj_detect.detect_objects(frame, confidence_level = confidence)

            # Add the bounding boxes to the frame
            annotated_frame = edgeiq.markup_image(frame, results.predictions, colors = obj_detect.colors)

            # Write the frame to the video
            video_writer.write_frame(annotated_frame)

            # Print the progress of the conversion
            print("Progress: Frame " + str(current_frame) + " out of " + str(source_video_frame_count))

            # Increment the counter
            current_frame = current_frame + 1

    # Close the annotated video
    video_writer.close()

    # Close the source video file and release the RAM
    source_video.release()
    cv2.destroyAllWindows()

    # Provide user feedback
    print("Conversion process complete, took " + str(round(time.time() - start_time, 2)) + " seconds")

# Function for counting the frames of a video
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

if __name__ == "__main__":
    main()

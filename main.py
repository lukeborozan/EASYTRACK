import cv2
import streamlit as st
from pytube import YouTube
from ultralytics.models import yolo
import track
from track import *
from track import on_predict_start
from yolo_tracking.examples.detectors.__init__ import get_yolo_inferer
from ultralytics import YOLO
from yolo_tracking.examples.utils import write_mot_results
from track import run
import os

#Making the page

st.set_page_config(page_title = "main", page_icon = "soccer-ball.svg", layout = "wide")
header = st.container()
topcontent = st.container()

with header:
    st.title("EasyTrack")
    st.subheader("A sports stats tracking system")

with topcontent:
    st.header("A brief description of how to use the app")
    st.text("1. Upload the game file you want to analyze")
    st.text("2. Click the get stats button to get your stats")
st.markdown("---")


#User inputs the path of thier video
vidpath = st.container()
with vidpath:
    path = st.text_input("Paste the path of the video you want analyzed here. Press enter when finished to analyze the film.")
    run = st.button("Press this button to run the code.")
    if run:
        if 'path' not in st.session_state:
            st.session_state.path = path + '.txt'
            #Track.py analyzes path name + .txt so add .txt
        opt = track.parse_opt()
        opt.source = path
        opt.project = 'yolo_tracking'
        opt.yolo_model = '/Users/peterborozan/PycharmProjects/Streamlit EASYTRACK/REALFRbestyolov8.pt'
        opt.save = True
        opt.save_mot = True
        track.run(opt)
        #Methods in the track.py file


#Function to find the center of any bounding box
def center(point_x, point_y, wid, heigh):
     return ((point_x + wid // 2), (point_y + heigh //2))


#Initialize session state, weird streamlit caveat
if 'frame_number' not in st.session_state:
    st.session_state.frame_number = []

#Initialize session state again
if 'ball_positions' not in st.session_state:
    st.session_state.ball_positions = []

#Function that returns the center of the ball and frame number of those centers for the ball class. 
#Returns in an array called ball_positions
def parse_center_ball(file_path, ball_class =2):
    ball_positions = []
    #Need to pass center_ball and frame_number as arrays
    #an array that resets itself every time it goes through the for loop
    with open(file_path, 'r') as file:
        #Open the file
        for line in file:
            data = line.split()
            #Split the date in the file into the components shown below
            frame_number, object_id, x, y, width, height, _, class_id, *_ = map(int, data)
            if class_id == ball_class:
                #Ball class was saved as "2" in text file, so if its a ball
                center_ball = center(x, y, width, height)
                #Find the center of the frame
                ball_positions.append((center_ball, frame_number))
                #Add the center and the frame number to the ball_positions array
    return ball_positions

center_balls = []
getstats = st.button("Press the button to get your stats.")
if getstats:
    path_txt = path + '.txt'
    ball_positions = parse_center_ball(path_txt)
    #Get the centers of the ball for a given link

    center_balls = [position[0] for position in ball_positions]
    frames = [position[1] for position in ball_positions]
    #Saved the frames and centers based on the way the array was saved

#Function for getting the distance between two centers
def distance(point1, point2):
    return ((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2) ** 0.5

#Function for determining if the ball is stationary
def ball_is_stationary(center_balls, thresholddistance = 5, min_duration = 10):
    frames_stationary = 0
    stationary_frames = []

    for i in range(len(center_balls) - 1):
        distance_moved = distance(center_balls[i], center_balls[i + 1])
        #Calculates distance between centers in the center_balls array
        if distance_moved < thresholddistance:
            frames_stationary += 1
            if frames_stationary >= min_duration:
                #If its stationary for more than 10 frames
                return frames
        else:
            frames_stationary = 0
    return stationary_frames

stationary_frames = ball_is_stationary(center_balls)
st.write(stationary_frames)
#The frames at which the ball is stationary


times = set()
for i in range(len(stationary_frames)- 1):
    z = 0
    #Creates video capture object
    cap = cv2.VideoCapture(path)

    #Counts the number of frames
    fps = cap.get(cv2.CAP_PROP_FPS)
    totalNoFrames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    durationInSeconds = totalNoFrames // fps

    if (stationary_frames[i] // fps) not in times:
        st.write("Ball is stationary at " + str((stationary_frames[i]) // fps) + ". This could be a potential stoppage of play.")
        #Prints the seconds at which the ball is stationary
        times.add(stationary_frames[i] // fps)
        #Makes sure there it prints only one time for that given second


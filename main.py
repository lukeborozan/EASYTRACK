
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

video_file = open('yolo_tracking/exp/longvidyolo.mp4', 'rb')
video_bytes = video_file.read()
st.video(video_bytes)

with topcontent:
    st.header("A brief description of how to use the app")
    st.text("1. Upload the game file you want to analyze")
    st.text("2. Click the get stats button to get your stats")
st.markdown("---")

#Upload the files
videos = st.file_uploader("Upload your game film here. Press the analyze button when completed.", type=["mp4", "mov"], accept_multiple_files=True)
if videos is not None:
    for video in videos:
        st.video(video)

tempvid= st.container()
with tempvid:
    analyze = st.button("Analyze")
    if analyze:
        video_path = "temp_video.mp4"
        with open(video_path, "wb") as f:
            f.write(video.getbuffer())
        opt = track.parse_opt()
        opt.source = video_path
        opt.project = 'yolo_tracking'
        opt.yolo_model = '/Users/peterborozan/PycharmProjects/Streamlit EASYTRACK/REALFRbestyolov8.pt'
        opt.save = True
        opt.save_mot = True
        track.run(opt)

def download_youtube_video(url, output_path='downloaded_videos'):
    yt = YouTube(url)
    stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    return stream.download(output_path=output_path)

ytlink = st.container()
with ytlink:
    link = st.text_input("Paste the link to the YouTube video here. Press enter when finished to analyze the flim.")
    if link:
        opt = track.parse_opt()
        opt.source = download_youtube_video(link)
        opt.project = 'yolo_tracking'
        opt.yolo_model = '/Users/peterborozan/PycharmProjects/Streamlit EASYTRACK/REALFRbestyolov8.pt'
        opt.save = True
        opt.save_mot = True
        track.run(opt)

        # video_path = download_youtube_video(link)
        # process_video(video_path, output_dir)

vidpath = st.container()
with vidpath:
    path = st.text_input("Paste the path of the video you want analyzed here. Press enter when finished to analyze the film.")
    if path:
        opt = track.parse_opt()
        opt.source = path
        opt.project = 'yolo_tracking'
        opt.yolo_model = '/Users/peterborozan/PycharmProjects/Streamlit EASYTRACK/REALFRbestyolov8.pt'
        opt.save = True
        opt.save_mot = True
        track.run(opt)

if 'path' not in st.session_state:
    st.session_state.path = path + ".txt"

def center(point_x, point_y, wid, heigh):
    return ((point_x + wid // 2), (point_y + heigh //2))

def distance(point1, point2):
    return ((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2) ** 0.5


##################### CHECK THAT ITS A VALID LINK #########################

# list = []
# if path and link:
#     if os.path.isfile(path):
#         l.append(path)
#
# for i in list:
#     i.tracking()

#Every time someone uses the buttons, check that its a valid link/path/etc
#append the list with that link
#run a for loop through the list with an analyzation of each item that has been added

################## WHEN THEY INPUT A VIDEO FILE ##########################


        # for video in videos:
        #     #Save uploaded video to temporary file
        #     video_path = "temp_video.mp4"
        #     with open(video_path, "wb") as f:
        #         f.write(video.getbuffer())
        #
        #         #define output directory
        #
        #         output_dir = "path_to_output_directory"
        #         #call the process video function
        #
        #         #process_video2(video_path, output_dir)
        #         tracking2 = track.run(source = 'clip.mp4', conf = args.conf, iou = args.iou, show = args.show, stream = True, device = args.device, show_conf = args.show.conf, save_txt = args.save_txt, show_labels = args.show_labels, save = store_true, verbose=args.verbose, exist_ok=args.exist_ok, project=args.project, name=args.name, classes=args.classes, imgsz=args.imgsz, vid_stride=args.vid_stride, line_width=args.line_width)

        #Save uploaded video to temporary file



##PARSE THE TEXT FILE SO THAT BALL_POSITIONS ARRAY CONTAINS FRAME NUMBER, AND CENTER OF BOUDNING BOX IN (X,Y) FORMAT##


ball_positions = []

if 'ball_positions' not in st.session_state:
    st.session_state.ball_positions = 0

def parse_center_ball(file_path, ball_class):
    global ball_positions
    ball_positions = []
    with open(file_path, 'r') as file:
        for line in file:
            data = line.split()
            frame_number, object_id, x, y, width, height, rand, class_id, rand2, *_ = map(int, data)
            if class_id == ball_class:
                center_ball = center(x, y, width, height)
                ball_positions.append((frame_number, center_ball))
    return ball_positions
ball_positions = parse_center_ball(st.session_state.path, ball_class= 2)


#ball class
frame_number = 0

if 'frame_number' not in st.session_state:
    st.session_state.frame_number = 0

def ball_is_stationary(ball_positions, threshold = 5, min_duration = 30):
    global frame_number
    frames_stationary = 0
    for i in range(1, len(ball_positions)):
        if distance(ball_positions[i], ball_positions[i + 1]) < threshold:
            frames_stationary += 1
            if frames_stationary >= min_duration:
                return frame_number
            else:
                frames_stationary = 0
    return False

def parse_center_goal(file_path, goal_class):
    goal_center = []
    with open(file_path, 'r') as file:
        for line in file:
            data = line.split()
            frame_number, object_id, x, y, width, height, class_id, *_ = map(int, data)
            if class_id == goal_class:
                center_goal = center(x, y, width, height)
                goal_center.append(center_goal)
    return goal_center
goal_center = parse_center_goal(st.session_state.path, goal_class= 1)

goal = 0

if 'goal' not in st.session_state:
    st.session_state.goal = 0

def is_it_goal(goal_positions, x, width, y, height, duration = 30):
    global goal
    frames = 0
    for i in range(1, len(goal_positions)):
        if x < goal_center < x + width and y < goal_center < y + height:
            frames+=1
            if frames > duration:
                st.session_state.goal+=1
        else:
            return "There were no goals scored."

    return goal



def parse_player_tracking_data(file_path, player_class):
    player_positions = []
    with open(file_path, 'r') as file:
        for line in file:
            data = line.split()
            frame_number, object_id, x, y, width, height, class_id, *_ = map(int, data)
            if class_id == player_class:
                    center_player = center(x, y, width, height)
                    player_positions.append((frame_number, center_player))
    return player_positions
player_positions = parse_player_tracking_data(st.session_state.path, player_class =0)







#helper function center- find the center of any object you detect
#if center of ball is anywhere in the bounding box of a goal, call it a goal
#kick function
#ball movement


        #Create a for loop that iterates through file object.Iterate through videos and through each iteration, grab the video file
        #for i in len(videos) each element of the file uploader object and then runs the track.py file on that file and saves it
        #Another button that downloads the data because we can't save it?
        #Pass through each element f the upload
        #videos(i), convert to cv2??, can also save as a pandas dataframe??
        #Every time you grab a video file, want to analyze that video file. Pass the video file once its converted to the proper format to the object track.py which will have final.pty
        #*** need pt and tracking files. Put the yolo tracking folder n that motherfucker- DONE
        #Save the text file for each video i so we have the objects and their ids in each frame




#get the path instead of the temp video
#Choose to upload youtube link or path
#Buttons to add link and append it to the video
# The model requirea following input features as a DataFrame:

# [   'sex', 1 for male
#      'age', from 15 - 25
#      'Medu', mother's education (numeric: 0 - none,  1 - primary education (4th grade), 2 – 5th to 9th grade, 3 – secondary education or 4 – higher education)
#      'Fedu', father's education (numeric: 0 - none,  1 - primary education (4th grade), 2 – 5th to 9th grade, 3 – secondary education or 4 – higher education)
#      'traveltime', home to school travel time (numeric: 1 - <15 min., 2 - 15 to 30 min., 3 - 30 min. to 1 hour, or 4 - >1 hour)
#      'studytime', weekly study time (numeric: 1 - <2 hours, 2 - 2 to 5 hours, 3 - 5 to 10 hours, or 4 - >10 hours)
#      'failures', number of past class failures (numeric: n if 1<=n<3, else 4)
#     'activities', 1 if student participated in extra curicular activities
#      'nursery', 1 for yes and 0 for no ( yes if student read nursery in this shcool )
#      'higher', 1 for yes and 0 for no ( if student wants to study higher )
#     'internet', 1 for yes and 0 for no
#      'freetime', free time after school (numeric: from 1 - very low to 5 - very high)
#      'goout', going out with friends (numeric: from 1 - very low to 5 - very high)
#      'health', current health status (numeric: from 1 - very bad to 5 - very good)
#      'absences', number of school absences (numeric: from 0 to 93)
#      'G1', first period grade (numeric: from 0 to 20)
#      'G2', second period grade (numeric: from 0 to 20)
#      'is_urban', 1 for yes and 0 for no
#      'Mjob_health', 1 for yes and 0 for no
#      'Mjob_other', 1 for yes and 0 for no
#      'Mjob_services', 1 for yes and 0 for no
#     'Mjob_teacher', 1 for yes and 0 for no
#      'Fjob_health', 1 for yes and 0 for no
#      'Fjob_other', 1 for yes and 0 for no
#      'Fjob_services', 1 for yes and 0 for no
#     'Fjob_teacher', 1 for yes and 0 for no
#      'reason_home', 1 for yes and 0 for no
#      'reason_other', 1 for yes and 0 for no
#      'reason_reputation', 1 for yes and 0 for no
#     'guardian_mother', 1 for yes and 0 for no
#      'guardian_other'1 for yes and 0 for no
# ]

import streamlit as st
import gspread as gs
import pandas as pd
import numpy as np
# from oauth2client.service_account import ServiceAccountCredentials
# import datetime
from time import time
import matplotlib.pyplot as plt
import seaborn as sns
import pickle


# setting page configurations
st.set_page_config("Forecasting", layout="wide", initial_sidebar_state="collapsed", page_icon="hourglass_flowing_sand")
st.title(":hourglass_flowing_sand: Result Forecasting")
st.caption("Enter student details and get a prediction about its final term performance. The system will automatically generate predictions for either selected class students or all school students when it is in use.")
st.divider()



############################################# FUNCTIONS
@st.cache_resource
def load_model():
    """Loads the model and returns it."""
    try:
        print("Loading the model")
        with open("pages/school_MlModel.pkl", 'rb') as model_file:
            model=pickle.load(model_file)
    except:
        st.error("Model loading failed.")
        print("Model loading failed.")
        model=1
    
    return model

def inference_model(model, stud_input):
    """Requires model and the input. Makes prediction with the model and returns position after rounding."""
    print("Inferencing with model.")

    prediction=model.predict(stud_input)
    prediction=np.round(list(prediction)[0],0).astype(int)

    print("Done all. Returning prediction.")

    return prediction

def transform_position(position):
    """Requires a position (int) and converts it according to our encoding. If user entered 1 then according to our encoding, it is 20 etc. Returns the transformed position."""
    if (position==1):
        position=20
    elif (position==20):
        position=1
    else:
        position=20-position

    return position



############################################# UI (setting inputs)
# each column contains multiple inputs and encode them on the spot
col1, col2, col3, col4=st.columns(4)
with col1:
    sex=st.selectbox("Gender of student", options=["Male", "Female"])
    # encoding
    if (sex=="Male"):
        sex=1
    else:
        sex=0

    Fedu=st.selectbox("Father Education", options=["None", "Half Matric", "Middle", "Matric", "Higher"])
    # encoding
    if (Fedu=="None"):
        Fedu=0
    elif (Fedu=="Half Matric"):
        Fedu=1
    elif (Fedu=="Middle"):
        Fedu=2
    elif (Fedu=="Matric"):
        Fedu=3
    else:
        Fedu=4

    Mjob=st.selectbox("Mother Job", options=["Health care practitioner", "Teacher", "In Govt. Services", "Other"])
    # declaring variables to encode the feature
    Mjob_health=0
    Mjob_teacher=0
    Mjob_services=0
    Mjob_other=0
    if (Mjob=="Health care practitioner"):
        Mjob_health=1
    elif (Mjob=="Teacher"):
        Mjob_teacher=1
    elif (Mjob=="In Govt. Services"):
        Mjob_services=1
    else:
        Mjob_other=1

    activities=st.selectbox("Extra Curriculum activities", options=["yes", "no"])
    # encoding
    if (activities=="yes"):
        activities=1
    else:
        activities=0

    internet=st.selectbox("Has access to internet?", options=["yes", "no"])
    # encoding
    if (internet=="yes"):
        internet=1
    else:
        internet=0

    health=st.selectbox("Health", options=["Weak", "Slight weak", "Average", "Healthy", "Very healthy"])
    # encoding
    if (health=="Weak"):
        health=1
    elif (health=="Slight Weak"):
        health=2
    elif (health=="Average"):
        health=3
    elif (health=="Healthy"):
        health=4
    else:
        health=5

    G1=st.number_input("Position in 1st term (1-20", min_value=1, max_value=20, value=5)
    # encoding
    G1=transform_position(G1)

    reason=st.selectbox("Reason for selecting the school", options=["Near to home", "School reputation", "Others"])
    # declaring features for encoding
    reason_home=0
    reason_reputation=0
    reason_other=0
    if (reason=="Near to home"):
        reason_home=1
    elif (reason=="School reputation"):
        reason_reputation=1
    else:
        reason_other=1


with col2:
    age=st.number_input("Age", min_value=10, value=15)

    traveltime=st.selectbox("Time to reach school", options=["<15 min.", "15 to 30 min.", "30 min. to 1 hour", ">1 hour"])
    # encoding
    if (traveltime=="<15 min."):
        traveltime=1
    elif (traveltime=="15 to 30 min."):
        traveltime=2
    elif (traveltime=="30 min. to 1 hour"):
        traveltime=3
    else:
        traveltime=4

    Fjob=st.selectbox("Father Job", options=["Health care practitioner", "Teacher", "In Govt. Services", "Other"])
    # declaring variables to encode the feature
    Fjob_health=0
    Fjob_teacher=0
    Fjob_services=0
    Fjob_other=0
    if (Fjob=="Health care practitioner"):
        Fjob_health=1
    elif (Fjob=="Teacher"):
        Fjob_teacher=1
    elif (Fjob=="In Govt. Services"):
        Fjob_services=1
    else:
        Fjob_other=1

    nursery=st.selectbox("Learned nursery here?", options=["yes", "no"])
    # encoding
    if (nursery=="yes"):
        nursery=1
    else:
        nursery=0

    freetime=st.selectbox("Free Time", options=["1 hour", "2 hour", "3 hour", "4 hour", "5 hour"])
    # encoding
    if (freetime=="1 hour"):
        freetime=1
    elif (freetime=="2 hour"):
        freetime=2
    elif (freetime=="3 hour"):
        freetime=3
    elif (freetime=="4 hour"):
        freetime=4
    else:
        freetime=5

    absences=st.number_input("No. of school absences", min_value=0, value=0)

    G2=st.number_input("Position in 2nd term (1-20", min_value=1, max_value=20, value=5)
    # encoding
    G2=transform_position(G2)
    

with col3:
    Medu=st.selectbox("Mother Education", options=["None", "Half Matric", "Middle", "Matric", "Higher"])
    # encoding
    if (Medu=="None"):
        Medu=0
    elif (Medu=="Half Matric"):
        Medu=1
    elif (Medu=="Middle"):
        Medu=2
    elif (Medu=="Matric"):
        Medu=3
    else:
        Medu=4

    studytime=st.selectbox("Weekly study time", options=["< 2 hours", "2 - 5 hours", "5 - 10 hours", "> 10 hours"])
    # encoding
    if (studytime=="< 2 hours"):
        studytime=1
    elif (studytime=="2 - 5 hours"):
        studytime=2
    elif (studytime=="5 - 10 hours"):
        studytime=3
    else:
        studytime=4

    guardian=st.selectbox("Guardian", options=["Mother", "Father", "Other"])
    # declaring features for encoding
    guardian_mother=0
    guardian_other=0
    if (guardian=="Mother"):
        guardian_mother=1
    else:
        guardian_other=1

    failures=st.number_input("No of failures", value=0, min_value=0, max_value=10)

    higher=st.selectbox("Wants to complete higher education?", options=["yes", "no"])
    # encoding
    if (higher=="yes"):
        higher=1
    else:
        higher=0

    goout=st.selectbox("Time spend going out", options=["1 hour", "2 hour", "3 hour", "4 hour", "5 hour"])
    # encoding
    if (goout=="1 hour"):
        goout=1
    elif (goout=="2 hour"):
        goout=2
    elif (goout=="3 hour"):
        goout=3
    elif (goout=="4 hour"):
        goout=4
    else:
        goout=5

    is_urban=st.selectbox("Student residence area", options=["Urban", "Rural"])
    # encoding
    if (is_urban=="Urban"):
        is_urban=1
    else:
        is_urban=0

    

# submit button
st.divider()
submit_btn=st.button("Submit", type="primary", use_container_width=True)


######################################################### Handling submission
if submit_btn:
    # preparing inputs
    # feature names
    feats=["sex", "age", "Medu", "Fedu", "traveltime", "studytime", "failures", "activities", "nursery", "higher", "internet", "freetime", "goout", "health", "absences", "G1", "G2", "is_urban", "Mjob_health", "Mjob_other", "Mjob_services", "Mjob_teacher", "Fjob_health", "Fjob_other", "Fjob_services", "Fjob_teacher", "reason_home", "reason_other", "reason_reputation", "guardian_mother", "guardian_other"]
    # values
    vals=[sex, age, Medu, Fedu, traveltime, studytime, failures, activities, nursery, higher, internet, freetime, goout, health, absences, G1, G2, is_urban, Mjob_health, Mjob_other, Mjob_services, Mjob_teacher, Fjob_health, Fjob_other, Fjob_services, Fjob_teacher, reason_home, reason_other, reason_reputation, guardian_mother, guardian_other]

    # dataframe creation
    stud_input=pd.DataFrame([vals], columns=feats)

    # writting created dataframe
    st.dataframe(stud_input)
    # load model and inference with it
    with st.spinner("Predicting..."):
        prediction=inference_model(load_model(), stud_input)
        # transforming the position and presenting it.
        prediction=transform_position(prediction)
        st.write(f"Your predicted position is: :blue[{prediction}].")
    
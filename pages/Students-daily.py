# We are using specified number of columns from the dataframe using list/dataframe slicing technique, for the purpose of checking duplicate row. If number of columns are changed, then we'll need to adjust that.

import streamlit as st
import gspread as gs
import pandas as pd
import numpy as np
from oauth2client.service_account import ServiceAccountCredentials
import datetime
from time import time

# setting page configurations
st.set_page_config("Daily Performance", layout="wide", initial_sidebar_state="collapsed", page_icon="bar_chart")
st.title(":bar_chart: Students Daily Performance")
st.caption("Upate your students performance every working day for optimal management.")
st.divider()


################################### Initial Variables and Functions
# worksheet related variables
worksheet_name="dataset-main"
sheetname="full-dataset"
json_key_filename="streamlit-test-421310-8019a039f9d5.json"

# date realted variables
current_year=datetime.datetime.now().year
current_month=datetime.datetime.now().month
current_day=datetime.datetime.now().day

# dataframe related variables
df_class_col="class_with_section"
df_class_incharge_col="incharge"
df_student_name_col="student_name"
df_student_gender_col="student_gender"
df_relation_col="student_relation_with_guardian"
df_guardian_name_col="guardian_name"
df_stud_guar_name_col="student_guardian"
df_subjects_col="class_subjects"
df_subj_teach_col="subject_teacher"


# functions
@st.cache_data
def load_df(_sheet):
    """Loads all the previous records from the provided sheet, converts them into pandas dataframe and returns that dataframe."""
    data=sheet.get_all_records()
    print("Got all the records. Converting into DataFrame")
    
    # converting into pandas DataFrame
    data=pd.DataFrame(data)
    print("DataFrame prepared. Returning it.")
    return data

@st.cache_resource
def open_sheet():
    """Connects with the worksheet, opens the 1st sheet and returns that."""

    # connecting with the sheet
    # scope=["https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive"]
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds=ServiceAccountCredentials.from_json_keyfile_name(json_key_filename, scope)
    client=gs.authorize(creds)
    print("Connected")

    # Opens the spreadsheet specified sheet
    spreadsheet=client.open(worksheet_name)
    print("Worksheet opened.")

    # Getting the specified sheet
    sheet=spreadsheet.worksheet(sheetname)
    print("Got specified sheet. Returning it")
    return sheet

def append_new_row(row):
    """Gets the cached sheet by calling open_sheet() and tries to append the new row. If success then return 0 else returns 1."""
    print("Getting sheet for appending new row.")
    start_time=time()
    sheet=open_sheet()

    try:
        sheet.append_row(values=row)

        end_time=time()
        time_to_append=(end_time-start_time)

        print(f"Appended. Time takes: {time_to_append}")
        return 0
    
    except Exception as err:
        end_time=time()
        time_to_append=(end_time-start_time)

        print(f"Appending failed. Time taken: {time_to_append} {err}")
        return 1



################################## preparing data
# Opening sheet and creating dataframe
sheet=open_sheet()
df=load_df(sheet)


# functions
@st.cache_data
def get_classes():
    """Retrieves unique classes from the dataframe and returns them as list."""

    print("Getting unique school classes as list..")
    school_classes=list(df[df_class_col].unique())
    print("Got classes as list. Returning them.")
    return school_classes


# creating variables to use while data entry e.g. classes, class students etc.
school_classes=get_classes()



#################################### UI Creation
# defining time section
year_col, month_col, day_col = st.columns(3)
with year_col:
    selected_year=st.number_input("Year", value=current_year)

with month_col:
    selected_month=st.number_input("Month", value=current_month)

with day_col:
    selected_day=st.number_input("Day", value=current_day)


# defining class section
class_col, class_incharge_col = st.columns(2)
with class_col:
    selected_class=st.selectbox("Class", placeholder="Choose student class", options=school_classes)
    # creating selected class dataframe for later use
    selected_class_df=df[df[df_class_col]==selected_class]

with class_incharge_col:
    # getting the last class incharge name using the selected class
    selected_class_incharge=list(selected_class_df[df_class_incharge_col])[-1]
    # Just doing the formatting of the class incharge value
    st.write("")
    st.write("")
    st.write(f":blue[Incharge:] {selected_class_incharge}")


# defining student section
# getting class recent incharge name
selected_class_students=list(selected_class_df[df_stud_guar_name_col].unique())
# displaying widget
selected_student=st.selectbox("Student Name - Guardian Name", placeholder="Choose student name.", options=selected_class_students)


# discipline parameters UI
present_options=["", "yes", "no"]
discipline_options=["", "yes", "no", "absent"]
present_col, proper_uniform_col, on_time_col, punished_col=st.columns(4)
with present_col:
    stud_present_status=st.selectbox("Present?", placeholder="Select status.", options=present_options)

with proper_uniform_col:
    stud_pro_uni_status=st.selectbox("Proper Uniform?", placeholder="Select status.", options=discipline_options)

with on_time_col:
    stud_on_time_status=st.selectbox("On Time?", placeholder="Select status.", options=discipline_options)

with punished_col:
    stud_punished_status=st.selectbox("Punished?", placeholder="Select status.", options=discipline_options)


# test parameters UI
subj_col, teacher_col, total_marks_col, obtain_marks_col=st.columns(4)
with subj_col:
    # getting selected class subjects list
    selected_class_subjs=list(selected_class_df[df_subjects_col].unique())
    # displaying widget
    selected_test_subj=st.selectbox("Subject", placeholder="Chemistry", options=selected_class_subjs)
    st.caption("Whose test happened today.")

with teacher_col:
    # getting selected_test_subject_teacher
    selected_test_subj_teach=list(selected_class_df.loc[selected_class_df[df_subjects_col]==selected_test_subj, df_subj_teach_col])[-1]
    # displaying widget with proper formatting
    st.write("")
    st.write("")
    st.write(f":blue[Teacher:] {selected_test_subj_teach}")

with total_marks_col:
    selected_test_subj_t_marks=st.number_input("Total Marks", placeholder="50", help="Total marks of the test.", format="%f")

with obtain_marks_col:
    selected_test_subj_o_marks=st.number_input("Obtained Marks", placeholder="48", help="Obtained marks from the test.", format="%f")


# submit button
submit_btn=st.button("Submit", type="primary", use_container_width=True)



############################################# Student Daily Data Saving (upon pressing the submit button)
# checking if the any entry is null
cond_1=(selected_year=="")
cond_2=(selected_month=="")
cond_3=(selected_day=="")
cond_4=(selected_class=="")
cond_5=(selected_student=="")
cond_6=(stud_present_status=="")
cond_7=(stud_on_time_status=="")
cond_8=(stud_pro_uni_status=="")
cond_9=(stud_punished_status=="")
cond_10=(selected_test_subj=="")
cond_11=(selected_test_subj_t_marks=="")
cond_12=(selected_test_subj_o_marks=="")

if submit_btn:
    # preparing row to append
    student_name, relation, guardian_name, gender = list(((selected_class_df.loc[selected_class_df[df_stud_guar_name_col] == selected_student, [df_student_name_col, df_relation_col, df_guardian_name_col, df_student_gender_col]]).tail(1).values)[0])
    clas, section=selected_class.split(" ")
    
    row_to_append=[selected_year, selected_month, selected_day, clas, section, selected_class_incharge, student_name, guardian_name, relation, gender, stud_present_status, stud_on_time_status, stud_pro_uni_status, stud_punished_status, "", selected_test_subj, selected_test_subj_teach, selected_test_subj_t_marks, selected_test_subj_o_marks]
    # condition checking same entry
    # converting row to dataframe
    # row_df = pd.DataFrame([row_to_append], columns=df.columns[:19])
    # Check if the row_df is present in the DataFrame df
    # same_row_exists = (df.iloc[:, :19] == row_df.iloc[0]).all(axis=1).any()
    
    # if anything is null
    if cond_1 or cond_2 or cond_3 or cond_4 or cond_5 or cond_6 or cond_7 or cond_8 or cond_9 or cond_10 or cond_11 or cond_12:
        st.error("Please enter all fields.")
    # if obtained marks are greater than total
    elif(selected_test_subj_o_marks > selected_test_subj_t_marks):
        st.error("Obtained marks are greater than total marks.")
    # if the same entry already exists
    # elif(same_row_exists):
        # st.error("Same details already exist. Try updating date or update details using the update records tab.")

    else:
        st.write("Everything is fine.")
        with st.spinner("Adding record.."):
            response=append_new_row(row_to_append)

            # checking for the appending response
            if response==0:
                st.success("Record added.")
            else:
                st.error("An error occured. Pleases refresh the page and try again.")




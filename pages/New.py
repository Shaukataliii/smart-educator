# We are using specified number of columns from the dataframe using list/dataframe slicing technique, for the purpose of checking duplicate row. If number of columns are changed, then we'll need to adjust that.

import streamlit as st
import gspread as gs
import pandas as pd
import numpy as np
from oauth2client.service_account import ServiceAccountCredentials
import datetime
from time import time

# setting page configurations
st.set_page_config("New Record", layout="wide", initial_sidebar_state="collapsed", page_icon="pencil")
st.title(":female-student: Add New Record")
st.caption("Enter new admissions details using this form.")
st.divider()


################################### Initial Variables and Functions
# worksheet related variables
# sheet10 is being loaded here which is containing exams-dataset
worksheet_name="dataset-main"
sheetname1="full-dataset"
sheetname2="financial-dataset"
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
    data=_sheet.get_all_records()
    print("Got all the records. Converting into DataFrame")
    
    # converting into pandas DataFrame
    data=pd.DataFrame(data)
    print("DataFrame prepared. Returning it.")
    return data

@st.cache_resource
def connect_with_worksheet(_worksheet_name):
    """Connects with the provided worksheet_name and returns the worksheet."""

    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds=ServiceAccountCredentials.from_json_keyfile_name(json_key_filename, scope)
    client=gs.authorize(creds)
    print("Connected")

    # Opens the spreadsheet specified
    spreadsheet=client.open(worksheet_name)
    print("Worksheet opened.")

    return spreadsheet

@st.cache_resource
def open_sheet1(_sheetname):
    """Connects with the worksheet, opens the given sheet and returns that."""

    # connecting with the sheet
    spreadsheet=connect_with_worksheet(worksheet_name)

    # Getting the specified sheet
    sheet=spreadsheet.worksheet(_sheetname)
    print(f"Got {_sheetname} sheet. Returning it")
    return sheet

@st.cache_resource
def open_sheet2(_sheetname):
    """Connects with the worksheet, opens the provided sheetname and returns that."""

    # connecting with the sheet
    spreadsheet=connect_with_worksheet(worksheet_name)

    # Getting the specified sheet
    sheet=spreadsheet.worksheet(_sheetname)
    print(f"Got {_sheetname} sheet. Returning it")
    return sheet

def append_new_row(sheetname, row):
    """Gets the cached sheet by calling open_sheet() and tries to append the new row. If success then return 0 else returns 1."""
    print("Getting sheet for appending new row.")
    
    # opening the provided sheetname
    if sheetname==sheetname1:
        start_time=time()
        sheet=open_sheet1(sheetname)
    elif sheetname==sheetname2:
        start_time=time()
        sheet=open_sheet2(sheetname)
    else:
        print("Provided sheetname is not sheetname1 or sheetname2. Execution stopped.")
        st.stop()
    
    print(f"Got {sheet}. Appending row into it.")

    try:
        sheet.append_row(values=row)

        end_time=time()
        time_to_append=(end_time-start_time)

        print(f"Appended. Time taken: {time_to_append}")
        return 0
    
    except Exception as err:
        end_time=time()
        time_to_append=(end_time-start_time)

        print(f"Appending failed. Time taken: {time_to_append} {err}")
        return 1



################################## preparing data
# Opening sheet and creating dataframe
main_df_sheet=open_sheet1(sheetname1)
finance_df_sheet=open_sheet2(sheetname2)

# loading the main dataset
df=load_df(main_df_sheet)



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
#---------- New admission section -----------
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
stud_name_col, stud_guardian_col, guardian_relation_col=st.columns(3)
guardian_relation_options=["", "son of", "daughter of", "Other"]
with stud_name_col:
    entered_stud_name=st.text_input("Student Name", placeholder="Enter student name.")

with stud_guardian_col:
    entered_guardian_name=st.text_input("Guardian Name", placeholder="Enter guardian name")

with guardian_relation_col:
    entered_guardian_relation=st.selectbox("Relation with guardian", placeholder="Select student relation with guardian", options=guardian_relation_options)


# defining student personal data and fee
stud_gender_col, stud_age_col, stud_fee_col=st.columns(3)
stud_gender_options=["", "Male", "Female"]
with stud_gender_col:
    entered_stud_gender=st.selectbox("Gender", placeholder="Select student gender", options=stud_gender_options)

with stud_age_col:
    entered_stud_age=st.number_input("Age", placeholder="13", format="%f")

with stud_fee_col:
    entered_stud_fee=st.number_input("Fee", placeholder="3000", format="%f")


# submit button
submit_btn=st.button("Complete Admission", type="primary", use_container_width=True)



############################################# Student Admission Data Saving (upon pressing the submit button)
# checking if the any entry is null
cond_1=(selected_year=="")
cond_2=(selected_month=="")
cond_3=(selected_day=="")
cond_4=(selected_class=="")
cond_5=(entered_stud_name=="")
cond_6=(entered_guardian_name=="")
cond_7=(entered_guardian_relation=="")
cond_8=(entered_stud_gender=="")
cond_9=(entered_stud_age==0)
cond_10=(entered_stud_fee==0)

if submit_btn:
    # if anything is null
    if cond_1 or cond_2 or cond_3 or cond_4 or cond_5 or cond_6 or cond_7 or cond_8 or cond_9 or cond_10:
        st.error("Please enter all fields.")
    
    else:
        # preparing row to append
        clas, section=selected_class.split(" ")
        stud_guardian=(f"{entered_stud_name} {entered_guardian_relation} {entered_guardian_name}")
        
        row_to_append_in_1=[selected_year, selected_month, selected_day, clas, section, selected_class_incharge, entered_stud_name, entered_guardian_name, entered_guardian_relation, entered_stud_gender, "", "", "", "", "", "", "", "", "", "",  selected_class, stud_guardian]

        row_to_append_in_2=[selected_year, selected_month, stud_guardian, selected_class, "yes", entered_stud_fee]
        # condition checking same entry for row 1
        # JUST UNCOMMENT THE FOLLOWING 4 LINES TO ADD DUPLICATE ROW CHECKING SYSTEM
        # # converting row to dataframe
        # row_df = pd.DataFrame([row_to_append_in_1], columns=df.columns[:22])
        # # Check if the row_df is present in the DataFrame df
        # same_row_exists = (df.iloc[:, :22] == row_df.iloc[0]).all(axis=1).any()

        same_row_exists=False
        
        # if the same entry already exists
        if(same_row_exists):
            # st.error("Same details already exist in main dataset. Try updating date or update details using the update records tab.")
            print("Same row exists")

        else:
            st.write("Everything is fine.")
            with st.spinner("Adding record.."):
                # appending data to main sheet (sheetname1)
                response1=append_new_row(sheetname1, row_to_append_in_1)

                # appending data to main sheet (sheetname1)
                response2=append_new_row(sheetname2, row_to_append_in_2)

                # checking for the appending response
                if response1==0 and response2==0:
                    st.success("Both records added.")
                elif response1==0 and response2==1:
                    st.success("1st record added only.")
                elif response1==1 and response2==0:
                    st.success("2nd record added only.")
                else:
                    st.error("An error occured. Pleases refresh the page and try again.")


#---------- Update record section -----------
# Will be added on demand.
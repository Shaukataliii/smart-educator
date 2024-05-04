import streamlit as st
import gspread as gs
import pandas as pd
import numpy as np
from oauth2client.service_account import ServiceAccountCredentials
import datetime
from time import time
import matplotlib.pyplot as plt
import seaborn as sns

# setting page configurations
st.set_page_config("Dashboard", layout="wide", initial_sidebar_state="collapsed", page_icon="bar_chart")
# st.title(":bar_chart: Al-Madina-Dashboard")
# st.caption("Analyze how the shcool is performing over time.")
# st.divider()


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
# financial dataframe vars
fdf_fee_col="fee"
fdf_paid_col="paid"

# main-dataset dataframe vars
df_present_col="present"
df_test_pert_col="percentage"
df_punished_col="punished"
df_properuni_col="proper_uniform"
df_ontime_col="on_time"
df_teacher_col="subject_teacher"


# vars with same column namems in both sheets
stud_grau_name_col="student_guardian"
class_section_col="class_with_section"
year_col="year"
month_col="month"
day_col="day"


# functions
@st.cache_data
def load_df1(_sheet):
    """Loads all the previous records from the provided sheet, converts them into pandas dataframe and returns that dataframe."""
    data=_sheet.get_all_records()
    print("Got all the records. Converting into DataFrame")
    
    # converting into pandas DataFrame
    data=pd.DataFrame(data)
    print("DataFrame prepared. Returning it.")
    return data

@st.cache_data
def load_df2(_sheet):
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

@st.cache_data
def get_classes(_df):
    """Retrieves unique classes from the dataframe and returns them as list."""

    print("Getting unique school classes as list..")
    school_classes=list(_df[class_section_col].unique())
    print("Got classes as list. Returning them.")
    return school_classes

def perform_label_encoding(df, required_cols):
    """Performs label encoding on the provided columnnames of the provided dataframe so as to convert yes to 1, no to 0, 1 to 1, -1 to 0 and 0 to 0. Returns the dataframe after processing."""
    print("Performing label encoding on the dataset.")

    for col in required_cols:
        df[col]=df[col].map({"yes":1, "no":0, "absent": -1, 1:1, 0:0, -1:0})

    print("Done. Returning it.")
    return df

def generate_palette(series= "color", palette: str="pastel"):
    "Takes a series (optional) and a palette (optional) and generates palette with colors equal to length of the series and return it. By default number of color is 5 and palette is pastel."
    palette=sns.color_palette(palette, len(series))
    return palette


################################## preparing data
# Opening sheet and creating dataframe
main_df_sheet=open_sheet1(sheetname1)
finance_df_sheet=open_sheet2(sheetname2)

# loading the main dataset
df=load_df1(main_df_sheet)
fdf=load_df2(finance_df_sheet)

# performing encoding on the main-dataset
required_columns=[df_present_col, df_punished_col, df_ontime_col, df_properuni_col]
df=perform_label_encoding(df, required_columns)

# creating variables to use while data entry e.g. classes, class students etc.
school_classes=get_classes(df)



################################## Creating UI (along with required computations)
# variable to show duration
duration_label=""

ui_year_col, ui_month_col, ui_day_col, ui_class_col, ui_stud_name_col=st.columns(5)
with ui_year_col:
    entered_year=st.number_input("Year", value=2024, help="Enter the year for which you want to see results.")

with ui_month_col:
    entered_month=st.number_input("Month", value=4, max_value=12, help="Enter the month for which you want to see results.")

with ui_day_col:
    entered_day=st.number_input("Day", value=3, max_value=31, help="Enter the day for which you want to see results.")

with ui_class_col:
    selected_class=st.selectbox("Class", options=school_classes)
    # creating selected class dataframe
    selected_class_df=df[df[class_section_col]==selected_class]

with ui_stud_name_col:
    # getting unique students of the class (using student_guardian name)
    selected_class_students=selected_class_df[stud_grau_name_col].unique()
    # displaying widget
    selected_student=st.selectbox("Student", options=selected_class_students)



# financial figures for current year and month
ttl_studs_col, fee_c_col, fee_r_col=st.columns(3)
with ttl_studs_col:
    # joining student_guardian column with class_with_section_column.
    fdf["fdf_stud_guar_cls_sec_col"]=fdf[stud_grau_name_col] + " " + [class_section_col]
    schl_t_studs=len(fdf[(fdf[year_col]==current_year)]["fdf_stud_guar_cls_sec_col"].unique())
    
    st.write(f"Total Students: :blue[{schl_t_studs}]")

with fee_c_col:
    # getting the sum of fee where paid(yes/no) is yes for current year and month.
    fee_c_current_month=fdf[(fdf[year_col]==current_year) & (fdf[month_col]==current_month) & (fdf[fdf_paid_col]=="yes")]["fee"].sum()
    # displaying widget.
    st.write(f"Collected Fee: :blue[{fee_c_current_month}]")

with fee_r_col:
    # getting the sum of fee where paid(yes/no) is no (indicating fee is not paid yet) for current year and month.
    fee_r_current_month=fdf[(fdf[year_col]==current_year) & (fdf[month_col]==current_month) & (fdf[fdf_paid_col]=="no")]["fee"].sum()
    # displaying widget.
    st.write(f"Remaining Fee: :blue[{fee_r_current_month}]")


# class based perofrmance

# displaying number of students in each class during specified duration (day)
# getting count of students for the specifed day (for each class)
df_entered_month=df[(df[year_col]==entered_year) & (df[month_col]==entered_month)]
df_entered_day=df[(df[year_col]==entered_year) & (df[month_col]==entered_month) & (df[day_col]==entered_day)]

# getting the class counts
class_counts=df_entered_day.groupby(class_section_col).size().reset_index(name="no_of_students")
    
# displaying widget
# st.write(class_counts)    # can uncomment for testing.
try:
    width=20
    height=3
    fig, ax = plt.subplots(figsize=(width, height))
    class_counts.plot.bar(x=class_section_col, y='no_of_students', ax=ax, color=generate_palette(class_counts))
    ax.set_xlabel('Class')
    ax.set_ylabel('Number of Students')
    ax.set_title(f"No. of students in each class on {entered_day}-{entered_month}-{entered_year}")
    st.pyplot(fig)
except:
    st.subheader(":red[No Data to Display]")


# creating columns and displaying results
cls_perf_col1, cls_perf_col2=st.columns(2)

#### graphs based on day
# displaying attendance % of each class for the specified day
with cls_perf_col1:
    # getting count of students for the specifed day (for each class)
    class_att_pert=df_entered_day.groupby(class_section_col)[df_present_col].mean().reset_index(name="class_att_%")
    class_att_pert["class_att_%"] *= 100
    
    # displaying widget
    # st.write(class_att_pert)    # can uncomment for testing.
    try:
        width=10
        height=5
        fig, ax = plt.subplots(figsize=(width, height))
        class_att_pert.plot.bar(x=class_section_col, y="class_att_%", ax=ax, color=generate_palette(class_att_pert, palette="rocket_r"))
        
        # Set y-axis ticks to 20, 40, 60, 80, 100
        ax.set_yticks([0, 20, 40, 60, 80, 100])
        # ax.set_xticks(class_att_pert.index)
        ax.set_xlabel('Class')
        ax.set_ylabel('Attendance %')
        ax.set_title(f"Attendance % of each class on {entered_day}-{entered_month}-{entered_year}")
        st.pyplot(fig)

    except:
        st.subheader(":red[No Data to Display]")

# displaying total test results % on specified day
with cls_perf_col2:
    # getting mean test % of students of each class for the specifed day (for each class)  
    class_test_pert=df_entered_day.groupby(class_section_col)[df_test_pert_col].mean().reset_index(name="class_test_%")
    
    # transforming 0-1 to 0-100
    class_test_pert["class_test_%"] *= 100
    
    # displaying widget
    # st.write(class_att_pert)    # can uncomment for testing.
    try:
        width=10
        height=5
        fig, ax = plt.subplots(figsize=(width, height))
        class_test_pert.plot.bar(x=class_section_col, y="class_test_%", ax=ax, color=generate_palette(class_test_pert, palette="rocket_r"))
        
        # Set y-axis ticks to 20, 40, 60, 80, 100
        pert_ytick_labels=[0, 20, 40, 60, 80, 100]
        ax.set_yticks(pert_ytick_labels)
        ax.set_xlabel('Class')
        ax.set_ylabel('Test Obtained Marks %')
        ax.set_title(f"Test results % of each class {entered_day}-{entered_month}-{entered_year}")
        st.pyplot(fig)
    except:
        st.subheader(":red[No Data to Display]")


#### graphs based on month
# displaying specified class specified month attendance %
with cls_perf_col1:
    # getting the mean of specified class every day attendance
    selected_month_class_att_pert=df_entered_month[(df_entered_month[class_section_col]==selected_class)].groupby(day_col)[df_present_col].mean()
    # transforming the percentage between 0 to 100
    selected_month_class_att_pert *= 100

    # displaying widget
    try:
        fig, ax=plt.subplots(figsize=(width, height))
        selected_month_class_att_pert.plot.area(x=day_col, y=selected_month_class_att_pert.index, ax=ax, color=generate_palette(palette="husl"))

        # setting labels
        ax.set_xlabel("Day")
        ax.set_ylabel("Attendance %")
        ax.set_title(f"Attendance % of {selected_class} in {entered_month}-{entered_year}")
        st.pyplot(fig)

    except Exception as err:
        st.write(err)
        st.subheader(":red[No Data to display]")

# displaying speficied class specified month test %
with cls_perf_col2:
    # getting the mean of specified class every day test performance
    selected_month_class_test_pert=df_entered_month[(df_entered_month[class_section_col]==selected_class)].groupby(day_col)[df_test_pert_col].mean()
    # transforming the percentage between 0 to 100
    selected_month_class_test_pert *= 100

    # displaying widget
    try:
        fig, ax=plt.subplots(figsize=(width, height))
        selected_month_class_test_pert.plot.area(x=day_col, y=selected_month_class_test_pert.index, ax=ax, color=generate_palette(palette="coolwarm"))

        # setting labels
        ax.set_xlabel("Day")
        ax.set_ylabel("Test Result %")
        ax.set_title(f"Test Result % of {selected_class} in {entered_month}-{entered_year}")
        st.pyplot(fig)

    except Exception as err:
        st.subheader(":red[No Data to display]")

# displaying each teacher no. of tests taken in specified month and class
with cls_perf_col1:
    # getting count of entreis of each teacher in spec class in spec month
    no_tests_by_teacher_selected_cls=df_entered_month[(df_entered_month[class_section_col]==selected_class)].groupby(df_teacher_col)[stud_grau_name_col].count()
    # number of students in the specified class
    no_studs_selected_cls=df_entered_day[(df_entered_day[class_section_col]==selected_class)][stud_grau_name_col].count()
    # dividing count by number of class students to get the number of tests
    no_tests_by_teacher_selected_cls /= no_studs_selected_cls
    # specifying tests count for yticklabels
    no_tests=[0,2,4,6,8,10]
    
    # displaying widget
    try:
        fig, ax=plt.subplots(figsize=(width, height))
        no_tests_by_teacher_selected_cls.plot.bar(x=df_teacher_col, ax=ax, color=generate_palette(series=no_tests_by_teacher_selected_cls, palette="coolwarm"))

        # setting labels
        ax.set_yticklabels(no_tests)
        ax.set_xlabel("Teacher Name")
        ax.set_ylabel("# Tests Taken")
        ax.set_title(f"No. of Tests Taken by each teacher in {selected_class} in {entered_month}-{entered_year}.")
        st.pyplot(fig)

    except Exception as err:
        st.subheader(":red[No Data to display]")

# displaying each teacher tests results % taken in specified month and class
with cls_perf_col2:
    # getting count of entreis of each teacher in spec class in spec month
    tests_rslts_pert_by_teacher_selected_cls=df_entered_month[(df_entered_month[class_section_col]==selected_class)].groupby(df_teacher_col)[df_test_pert_col].mean()
    # number of students in the specified class on the entered day
    no_studs_selected_cls=df_entered_day[(df_entered_day[class_section_col]==selected_class)][stud_grau_name_col].count()
    # dividing percentage by number of class students to get the right results percentage
    tests_rslts_pert_by_teacher_selected_cls /= no_studs_selected_cls
    
    # displaying widget
    try:
        fig, ax=plt.subplots(figsize=(width, height))
        tests_rslts_pert_by_teacher_selected_cls.plot.bar(x=df_teacher_col, ax=ax, color=generate_palette(series=tests_rslts_pert_by_teacher_selected_cls, palette="coolwarm"))

        # setting labels
        ax.set_yticklabels(pert_ytick_labels)
        ax.set_xlabel("Teacher Name")
        ax.set_ylabel("Tests Result %")
        ax.set_title(f"Tests Results % of each teacher in {selected_class} in {entered_month}-{entered_year}.")
        st.pyplot(fig)

    except Exception as err:
        st.subheader(":red[No Data to display]")


#### graphs based on year
# displaying no of classes each teacher has taken in specified  year
with cls_perf_col1:
    # getting count of entries of each teacher in spec year
    entries_each_teacher_selected_year=df[(df[year_col]==entered_year)].groupby(df_teacher_col)[stud_grau_name_col].count()
    # number of students of the school on current day (using entered day to get recent results)
    studs_count_curr_day=df_entered_month[(df_entered_month[day_col]==current_day)].groupby(class_section_col)[stud_grau_name_col].size().reset_index(drop=True).sum()
    clses_each_teacher_taken_entered_year=entries_each_teacher_selected_year / studs_count_curr_day

    # displaying widget
    try:
        fig, ax=plt.subplots(figsize=(width, height))
        clses_each_teacher_taken_entered_year.plot.bar(ax=ax, color=generate_palette(series=clses_each_teacher_taken_entered_year, palette="cubehelix_r"))

        # setting labels
        # x=df_teacher_col, 
        # ax.set_yticklabels(pert_ytick_labels)
        ax.set_xlabel("Teacher Name")
        ax.set_ylabel(f"No. of classes in {entered_year}")
        ax.set_title(f"No. of classes taken by each teacher in {entered_year}.")
        st.pyplot(fig)

    except Exception as err:
        st.subheader(":red[No Data to display]")

# displaying discipline performance of specified student in specified month or year (based on the value of entered_month)
with cls_perf_col2:
    if (entered_month==0):
        # getting average of discipline params for the specified month of selected student
        selected_stud_dis_perf_in_selected_duration=df[(df[year_col]==entered_year) & (df[class_section_col]==selected_class) & (df[stud_grau_name_col]==selected_student)][[df_present_col, df_ontime_col, df_properuni_col, df_punished_col]].agg("mean", axis=0)
        duration=f"{entered_year}"

    else:
        # getting average of discipline params for the specified month of selected student
        selected_stud_dis_perf_in_selected_duration=df_entered_month[(df_entered_month[class_section_col]==selected_class) & (df_entered_month[stud_grau_name_col]==selected_student)][[df_present_col, df_ontime_col, df_properuni_col, df_punished_col]].agg("mean", axis=0)
        duration=f"{entered_month}-{entered_year}"

    # transforming into percentage
    selected_stud_dis_perf_in_selected_duration *= 100

    # displaying widget
    try:
        fig, ax=plt.subplots(figsize=(width,height))
        selected_stud_dis_perf_in_selected_duration.plot.bar(ax=ax, color=generate_palette(selected_stud_dis_perf_in_selected_duration, palette="cubehelix_r"))

        # setting labels
        ax.set_xlabel("Discipline Parameters")
        ax.set_ylabel("Performance in %")
        ax.set_title(f"{selected_student} discipline % in {duration}")
        st.pyplot(fig)

    except Exception as err:
        st.write(err)
        st.subheader(":red[No Data to Display]")


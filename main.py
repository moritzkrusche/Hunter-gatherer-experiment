#*********************************************************************************************************************
# Stone Age hunter-gatherer experiment V 1.0

# Originally submitted as "Programming for Cognitive Science Assignment 3" at University College London, 6 March 2017

# This programme is an exploration vs exploitation dilemma that takes place on three different levels
# The participant controls a figure that can move around different resource patches; these are on 2X2, 3X3, 4X4
# grid respectively (levels 1-3)

# With a limited amount of movements, the participant has to make careful choices as to whether exploit
#  current resources, or explore new ones. Every resource patch has an underlying probability function that
#  is probed when resources are gathered

# There are 3 conditions that result in different parameters for these probability functions.
# Conditions are assigned automatically to ensure equal numbers across
# Conditions 2 and 3 have higher variability in payoffs, and also contain a depreciation parameter that will
# lower subsequent payoff every time a resource patch is exploited, however mean payoff is slightly higher

# As an experiment, the main interest would be how people switch between patches, and which cognitive models can
# best approximate their behaviour. To allow for this, every single action (not just averages) that the participant
# takes is logged and written to the results file

# If you want to test the programme, put testing_programme around line 60 to True. This will reveal a button that
# allows you to skip through game levels. Also set the page index to 3 if you want to start with the experiment
# For actually testing participants it may be beneficial to not print group assignment around line 110 and depreciation
# around line 630, at least if they can see the console, but I feel that for assessing this programme, these print
# statements are highly informative

# NOTE: The UI has been developed on MAC OS X and while the font and box sizes were adjusted for use on Windows, this
# could not be tested extensively, and they may still need further adjustment

# What is unique about this particular implementation is the detailed UI, conciseness of the code
# as well as the challenging gameplay; because life in the stone ages is very hard, participants must take great care
# not to get negative scores (starvation) or be eaten by predators. Note: being eaten always resets the score to zero.

#*********************************************************************************************************************
# Initialising the UI & import & some settings

#!../opt/local/bin/pythonw
#-*- coding:utf-8 -*-

# Import modules and one one other .py page with text that is added to the UI at some stages

import os
import random
import sys
import time

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import specs
from stone_age import *

# print at least something? Might be useful, if the UI crashes for some other software reason
print('Application started')
# this is the name of the .csv file, where the results are stored
results_file = 'exp_results.csv'
feedback_file = 'exp_feedback.txt'

# Initialising the UI
app = QApplication(sys.argv)
window = QMainWindow()
ui = Ui_window_all_pages()
ui.setupUi(window)

# If set to True, it reveals a "Skip" or an "EAT ME" button on every page or level, that allows for skipping
#  through the programme..
testing_programme = True
# These settings govern by how much paramaters are modified in a multimodal distribution (-mean, + sd)
mod_mean = 5
mod_sd = 15
# Determines likelihood of multimodal distribution and being eaten on a deer patch. Random int between 0 and these
prob_multi = 2
prob_tiger = 9
# How many multiples of the standard no of turns there are per level; also affects depreciation and payoff
turns_mod = 2

# Always start testing with 0 at the consent page; or set to 2 to debug the experiment
ui.all_pages.setCurrentIndex(0)
current_lvl = str(ui.all_pages.currentIndex() - 2)

def update_lvl():

    global current_lvl
    current_lvl = str(ui.all_pages.currentIndex() - 2)

#*********************************************************************************************************************
# Determine the condition, and retrieving the appropriate payoffs
# Condition is determined randomly only in the first experimental run; on later runs, it is chosen based on which
# previous condition in the results .csv file is least common
if os.path.isfile(results_file):
    file = open(results_file, 'r')
    lines = file.readlines()[1:]
    groups_so_far = []
    for line in lines:
        split_lines = line.split(",")
        groups_so_far.append(split_lines[0])
    no_grp1 = groups_so_far.count("1")
    no_grp2 = groups_so_far.count("2")
    no_grp3 = groups_so_far.count("3")

# assign group based on least common in results .csv file
def get_group():

    try:
        if no_grp1 >= no_grp2 > no_grp3 or no_grp2 >= no_grp1 > no_grp3:
            next_group = 3
        elif no_grp3 >= no_grp1 > no_grp2 or no_grp1 >= no_grp3 > no_grp2:
            next_group = 2
        elif no_grp3 >= no_grp2 > no_grp1 or no_grp3 >= no_grp2 > no_grp1:
            next_group = 1
        else:
            next_group = random.randint(1, 3)
    except:
        next_group = random.randint(1, 3)
    return next_group

group = get_group()
print("GROUP:", group)

# These settings determine by how much a resource patch is going to be depreciated every time it is used. This will
# vary between groups. Modifier of mean expected payoff compensate for this, by generically multiplying or adding
#  to the payoff generated to the distribution
def difficulty(group):

    if group == 1:
        return 0, 1, 1
    elif group == 2:
        return 0.8, 1, 3
    elif group == 3:
        return 1.6, 1.1, 5

depreciator = difficulty(group)[0] / turns_mod
difficulty_multi = difficulty(group)[1] / turns_mod
difficulty_add = difficulty(group)[2] / turns_mod

# 3 levels in total; 3 different maps in designer, but could replay with code
levels = ["1", "2", "3"]

# How many turns there are per level. Feel free to increase or decrease. For valid results, it should be at least 2x
# this amount, by setting turns_mod to 2, but that might make testing the programme annoying...
turns_lvl1 = 20 * turns_mod
turns_lvl2 = 45 * turns_mod
turns_lvl3 = 80 * turns_mod
turns_list = [turns_lvl1, turns_lvl2, turns_lvl3]

# Score set to 0 at start; might also be anything else
score = 0

patches_lvl1 = specs.payoff_patches[group-1][0]
patches_lvl2 = specs.payoff_patches[group-1][1]
patches_lvl3 = specs.payoff_patches[group-1][2]
patches_lvl= {"1": patches_lvl1, "2": patches_lvl2, "3": patches_lvl3}

#*********************************************************************************************************************
# Setting up the UI and hiding all sorts of menus and events

# For every level there is a distinct ui element, and these dictionaries allow for looping over them
# Not as nice & concise as exec/eval, but much faster and generally better code

# The demo boxes dictionaries makes some functions shorter in code, because it is looped over during check
# the 1 values are mandatory and when 'student' is checked, all values are set to 1
demo_boxes_error = {ui.demo_error_vision:1, ui.demo_error_handedness:1, ui.demo_error_edu:1, ui.demo_error_student:1,
                    ui.demo_error_subject:0, ui.demo_error_year:0}

demo_boxes_box = {ui.demo_error_vision: ui.demo_box_vision, ui.demo_error_handedness: ui.demo_box_handedness,
                  ui.demo_error_edu: ui.demo_box_edu, ui.demo_error_student: ui.demo_box_student, ui.demo_error_subject:
                      ui.demo_box_subject, ui.demo_error_year: ui.demo_box_year}

# these widgets govern the "eaten" event
eaten_widgets = {"1": [ui.lvl1_eaten1, ui.lvl1_eaten2, ui.lvl1_eaten_box, ui.lvl1_eaten_patch], "2":
    [ui.lvl2_eaten1, ui.lvl2_eaten2, ui.lvl2_eaten_box, ui.lvl2_eaten_patch], "3":
    [ui.lvl3_eaten1, ui.lvl3_eaten2, ui.lvl3_eaten_box, ui.lvl3_eaten_patch]}

# buttons that are hidden to prevent illegal moves
directions_widgets = {"1": [ui.lvl1_move_left, ui.lvl1_move_right, ui.lvl1_move_up, ui.lvl1_move_down], "2":
    [ui.lvl2_move_left, ui.lvl2_move_right, ui.lvl2_move_up, ui.lvl2_move_down], "3":
    [ui.lvl3_move_left, ui.lvl3_move_right, ui.lvl3_move_up, ui.lvl3_move_down]}

#  animations of good and rotten apples to indicate payoff quality
payoff_widgets = {"1": [ui.lvl1_good_payoff, ui.lvl1_bad_payoff], "2":[ui.lvl2_good_payoff, ui.lvl2_bad_payoff], "3":
    [ui.lvl3_good_payoff, ui.lvl3_bad_payoff]}

# the sabre tooth tigre that is moved onto the player position
eaten_patch = {"1": ui.lvl1_eaten_patch, "2": ui.lvl2_eaten_patch, "3": ui.lvl3_eaten_patch}

# These are the numbers shown in the UI of the player score, turns, and payoff
score_widget_no = {"1": ui.lvl1_score_no, "2": ui.lvl2_score_no, "3": ui.lvl3_score_no}

score_widget_text = {"1": ui.lvl1_score_text, "2": ui.lvl2_score_text, "3": ui.lvl3_score_text}

turns_widget_no = {"1": ui.lvl1_turns_no, "2": ui.lvl2_turns_no, "3": ui.lvl3_turns_no}

results_widget_text = {"1": ui.lvl1_result_text, "2": ui.lvl2_result_text, "3": ui.lvl3_result_text}

results_widget_no = {"1": ui.lvl1_result_no, "2": ui.lvl2_result_no, "3": ui.lvl3_result_no}


# Setting up UI according to coded turns per level and starter score...
for level in levels:

    turns_this_lvl = turns_list[int(level)-1]

    turns_widget_no[level].setText(str(turns_this_lvl))
    score_widget_no[level].setText(str(score))
    results_widget_text[level].setText('Food')


# hides "Skip" and Eat Me" buttons
if testing_programme == False:
    ui.lvl1_button_eatme.hide()
    ui.lvl2_button_eatme.hide()
    ui.lvl3_button_eatme.hide()
    ui.consent_button_skip.hide()
    ui.demo_button_skip.hide()
    ui.inst_button_skip.hide()

def hide_animation():

    for level in payoff_widgets:
        for widget in payoff_widgets[level]:
            widget.hide()


hide_animation()

# This function hides various boxes that contain error messages if fields in the form are left out. It is called again,
# once the 'submit' button is clicked
def hide_boxes():

    ui.demo_error_ppt.hide()
    ui.demo_error_gender.hide()
    ui.demo_error_age.hide()
    ui.demo_error_global.hide()
    for error in demo_boxes_error:
        error.hide()

hide_boxes()

# hides optional boxes on the demographics page
ui.demo_widget_subject.hide()
ui.demo_widget_year.hide()

# on the consent page
ui.consent_message_quit.hide()
ui.consent_button_submit.hide()

# on the instructions page
ui.inst_button_confirm.hide()


# and on the experimental pages
def hide_eaten():

    for level in eaten_widgets:
        for widget in eaten_widgets[level]:
            widget.hide()


hide_eaten()


# resets UI when the gatherer is at the cave position
def reset_cave():

    if current_lvl in levels:

        results_widget_text[current_lvl].hide()
        results_widget_no[current_lvl].hide()

        for button in directions_widgets[current_lvl]:
            button.hide()

        # show move_down button, as this is the only legal move out of the cave
        directions_widgets[current_lvl][3].show()

reset_cave()

#*********************************************************************************************************************
# Setting up various dictionaries that keep track of participant actions

# the dictionary keys represents levels 1-3; access is easier in int format
score_tracker = {1: 0, 2: 0, 3: 0}
moves_tracker = {1: 0, 2: 0, 3: 0}
eaten_tracker = {1: 0, 2: 0, 3: 0}

# Here, the dictionary keys represent patches numbered from 0(cave), to 4 (level1), 9 (level2), until 16 (level3)
# patches_tracker logs + 1 whenever a patch is exploited, payoff_tracker adds the payoff of one particular patch
# on one particular level
patches_tracker_lvl1 = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}
payoff_tracker_lvl1 = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}

patches_tracker_lvl2 = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0}
payoff_tracker_lvl2 = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0}

patches_tracker_lvl3 = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0, 14: 0,
                       15: 0, 16: 0}
payoff_tracker_lvl3 = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0, 14: 0,
                       15: 0, 16: 0}

patches_trackers = {"1": patches_tracker_lvl1, "2": patches_tracker_lvl2, "3": patches_tracker_lvl3}
payoff_trackers = {"1": payoff_tracker_lvl1, "2": payoff_tracker_lvl2, "3": payoff_tracker_lvl3}

#*********************************************************************************************************************
# Setting up and updating variables that are manipulated through the UI (such as demographics)

# initialises variables for the forms
window.ppt_no = ui.demo_box_ppt.text()
window.ppt_age = ui.demo_box_age.value()
window.ppt_sex = ui.demo_box_gender.currentIndex()
window.ppt_vision = ui.demo_box_vision.currentIndex()
window.ppt_handedness = ui.demo_box_handedness.currentIndex()
window.ppt_edu = ui.demo_box_edu.currentIndex()
window.ppt_student = ui.demo_box_student.currentIndex()
window.ppt_subject = ui.demo_box_subject.currentIndex()
window.ppt_year = ui.demo_box_year.currentIndex()
window.ppt_feedback = ui.debrief_open_answer.text()


# Saves the information entered in the form in the variables
def update_ppt_no():
    window.ppt_no = ui.demo_box_ppt.text()
def update_age():
    window.ppt_age = ui.demo_box_age.value()
def update_sex():
    window.ppt_sex = ui.demo_box_gender.currentIndex()
def update_vision():
    window.ppt_vision = ui.demo_box_vision.currentIndex()
def update_handedness():
    window.ppt_handedness = ui.demo_box_handedness.currentIndex()
def update_edu():
    window.ppt_edu = ui.demo_box_edu.currentIndex()
def update_student():
    window.ppt_student = ui.demo_box_student.currentIndex()
def update_subject():
    window.ppt_subject = ui.demo_box_subject.currentIndex()
def update_year():
    window.ppt_year = ui.demo_box_year.currentIndex()
def update_feedback():
    window.ppt_feedback = ui.debrief_open_answer.text()

#*********************************************************************************************************************
# Main Functions that are not needed further up in code


# This function checks whether the demographics page has been filled in correctly
# Error messages are shown dynamically, depending on the missing information
def submitted():

    # checks if box 'student' is selected; if it is, 'subject' and 'year' have to be filled in as well
    if ui.demo_box_student.currentIndex() == 2:
        demo_boxes_error[ui.demo_error_subject] = 0
        demo_boxes_error[ui.demo_error_year] = 0
    else:
        demo_boxes_error[ui.demo_error_subject] = 1
        demo_boxes_error[ui.demo_error_year] = 1

    # checks whether the form is filled in completely
    def check_demo_error():

        check = False
        hide_boxes()

        # checking the comboboxes via the dictionary
        def check_demo_boxes_error():
            check_2 = True
            for error in demo_boxes_error:
                if not demo_boxes_error[error] == 0:
                    if demo_boxes_box[error].currentIndex() == 0:
                        error.show()
                        ui.demo_error_global.show()
                        check_2 = False
            return check_2

        # These error messages are more specific to the field not filled in correctly
        if ui.demo_box_ppt.text() == "":
            ui.demo_error_ppt.show()
            ui.demo_error_global.setText("Please provide your participant number!")
            ui.demo_error_global.show()
        elif ui.demo_box_gender.currentIndex() == 0:
            ui.demo_error_gender.show()
            ui.demo_error_global.setText("Please provide your gender!")
            ui.demo_error_global.show()
        elif ui.demo_box_age.value() == 0:
            ui.demo_error_age.show()
            ui.demo_error_global.setText("Please provide your correct age!")
            ui.demo_error_global.show()
        # Need to be at least 18 to participate, at the moment
        elif 18 > window.ppt_age:
            ui.demo_error_global.setText("You must be 18 years old in order to participate in this experiment!")
            ui.demo_error_global.move(540,470)
            ui.demo_error_global.show()
        # shows error message when not all combo-boxes are selected, else hides the error message again
        elif check_demo_boxes_error() == False:
            ui.demo_error_global.setText("Please complete all mandatory fields")
            ui.demo_error_global.show()
        else:
            ui.demo_error_global.hide()
            check = True
        return check
    # Move to next page if all is filled in correctly
    if check_demo_error() == True:
        ui.all_pages.setCurrentIndex(ui.all_pages.currentIndex() + 1)
    else:
        check_demo_error()

# If the student box is checked as yes, questions about the subject and year pop up; they are mandatory as long as
# 'student' remains checked
def show_student():

    if ui.demo_box_student.currentIndex() == 2:
        ui.demo_widget_subject.hide()
        ui.demo_widget_year.hide()
    else:
        ui.demo_widget_subject.show()
        ui.demo_widget_year.show()

# If consent is checked, the button for moving on is shown, if no consent checked, a quit dialogue is shown
def check_consent():

    if ui.consent_checkbox_yes.isChecked() == True:
        ui.consent_button_submit.show()
        ui.consent_message_quit.hide()
    elif ui.consent_checkbox_no.isChecked() == True:
        ui.consent_message_quit.show()
        ui.consent_button_submit.hide()

# Exits the programme if no consent
# Dirty Try / except to prevent an occasional SIGSEGV memory error in one of the libraries written in C
def terminate():
    try:
        window.close()
    except:
        time.sleep(5)
        terminate()

# Writes all results into a .csv file, if no such file exists, it creates one
def write_file():

    # sorting dictionaries for writing to file
    ppt_patches_lvl1 = sorted(patches_tracker_lvl1.items())
    ppt_patches_lvl2 = sorted(patches_tracker_lvl2.items())
    ppt_patches_lvl3 = sorted(patches_tracker_lvl3.items())
    ppt_payoff_lvl1 = sorted(payoff_tracker_lvl1.items())
    ppt_payoff_lvl2 = sorted(payoff_tracker_lvl2.items())
    ppt_payoff_lvl3 = sorted(payoff_tracker_lvl3.items())
    ppt_eaten_per_lvl = sorted(eaten_tracker.items())
    ppt_moves_per_lvl = sorted(moves_tracker.items())
    ppt_score_per_lvl = sorted(score_tracker.items())

    # retrieves last score from level 3
    ppt_score = int(ui.lvl3_score_no.text())

    # This demographic data is added for every participant in one line
    next_line = [group, window.ppt_no, ppt_score, window.ppt_age, window.ppt_sex, window.ppt_vision,
                 window.ppt_handedness, window.ppt_edu, window.ppt_student, window.ppt_subject, window.ppt_year]

    # These logs are added to every line. The patches log contains a detailed log of participants activities during
    # the task and is particularly useful for later cognitive modelling. Because so much data is written, it was
    # necessary to do a double for loop - every other solution did not produce good enough results.
    patches_log = [ppt_patches_lvl1, ppt_patches_lvl2, ppt_patches_lvl3, ppt_payoff_lvl1, ppt_payoff_lvl2,
                   ppt_payoff_lvl3]
    ppt_log = [ppt_eaten_per_lvl, ppt_moves_per_lvl, ppt_score_per_lvl]

    # This is the header of the results file, only created when first written
    # It was necessary to create this function due to the large amount of data collected, and specific file structure.
    def write_header(some_file):

        some_file.write("Condition, ID-Nr, Score, Age, Gender, Vision, Handedness, Education, Student, Subject, Year, ")

        for eaten in ppt_log[0]:
            some_file.write("Eaten Level" + str(eaten[0]) + ",")

        for move in ppt_log[1]:
            some_file.write("Moves Level" + str(move[0]) + ",")

        for score in ppt_log[2]:
            some_file.write("Score Level" + str(score[0]) + ",")

        for log in range (1, 4):

            for patch in patches_log[log - 1]:
                some_file.write("Patch" + str(patch[0]) + "/Level" + str(log) + ",")
            for payoff in patches_log[log + 2]:
                some_file.write("Payoff" + str(payoff[0]) + "/Level" + str(log) + ",")

        some_file.write("\n")

    if os.path.isfile(results_file):
        file = open(results_file, 'a')
    else:
        file = open(results_file, 'w')
        write_header(file)

    for item in next_line:
        file.write(str(item) + ",")

    for log in ppt_log:

        for item in log:
            file.write(str(item[1]) + ",")

    for log in range(1, 4):

        for item in patches_log[log - 1]:
            file.write(str(item[1]) + ",")
        for item in patches_log[log + 2]:
            file.write(str(item[1]) + ",")

    file.write("\n")
    file.close()
    print("results file has been created!")

# Terminates the programme and writes a separate feedback file, should participants wish to give any;
# this is so that any feedback given does not clutter up the main file that logs a lot of data...
def terminate_write_feedback():

    header = "This text file summarises all feedback typed by participants on the debriefing page\n"
    next_line = ["Participant ", window.ppt_no, " in group ", group, " gave this feedback: ", window.ppt_feedback]

    if os.path.isfile(feedback_file):
        file = open(feedback_file, 'a')
    else:
        file = open(feedback_file, 'w')
        file.write(header)
    for item in next_line:
        file.write(str(item))
    file.write("\n")
    file.close()
    print("feedback file has been created!")
    terminate()

# Move to next page
def next_page():

    ui.all_pages.setCurrentIndex(ui.all_pages.currentIndex() +1)
    update_lvl()
    # stopping timers after the last level & writing the results file.
    if current_lvl == "4":
        timer_bad.stop()
        timer_good.stop()
        write_file()
    if current_lvl in levels:
        reset_cave()

# Checks whether the box 'I read the instructions' is ticked, and reveals the button to proceed.
# If it is unticked, the button is hidden again
def check_inst():

    if ui.inst_checkbox.isChecked() == True:
        ui.inst_button_confirm.show()
    elif ui.inst_checkbox.isChecked() == False:
        ui.inst_button_confirm.hide()


# checks whether the gatherer is back in his cave after nightfall...
def check_eaten(some_turn):

    pos = get_pos()
    if some_turn <= 0:
        if pos[0] == 260 and pos[1] == 10:
            survived_next()
        else:
            eaten()

# Eaten event; shows menus and popups and resets score to zero, also logs being eaten
def eaten():

    eaten_tracker[int(current_lvl)] = 1
    score_widget_no[current_lvl].setText('0')
    pos = get_pos()

    for widget in eaten_widgets[current_lvl]:
        eaten_patch[current_lvl].move(pos[0], pos[1])
        widget.show()

# keeps the score, if the gatherer survived
def survived_next():

    survived_score = int(score_widget_no[current_lvl].text())
    score_tracker[int(current_lvl)] = survived_score
    hide_eaten()
    next_page()
    update_score(survived_score)
    reset_cave()

# next page if eaten; re-hides event for next level
def eaten_next():

    hide_eaten()
    next_page()
    reset_cave()

# acquiring the gatherers current position
def get_pos():
    if current_lvl == "1":
        char = ui.lvl1_widget_char
    elif current_lvl == "2":
        char = ui.lvl2_widget_char
    else:
        char = ui.lvl3_widget_char
    currentX = char.pos().x()
    currentY = char.pos().y()
    return currentX, currentY, char

# these functions govern movement of the gatherer in set directions by pushing the buttons
def move_right():
    pos = get_pos()
    char = pos[2]
    char.setGeometry(pos[0] + 110, pos[1], 100, 100)
    return move_restrictions()

def move_left():
    pos = get_pos()
    char = pos[2]
    char.setGeometry(pos[0] - 110, pos[1], 100, 100)
    return move_restrictions()

def move_up():
    pos = get_pos()
    char = pos[2]
    char.setGeometry(pos[0], pos[1] - 110, 100, 100)
    return move_restrictions()

def move_down():
    pos = get_pos()
    char = pos[2]
    char.setGeometry(pos[0], pos[1] + 110, 100, 100)
    return move_restrictions()

# this function dynamically hides arrow buttons depending on the current position and level,
#  logs moves and keeps track of how many are left before nightfall
def move_restrictions():

    moves_tracker[int(current_lvl)] += 1
    x = get_pos()[0]
    y = get_pos()[1]

    # current turn
    turn = int(turns_widget_no[current_lvl].text())
    # reduce by one in UI
    turns_widget_no[current_lvl].setText(str(turn -1))
    # feed back as int
    turns_left = int(turns_widget_no[current_lvl].text())

    # move_left, move_right etc. for the current lvl
    directions = directions_widgets[current_lvl]

    for button in directions:
        button.show()

    if x == 260:
        directions[0].hide()

    elif current_lvl == "1" and x == 370:
        ui.lvl1_move_right.hide()

    elif current_lvl == "2" and x == 480:
        ui.lvl2_move_right.hide()

    elif current_lvl == "3" and x == 590:
        ui.lvl3_move_right.hide()

    # hide up and right
    if y == 10:
        directions[2].hide()
        directions[1].hide()

    elif current_lvl == "1" and y == 230:
        ui.lvl1_move_down.hide()

    elif current_lvl == "2" and y == 340:
        ui.lvl2_move_down.hide()

    elif current_lvl == "3" and y == 450:
        ui.lvl3_move_down.hide()

    elif y == 120 and not x == 260:
        directions[2].hide()

    return check_eaten(turns_left)


# Animations of good or rotten apples, depending on payoff, on the current patch
# index [0]: good, [1]: bad

def animation_good():

    good_apple = payoff_widgets[current_lvl][0]
    currentX = good_apple.x()
    currentY = good_apple.y()
    good_apple.setGeometry(currentX, currentY - 20, 50, 50)

    if currentY == 0:

        timer_good.stop()
        good_apple.hide()

    timer_good.start(50)

def animation_bad():

    bad_apple = payoff_widgets[current_lvl][1]
    currentX = bad_apple.x()
    currentY = bad_apple.y()
    bad_apple.setGeometry(currentX, currentY - 20, 50, 50)

    if currentY == 0:

        timer_bad.stop()
        bad_apple.hide()

    timer_bad.start(50)

timer_good = QTimer()
timer_good.timeout.connect(animation_good)
timer_bad = QTimer()
timer_bad.timeout.connect(animation_bad)

# For every time a patch is exploited, its payoff is reduced by a set value. This value depends on the condition
def depreciate(patch_no, current_payoff):

    print("PATCH", patch_no)
    exploited_count = patches_trackers[current_lvl][patch_no]

    print("exploited ", exploited_count, "before, payoff reduced by ", int(round(exploited_count * depreciator, 0)))
    return int(round((current_payoff - exploited_count * depreciator), 0))

# updates score, but only if level count is 1-3
def update_score(score):

    if current_lvl in levels:
        set_score = str(score)

        old_score = int(score_widget_no[current_lvl].text())
        score_widget_no[current_lvl].setText(str(old_score + score))

# updates dictionaries that log participant activity whenever a patch is exploited
def update_exploited_patches(patch_no, some_payoff):

    patches_trackers[current_lvl][patch_no] += 1
    payoff_trackers[current_lvl][patch_no] += some_payoff

# activated when the gather button is pressed and sets in motion a range of functions
#  that govern the payoff according to position, condition and depreciation
def gather():

    pos = get_pos()
    patch = get_patch(pos[0], pos[1])

    # zero payoff in the cave
    if patch == 0:
        payoff = 0
    else:
        raw_payoff = get_payoff(patch)

        # So that payoff is zero for this level, once you got eaten.
        if raw_payoff != None:
            payoff = depreciate(patch, raw_payoff)
        else:
            payoff = 0

    # show payoff
    results_widget_no[current_lvl].show()
    results_widget_text[current_lvl].show()
    results_widget_no[current_lvl].setText(str(payoff))

    # minus one move per gathering
    turns_left = int(turns_widget_no[current_lvl].text()) - 1
    turns_widget_no[current_lvl].setText(str(turns_left))

    # show payoff animations
    if payoff > 0:
        # index [0] for good apple
        good_apple = payoff_widgets[current_lvl][0]

        good_apple.move(pos[0] + 20, pos[1])
        good_apple.show()
        animation_good()

    elif payoff <= 0:
        # index [1] for bad apple
        bad_apple = payoff_widgets[current_lvl][1]

        bad_apple.move(pos[0]+20, pos[1])
        bad_apple.show()
        animation_bad()

    return check_eaten(turns_left), update_exploited_patches(patch, payoff), update_score(payoff)

#*********************************************************************************************************************
# This set of functions determines the payoff depending on the patch, once gather() is called

# acquires the appropriate parameters of the probability function, and proceeds to draw from it
def get_payoff(patch_no):

    patch = "patch" + str(patch_no)
    specs = patches_lvl[current_lvl][patch]
    specs = specs.split(",")
    return draw(specs[0], int(specs[1]), int(specs[2]))

# drawing from the probability functions, according to patch parameters that are saved in the specs file
# which of these are loaded, depends on the condition
def draw(type, mean, sd):
    result_int = 0

    if type == "g":
        result = random.gauss(mean, sd)
        result_int = int(round(result, 0))

    elif type == "l":
        result = random.lognormvariate(mean, sd)
        result_int = int(round(result, 0))

    elif type == "n":
        result = random.normalvariate(mean, sd)
        result_int = int(round(result, 0))

    elif type == "m":
        multi = random.randint(0, prob_multi)
        if multi == 1:
            result = random.gauss(mean - mod_mean, sd + mod_sd)
            result_int = int(round(result, 0))
        else:
            result = random.gauss(mean, sd)
            result_int = int(round(result, 0))

    elif type == "d":
        tiger = random.randint(0, prob_tiger)
        if tiger == 1:
            eaten()
            return None
        else:
            result = random.gauss(mean, sd)
            result_int = int(round(result, 0))

    return (result_int * difficulty_multi) + difficulty_add

# determines the patch number (e.g. 0 for patch0, 1 for patch1 etc.) according to x and y coordinates
# Patches are arranged clockwise on level1, and then added per layer; i.e. patch 3 on all levels is the same coordinates
def get_patch(x, y):

    if x == 260:
        if y == 10:
            return 0
        elif y == 120:
            return 1
        elif y == 230:
            return 4
        elif y == 340:
            return 9
        elif y == 450:
            return 16

    elif x == 370:
        if y == 120:
            return 2
        elif y == 230:
            return 3
        elif y == 340:
            return 8
        elif y == 450:
            return 15

    elif x == 480:
        if y == 120:
            return 5
        elif y == 230:
            return 6
        elif y == 340:
            return 7
        elif y == 450:
            return 14

    elif x == 590:
        if y == 120:
            return 10
        elif y == 230:
            return 11
        elif y == 340:
            return 12
        elif y == 450:
            return 13


#*********************************************************************************************************************
# Connecting buttons & boxes on the consent page
ui.consent_button_quit.clicked.connect(terminate)
ui.consent_checkbox_yes.toggled.connect(check_consent)
ui.consent_checkbox_no.toggled.connect(check_consent)
ui.consent_button_submit.clicked.connect(next_page)
ui.consent_button_skip.clicked.connect(next_page)

# Connecting buttons & boxes on the demographics page
ui.demo_box_ppt.textChanged.connect(update_ppt_no)
ui.demo_box_age.valueChanged.connect(update_age)
ui.demo_box_gender.currentIndexChanged.connect(update_sex)
ui.demo_box_vision.currentIndexChanged.connect(update_vision)
ui.demo_box_handedness.currentIndexChanged.connect(update_handedness)
ui.demo_box_edu.currentIndexChanged.connect(update_edu)
ui.demo_box_student.currentIndexChanged.connect(update_student)
ui.demo_box_subject.currentIndexChanged.connect(update_subject)
ui.demo_box_year.currentIndexChanged.connect(update_year)
ui.demo_button_submit.clicked.connect(submitted)
ui.demo_box_student.currentIndexChanged.connect(show_student)
ui.demo_button_skip.clicked.connect(next_page)

# Connecting buttons on the instruction page
ui.inst_checkbox.toggled.connect(check_inst)
ui.inst_button_confirm.clicked.connect(next_page)
ui.inst_button_skip.clicked.connect(next_page)

# Connecting buttons on lvl1
ui.lvl1_button_eatme.clicked.connect(eaten)
ui.lvl1_button_eaten.clicked.connect(eaten_next)
ui.lvl1_move_down.clicked.connect(move_down)
ui.lvl1_move_up.clicked.connect(move_up)
ui.lvl1_move_left.clicked.connect(move_left)
ui.lvl1_move_right.clicked.connect(move_right)
ui.lvl1_gather.clicked.connect(gather)

# Connecting buttons on lvl2
ui.lvl2_button_eatme.clicked.connect(eaten)
ui.lvl2_button_eaten.clicked.connect(eaten_next)
ui.lvl2_move_down.clicked.connect(move_down)
ui.lvl2_move_up.clicked.connect(move_up)
ui.lvl2_move_left.clicked.connect(move_left)
ui.lvl2_move_right.clicked.connect(move_right)
ui.lvl2_gather.clicked.connect(gather)

# Connecting buttons on lvl3
ui.lvl3_button_eatme.clicked.connect(eaten)
ui.lvl3_button_eaten.clicked.connect(eaten_next)
ui.lvl3_move_down.clicked.connect(move_down)
ui.lvl3_move_up.clicked.connect(move_up)
ui.lvl3_move_left.clicked.connect(move_left)
ui.lvl3_move_right.clicked.connect(move_right)
ui.lvl3_gather.clicked.connect(gather)

# Connecting buttons on the debriefing page
ui.debrief_open_answer.textChanged.connect(update_feedback)
ui.debrief_button_quit.clicked.connect(terminate_write_feedback)

#*********************************************************************************************************************
# Starts the UI here

window.show()

sys.exit(app.exec_())

#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# ./setup-degree-project-course.py cycle_number course_id school_acronym
#
# Output: none (it modifies the state of the course)
#
#
# Input
# cycle_number is either 1 or 2 (1st or 2nd cycle)
#
# "-m" or "--modules" set up the two basic modules (Gatekeeper module 1 and Gatekeeper protected module 1)
# "-p" or "--page" set up the two basic pages for the course
# "-s" or "--survey" set up the survey
# "-S" or "--sections" set up the sections for the examiners and programs
#
# with the option "-v" or "--verbose" you get lots of output - showing in detail the operations of the program
#
# Can also be called with an alternative configuration file:
# ./setup-degree-project-course.py --config config-test.json 1 12683
#
# Example:
#
# Create basic modules:
#   ./setup-degree-project-course.py --config config-test.json -m 1 12683
#
# Create survey:
#   ./setup-degree-project-course.py --config config-test.json -s 1 12683 EECS
#
# Create custom colums:
#   ./setup-degree-project-course.py --config config-test.json -c 1 12683
#
# Create sections for examiners and programs:
#   ./setup-degree-project-course.py --config config-test.json -S 1 12683
#
# Create pages for the course
#   ./setup-degree-project-course.py --config config-test.json -p 1 12683
#
# G. Q. Maguire Jr.
#
#
# 2019.01.05
#

import requests, time
import pprint
import optparse
import sys
import json

# Use Python Pandas to create XLSX files
import pandas as pd

from bs4 import BeautifulSoup

################################
######    KOPPS related   ######
################################
KOPPSbaseUrl = 'https://www.kth.se'

English_language_code='en'
Swedish_language_code='sv'

KTH_Schools = {
    'ABE':  ['ABE'],
    'CBH':  ['BIO', 'CBH', 'CHE', 'STH'],
    'EECS': ['CSC', 'EES', 'ICT', 'EECS'], # corresponds to course codes starting with D, E, I, and J
    'ITM':  ['ECE', 'ITM'],
    'SCI':  ['SCI']
}

def v1_get_programmes():
    global Verbose_Flag
    #
    # Use the KOPPS API to get the data
    # GET /api/kopps/v1/course/{course code}
    # note that this returns XML
    url = "{0}/api/kopps/v1/programme".format(KOPPSbaseUrl)
    if Verbose_Flag:
        print("url: " + url)
    #
    r = requests.get(url)
    if Verbose_Flag:
        print("result of getting v1 programme: {}".format(r.text))
    #
    if r.status_code == requests.codes.ok:
        return r.text           # simply return the XML
    #
    return None

def programs_and_owner_and_titles():
    programs=v1_get_programmes()
    xml=BeautifulSoup(programs, "lxml")
    program_and_owner_titles=dict()
    for prog in xml.findAll('programme'):
        if prog.attrs['cancelled'] == 'false':
            owner=prog.owner.string
            titles=prog.findAll('title')
            title_en=''
            title_sv=''
            for t in titles:
                if t.attrs['xml:lang'] == 'en':
                    title_en=t.string
                if t.attrs['xml:lang'] == 'sv':
                    title_sv=t.string
            program_and_owner_titles[prog.attrs['code']]={'owner': owner, 'title_en': title_en, 'title_sv': title_sv}
    #
    return program_and_owner_titles

def programs_and_owner():
    programs=v1_get_programmes()
    xml=BeautifulSoup(programs, "lxml")
    program_and_owner=dict()
    for prog in xml.findAll('programme'):
        if prog.attrs['cancelled'] == 'false':
            program_and_owner[prog.attrs['code']]=prog.owner.string
    #
    return program_and_owner

def programs_in_school(programs, school_acronym):
    programs_in_the_school=list()
    #
    for p in programs:
        if programs[p]['owner'] == school_acronym:
            programs_in_the_school.append(p)
    return programs_in_the_school

def programs_in_school_with_titles(programs, school_acronym):
    relevant_programs=dict()
    #
    for p in programs:
        if programs[p]['owner'] == school_acronym:
            relevant_programs[p]=programs[p]
    return relevant_programs

# returns a list of elements of the form: {"code":"IF","name":"ICT/Kommunikationssystem"}
def get_dept_codes(language_code):
    global Verbose_Flag
    # GET https://www.kth.se/api/kopps/v2/departments.en.json
    # GET https://www.kth.se/api/kopps/v2/departments.sv.json
    url = "{0}/api/kopps/v2/departments.{1}.json".format(KOPPSbaseUrl, language_code)
    if Verbose_Flag:
        print("url: {}".format(url))
    #
    r = requests.get(url)
    if Verbose_Flag:
        print("result of getting department codes: {}".format(r.text))
    #
    if r.status_code == requests.codes.ok:
        page_response=r.json()
        return page_response
    #
    return None

def dept_codes_in_a_school(school_acronym, all_dept_codes):
    dept_codes=[]
    for dept in KTH_Schools[school_acronym]:
        for d in all_dept_codes:
            if d['name'].find(dept) == 0:
                dept_codes.append(d['code'])
    return dept_codes

def get_dept_courses(dept_code, language_code):
    global Verbose_Flag
    # Use the KOPPS API to get the data
    # GET /api/kopps/v2/courses/dd.json
    url = "{0}/api/kopps/v2/courses/{1}.json".format(KOPPSbaseUrl, dept_code)
    if language_code == 'en':
        url = url +'?l=en'    
    if Verbose_Flag:
        print("url: {}".format(url))
    #
    r = requests.get(url)
    if Verbose_Flag:
        print("result of getting courses for a department: {}".format(r.text))
    #
    if r.status_code == requests.codes.ok:
        page_response=r.json()
        return page_response
    #
    return None

def get_course_info(course_code):
    global Verbose_Flag
    # Use the KOPPS API to get the data
    # GET /api/kopps/v2/course/{course code}
    url = "{0}/api/kopps/v2/course/{1}".format(KOPPSbaseUrl, course_code)
    if Verbose_Flag:
        print("url: {}".format(url))
    #
    r = requests.get(url)
    if Verbose_Flag:
        print("result of getting course info: {}".format(r.text))
    #
    if r.status_code == requests.codes.ok:
        page_response=r.json()
        return page_response
    #
    return None



def get_course_rounds_info(course_code, r_info):
#Course round
#Returns information about a course round with specified course code, term, and Ladok round id.
#/api/kopps/v1/course/{course code}/round/{year}:{term (1/2)}/{round id}/{language (en|sv)}
# E.g. /api/kopps/v1/course/HS1735/round/2010:1/2
#https://www.kth.se/api/kopps/v1/course/II2202/round/2018:2/1
    global Verbose_Flag
    #
    if Verbose_Flag:
        print("get_course_rounds_info({0},{1})".format(course_code, r_info))
    round_id=r_info['n']
    startTerm=r_info['startTerm']
    year=startTerm[0:4]
    term=startTerm[4]
    if Verbose_Flag:
        print("get_course_rounds_info: round_id={0}, year={1}, term={2})".format(round_id, year, term))
    # Use the KOPPS API to get the data
    # GET /api/kopps/v1/course/{course code}/round/{year}:{term (1/2)}/{round id}/{language (en|sv)}
    # note that this returns XML
    url = "{0}/api/kopps/v1/course/{1}/round/{2}:{3}/{4}".format(KOPPSbaseUrl, course_code, year, term, round_id)
    if Verbose_Flag:
        print("url: {}".format(url))
    #
    r = requests.get(url)
    if Verbose_Flag:
        print("result of getting course round info: {}".format(r.text))
    #
    if r.status_code == requests.codes.ok:
        return r.text           # simply return the XML
    #
    return None

def v1_get_course_info(course_code):
    global Verbose_Flag
    #
    # Use the KOPPS API to get the data
    # GET /api/kopps/v1/course/{course code}
    # note that this returns XML
    url = "{0}/api/kopps/v1/course/{1}".format(KOPPSbaseUrl, course_code)
    if Verbose_Flag:
        print("url: {}".format(url))
    #
    r = requests.get(url)
    if Verbose_Flag:
        print("result of getting v1 course info: {}".format(r.text))
    #
    if r.status_code == requests.codes.ok:
        return r.text           # simply return the XML
    #
    return None



def convert_course_name_to_subject(name_of_course):
    working_str=name_of_course.rsplit(",")[0]
    #
    # if name_of_course begins with "Examensarbete inom ", skip this part
    prefix="Examensarbete inom "
    offset=working_str.find(prefix)
    if offset >= 0:
        working_str=working_str[(offset+len(prefix)):]
        return working_str
    #
    prefix2="Examensarbete i "
    offset2=name_of_course.find(prefix2)
    if offset2 >= 0:
        working_str=working_str[(offset2+len(prefix2)):]
        return working_str
    #
    return working_str

# returns a list of courses in the format: {'code': 'IL246X', 'title': 'Examensarbete inom elektroteknik, avancerad nivå', 'href': 'https://www.kth.se/student/kurser/kurs/IL246X', 'info': '', 'credits': '30,0', 'level': 'Avancerad nivå', 'state': 'ESTABLISHED', 'dept_code': 'J', 'department': 'EECS/Skolan för elektroteknik och datavetenskap', 'cycle': '2', 'subject': 'elektroteknik'}
def degree_project_courses(requested_dept_codes, language_code):
    global Verbose_Flag
    courses=[]                  # initialize the list of courses
    if len(requested_dept_codes) > 0:
        for d in requested_dept_codes:
            courses_d_all=get_dept_courses(d, language_code)
            courses_d=courses_d_all['courses']
            if Verbose_Flag:
                print("length of courses_d in dept {0} is {1}".format(d, len(courses_d)))
            # extend course information with department and dept_code
            for c in courses_d:
                # do not include cancelled courses by default
                if c['state'].find('CANCELLED') >=0:
                    continue
                c['dept_code']=d
                c['department']=courses_d_all['department']
                c['cycle'] = c['code'][2]
                name_of_course=c['title'][:] # name a copy of the string - so that changes to it do not propagate elsewhere
                c['subject']=convert_course_name_to_subject(name_of_course)
                if c['code'].endswith('x') or c['code'].endswith('X'):
                    courses.append(c)
                else:
                    continue
    else:
        return []
    return courses

def course_examiners(courses):
    global Verbose_Flag
    # get the examiners
    courses_info=dict()
    for c in courses:
        c_info=v1_get_course_info(c)
        xml=BeautifulSoup(c_info, "lxml")
        examiners=list()
        for examiner in xml.findAll('examiner'):
            examiners.append(examiner.string)
        courses_info[c]=examiners
    return courses_info

def potential_examiners_answer(examiners):
    examiner_alternatives_list=[]
    #
    for e in sorted(examiners):
        new_element=dict()
        new_element['blank_id']='e1'
        new_element['weight']=100
        new_element['text']=e
        examiner_alternatives_list.append(new_element)

    return examiner_alternatives_list



# returns a dict with the format:  {'II226X': 'AF', 'II246X': 'PF'}
# note that each of the course codes will only have one instance in the list
def course_gradingscale(courses):
    global Verbose_Flag
    # get the grading scale used for the course
    courses_info = dict()
    for c in courses:
        c_info=v1_get_course_info(c)
        xml=BeautifulSoup(c_info, "lxml")
        for gradingscale in xml.findAll('gradescalecode'):
            courses_info[c]="{}".format(gradingscale.string)
            if Verbose_Flag:
                print("gradingscale: {0}".format(gradingscale))
    return courses_info

def course_code_alternatives(pf_courses, af_courses):
    course_code_alternatives_list=[]
    for i in sorted(pf_courses):
        new_element=dict()
        new_element['blank_id']='PF'
        new_element['weight']=100
        new_element['text']=i
        course_code_alternatives_list.append(new_element)
    #
    for i in sorted(af_courses):
        new_element=dict()
        new_element['blank_id']='AF'
        new_element['weight']=100
        new_element['text']=i
        course_code_alternatives_list.append(new_element)
    #
    return course_code_alternatives_list

# def credits_for_course(course_code, courses):
#     for c in courses:
#         if c['code'] == course_code:
#             return c['credits']
#     return 0

# def title_for_course(course_code, courses):
#     for c in courses:
#         if c['code'] == course_code:
#             return c['title']
#     return ''

def credits_for_course(course_code, courses):
    credits=0
    course=courses.get(course_code, [])
    if course: 
        credits=course.get('credits', 0)
    return credits

def title_for_course(course_code, courses):
    title=''
    course=courses.get(course_code, [])
    if course: 
        title=course.get('title', 0)
    return title

def course_code_descriptions(pf_courses, af_courses, courses_english, courses_swedish):
    course_code_description='<div class="enhanceable_content tabs"><ul><li lang="en"><a href="#fragment-1">English</a></li><li lang="sv"><a href="#fragment-2">På svenska</a></li></ul><div id="fragment-1"><p lang="en"><table border="1" cellspacing="1" cellpadding="1"><tbody>'
    table_heading='<tr><th>Course Code</th><th>Credits</th><th>Name</th></tr>'
    course_code_description=course_code_description+table_heading

    for i in sorted(pf_courses):
        table_row='<tr><td>'+i+'</td><td>'+credits_for_course(i, courses_english)+'</td><td lang="en">'+title_for_course(i, courses_english)+'</td></tr>'
        course_code_description=course_code_description+table_row
    # end of table
    course_code_description=course_code_description+'</tbody></table></div><div id="fragment-2"><table border="1" cellspacing="1" cellpadding="1"><tbody>'
    table_heading='<tr><th>Kurskod</th><th>Credits</th><th>Namn</th></tr>'
    course_code_description=course_code_description+table_heading
    #
    for i in sorted(af_courses):
        table_row='<tr><td>'+i+'</td><td>'+credits_for_course(i, courses_swedish)+'</td><td lang="sv">'+title_for_course(i, courses_swedish)+'</td></tr>'
        course_code_description=course_code_description+table_row
    # end of table
    course_code_description=course_code_description+'</tbody></table></div>'
    #
    return course_code_description


################################
###### Canvas LMS related ######
################################

global baseUrl	# the base URL used for access to Canvas
global header	# the header for all HTML requests
global payload	# place to store additionally payload when needed for options to HTML requests

# Based upon the options to the program, initialize the variables used to access Canvas gia HTML requests
def initialize(options):
       global baseUrl, header, payload

       # styled based upon https://martin-thoma.com/configuration-files-in-python/
       if options.config_filename:
              config_file=options.config_filename
       else:
              config_file='config.json'

       try:
              with open(config_file) as json_data_file:
                     configuration = json.load(json_data_file)
                     access_token=configuration["canvas"]["access_token"]
                     baseUrl="https://"+configuration["canvas"]["host"]+"/api/v1"

                     header = {'Authorization' : 'Bearer ' + access_token}
                     payload = {}
       except:
              print("Unable to open configuration file named {}".format(config_file))
              print("Please create a suitable configuration file, the default name is config.json")
              sys.exit()

def users_in_course(course_id):
       user_found_thus_far=[]
       # Use the Canvas API to get the list of users enrolled in this course
       #GET /api/v1/courses/:course_id/enrollments

       url = "{0}/courses/{1}/enrollments".format(baseUrl,course_id)
       if Verbose_Flag:
              print("url: {}".format(url))

       extra_parameters={'per_page': '100'}
       r = requests.get(url, params=extra_parameters, headers = header)
       if Verbose_Flag:
              print("result of getting enrollments: {}".format(r.text))

       if r.status_code == requests.codes.ok:
              page_response=r.json()

              for p_response in page_response:  
                     user_found_thus_far.append(p_response)

              # the following is needed when the reponse has been paginated
              # i.e., when the response is split into pieces - each returning only some of the list of modules
              # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
              while r.links['current']['url'] != r.links['last']['url']:  
                     r = requests.get(r.links['next']['url'], headers=header)  
                     page_response = r.json()  
                     for p_response in page_response:  
                            user_found_thus_far.append(p_response)
       return user_found_thus_far

def user_profile_url(user_id):
       # Use the Canvas API to get the profile of a user
       #GET /api/v1/users/:user_id/profile

       url = "{0}/users/{1}/profile".format(baseUrl, user_id)
       if Verbose_Flag:
              print("user url: {}".format(url))

       r = requests.get(url, headers = header)
       if Verbose_Flag:
              print("result of getting profile: {}".format(r.text))

       if r.status_code == requests.codes.ok:
              page_response=r.json()
              return page_response
       return []

def section_name_from_section_id(sections_info, section_id): 
       for i in sections_info:
            if i['id'] == section_id:
                   return i['name']

def sections_in_course(course_id):
       sections_found_thus_far=[]
       # Use the Canvas API to get the list of sections for this course
       #GET /api/v1/courses/:course_id/sections

       url = "{0}/courses/{1}/sections".format(baseUrl,course_id)
       if Verbose_Flag:
              print("url: {}".format(url))

       r = requests.get(url, headers = header)
       if Verbose_Flag:
              print("result of getting sections: {}".format(r.text))

       if r.status_code == requests.codes.ok:
              page_response=r.json()

              for p_response in page_response:  
                     sections_found_thus_far.append(p_response)

              # the following is needed when the reponse has been paginated
              # i.e., when the response is split into pieces - each returning only some of the list of modules
              # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
              while r.links['current']['url'] != r.links['last']['url']:  
                     r = requests.get(r.links['next']['url'], headers=header)  
                     page_response = r.json()  
                     for p_response in page_response:  
                            sections_found_thus_far.append(p_response)

       return sections_found_thus_far

def list_your_courses():
       courses_found_thus_far=[]
       # Use the Canvas API to get the list of all of your courses
       # GET /api/v1/courses

       url = baseUrl+'courses'
       if Verbose_Flag:
              print("url: {}".format(url))

       r = requests.get(url, headers = header)
       if Verbose_Flag:
              print("result of getting courses: {}".format(r.text))

       if r.status_code == requests.codes.ok:
              page_response=r.json()

              for p_response in page_response:  
                     courses_found_thus_far.append(p_response)

              # the following is needed when the reponse has been paginated
              # i.e., when the response is split into pieces - each returning only some of the list of modules
              # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
              while r.links['current']['url'] != r.links['last']['url']:  
                     r = requests.get(r.links['next']['url'], headers=header)  
                     if Verbose_Flag:
                            print("result of getting courses for a paginated response: {}".format(r.text))
                     page_response = r.json()  
                     for p_response in page_response:  
                            courses_found_thus_far.append(p_response)

       return courses_found_thus_far

def list_assignments(course_id):
    assignments_found_thus_far=[]
    # Use the Canvas API to get the list of assignments for the course
    #GET /api/v1/courses/:course_id/assignments

    url = "{0}/courses/{1}/assignments".format(baseUrl, course_id)
    if Verbose_Flag:
        print("url: {}".format(url))

    r = requests.get(url, headers = header)
    if Verbose_Flag:
        print("result of getting assignments: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()

        for p_response in page_response:  
            assignments_found_thus_far.append(p_response)

            # the following is needed when the reponse has been paginated
            # i.e., when the response is split into pieces - each returning only some of the list of assignments
            # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
            while r.links['current']['url'] != r.links['last']['url']:  
                r = requests.get(r.links['next']['url'], headers=header)  
                if Verbose_Flag:
                    print("result of getting assignments for a paginated response: {}".format(r.text))
                page_response = r.json()  
                for p_response in page_response:  
                    assignments_found_thus_far.append(p_response)

    return assignments_found_thus_far

def create_assignment(course_id, name, max_points, grading_type, description):
    # Use the Canvas API to create an assignment
    # POST /api/v1/courses/:course_id/assignments

    # Request Parameters:
    #Parameter		Type	Description
    # assignment[name]	string	The assignment name.
    # assignment[position]		integer	The position of this assignment in the group when displaying assignment lists.
    # assignment[submission_types][]		string	List of supported submission types for the assignment. Unless the assignment is allowing online submissions, the array should only have one element.
    # assignment[peer_reviews]	boolean	If submission_types does not include external_tool,discussion_topic, online_quiz, or on_paper, determines whether or not peer reviews will be turned on for the assignment.
    # assignment[notify_of_update] boolean     If true, Canvas will send a notification to students in the class notifying them that the content has changed.
    # assignment[grade_group_students_individually]		integer	 If this is a group assignment, teachers have the options to grade students individually. If false, Canvas will apply the assignment's score to each member of the group. If true, the teacher can manually assign scores to each member of the group.
    # assignment[points_possible]		number	 The maximum points possible on the assignment.
    # assignment[grading_type]		string	The strategy used for grading the assignment. The assignment defaults to “points” if this field is omitted.
    # assignment[description]		string	The assignment's description, supports HTML.
    # assignment[grading_standard_id]		integer	The grading standard id to set for the course. If no value is provided for this argument the current grading_standard will be un-set from this course. This will update the grading_type for the course to 'letter_grade' unless it is already 'gpa_scale'.
    # assignment[published]		boolean	Whether this assignment is published. (Only useful if 'draft state' account setting is on) Unpublished assignments are not visible to students.

    url = "{0}/courses/{1}/assignments".format(baseUrl, course_id)
    if Verbose_Flag:
        print("url: {}".format(url))

    payload={'assignment[name]': name,
             'assignment[submission_types][]': ["none"],
             'assignment[peer_reviews]': False,
             'assignment[notify_of_update]': False,
             'assignment[grade_group_students_individually]': True,
             'assignment[peer_reviews]': False,
             'assignment[points_possible]': max_points,
             'assignment[grading_type]': grading_type,
             'assignment[description]': description,
             'assignment[published]': True # if not published it will not be in the gradebook
    }

    r = requests.post(url, headers = header, data=payload)
    if Verbose_Flag:
        print("result of post making an assignment: {}".format(r.text))
        print("r.status_code={}".format(r.status_code))
    if r.status_code == requests.codes.created:
        page_response=r.json()
        print("inserted assignment")
        return page_response['id']
    return False


def create_module_assignment_item(course_id, module_id, assignment_id, item_name, points):
    # Use the Canvas API to create a module item in the course and module
    #POST /api/v1/courses/:course_id/modules/:module_id/items
    url = "{0}/courses/{1}/modules/{2}/items".format(baseUrl, course_id, module_id)
    if Verbose_Flag:
        print("creating module assignment item for course_id={0} module_id={1} assignment_id={1}".format(course_id, module_id, assignment_id))
    payload = {'module_item[title]': item_name,
               'module_item[type]': 'Assignment',
               'module_item[content_id]': assignment_id,
               'module_item[completion_requirement][type]': 'min_score',
               'module_item[completion_requirement][min_score]': points

    }

    r = requests.post(url, headers = header, data = payload)
    if Verbose_Flag:
        print("result of creating module: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        modules_response=r.json()
        module_id=modules_response["id"]
        return module_id
    return  module_id

def list_modules(course_id):
    modules_found_thus_far=[]
    # Use the Canvas API to get the list of modules for the course
    #GET /api/v1/courses/:course_id/modules

    url = "{0}/courses/{1}/modules".format(baseUrl, course_id)
    if Verbose_Flag:
        print("url: {}".format(url))

    r = requests.get(url, headers = header)
    if Verbose_Flag:
        print("result of getting modules: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()

        for p_response in page_response:  
            modules_found_thus_far.append(p_response)

            # the following is needed when the reponse has been paginated
            # i.e., when the response is split into pieces - each returning only some of the list of modules
            # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
            while r.links['current']['url'] != r.links['last']['url']:  
                r = requests.get(r.links['next']['url'], headers=header)  
                if Verbose_Flag:
                    print("result of getting modules for a paginated response: {}".format(r.text))
                page_response = r.json()  
                for p_response in page_response:  
                    modules_found_thus_far.append(p_response)

    return modules_found_thus_far

def create_module(course_id, module_name, requires_module_id):
    module_id=None              # will contain the module's ID if it exists
    # Use the Canvas API to create a module in the course
    #POST /api/v1/courses/:course_id/modules
    url = "{0}/courses/{1}/modules".format(baseUrl, course_id,module_name)
    if Verbose_Flag:
        print("creating module for course_id={0} module_name={1}".format(course_id,module_name))
    if requires_module_id:
        payload = {'module[name]': module_name,
                   'module[prerequisite_module_ids][]': requires_module_id
        }
    else:
        payload = {'module[name]': module_name
        }
    r = requests.post(url, headers = header, data = payload)
    if Verbose_Flag:
        print("result of creating module: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        modules_response=r.json()
        module_id=modules_response["id"]
        return module_id
    return  module_id

def create_gatekeeper_module(course_id, module_name):
    module_id=None              # will contain the module's ID if it exists
    # Use the Canvas API to create a module in the course
    #POST /api/v1/courses/:course_id/modules
    url = "{0}/courses/{1}/modules".format(baseUrl, course_id)
    if Verbose_Flag:
        print("creating module for course_id={0} module_name={1}".format(course_id,module_name))
    payload = {'module[name]': module_name,
               'module[position]': 1,
               'module[require_sequential_progress]': True
    }
    r = requests.post(url, headers = header, data = payload)
    if Verbose_Flag:
        print("result of creating module: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        modules_response=r.json()
        module_id=modules_response["id"]
        return module_id
    return  module_id

def check_for_module(course_id,  module_name):
    modules_found_thus_far=[]
    module_id=None              # will contain the moudle's ID if it exists
    # Use the Canvas API to get the list of modules for the course
    #GET /api/v1/courses/:course_id/modules

    url = "{0}/courses/{1}/modules".format(baseUrl, course_id)
    if Verbose_Flag:
        print("url: {}".format(url))

    # this will do a partial match against the module_name
    # This reducing the number of responses returned

    payload = {'search_term': module_name} 
    r = requests.get(url, headers = header, data = payload)
    if Verbose_Flag:
        print("result of getting modules: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()

        for p_response in page_response:  
            modules_found_thus_far.append(p_response)

            # the following is needed when the reponse has been paginated
            # i.e., when the response is split into pieces - each returning only some of the list of modules
            # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
            while r.links['current']['url'] != r.links['last']['url']:  
                r = requests.get(r.links['next']['url'], headers=header)  
                if Verbose_Flag:
                    print("result of getting modules for a paginated response: {}".format(r.text))
                page_response = r.json()  
                for p_response in page_response:  
                    modules_found_thus_far.append(p_response)

    name_to_match="{}".format(module_name)
    if Verbose_Flag:
       print("name \t id\tmatching: {}".format(name_to_match))

    for m in modules_found_thus_far:
        if (m["name"]  ==  name_to_match):
            if Verbose_Flag:
                print("{0}\t{1}\ttrue".format(m["name"], m["id"]))
            module_id=m["id"]
            if Verbose_Flag:
                print("module_id is {}".format(module_id))
            return module_id
        else:
            if Verbose_Flag:
                print("{0}\t{1}".format(m["name"],m["id"]))

    return module_id


def create_basic_modules(course_id):
    module_id=check_for_module(course_id, "Gatekeeper module 1")
    print("create_basic_modules:module_id={}".format(module_id))
    if not module_id:
        module_id=create_gatekeeper_module(course_id, "Gatekeeper module 1")
    print("create_basic_modules:module_id={}".format(module_id))

    name="Gatekeeper 1 access control"
    description="This assignment is simply for access control. When the teacher sets the assignment for a student to have 1 point then the student will have access to the pages protected by the module where this assignment is."
    assignment_id=create_assignment(course_id, name, 1, 'points', description)
    print("create_basic_modules:assignment_id={}".format(assignment_id))

    item_name="Gatekeeper 1 access control"
    create_module_assignment_item(course_id, module_id, assignment_id, item_name, 1)

    if not check_for_module(course_id,  "Gatekeeper protected module 1"):
        access_controlled_module=create_module(course_id, "Gatekeeper protected module 1", module_id)

    return access_controlled_module

def create_survey_quiz(course_id):
    # Use the Canvas API to create a quiz
    # POST /api/v1/courses/:course_id/quizzes

    # Request Parameters:
    url = "{0}/courses/{1}/quizzes".format(baseUrl, course_id)
    if Verbose_Flag:
        print("url: {}".format(url))

    description='<div class="enhanceable_content tabs">\n<ul>\n<li lang="en"><a href="#fragment-1">English</a></li>\n<li lang="sv"><a href="#fragment-2">På svenska</a></li>\n</ul>\n<div id="fragment-1">\n<p lang="en">Please answer the following questions about your propose degree project.</p>\n</div>\n<div id="fragment-2">\n<p lang="sv">Var snäll och svara på följande frågor om ditt förslag på exjobb.</p>\n</div>\n</div>'
    payload={'quiz[title]': 'Information om exjobbsprojekt/Information for degree project',
             'quiz[description]': description,
             'quiz[quiz_type]': 'survey',
             'quiz[hide_results]': '',
             'quiz[show_correct_answers]': 'false',
             'quiz[allowed_attempts]': -1,
             'quiz[scoring_policy]': 'keep_latest',
             'quiz[published]': True
    }

    r = requests.post(url, headers = header, data=payload)
    if Verbose_Flag:
        print("result of post making a quiz: {}".format(r.text))
        print("r.status_code={}".format(r.status_code))
    if (r.status_code == requests.codes.created) or (r.status_code == requests.codes.ok):
        page_response=r.json()
        print("inserted quiz")
        return page_response['id']
    return False

def create_quiz_question_group(course_id, quiz_id, question_group_name):
    # return the quiz_group_id

    global Verbose_Flag

    # quiz_groups will be a dictionary of question_category and corresponding quiz_group_id
    # we learn the quiz_group_id when we put the first question into the question group
    print("course_id={0}, quiz_id={1}, question_group_name={2}".format(course_id, quiz_id, question_group_name))

    # Create a question group
    # POST /api/v1/courses/:course_id/quizzes/:quiz_id/groups
    url = "{0}/courses/{1}/quizzes/{2}/groups".format(baseUrl, course_id, quiz_id)

    if Verbose_Flag:
        print("url: " + url)
    payload={'quiz_groups':
             [
                 {
                     'name': question_group_name,
                     'pick_count': 1,
                     'question_points': 1
                 }
             ]
    }

    if Verbose_Flag:
        print("payload={}".format(payload))
    r = requests.post(url, headers = header, json=payload)

    print("result of post creating question group: {}".format(r.text))
    print("r.status_code={}".format(r.status_code))
    if (r.status_code == requests.codes.ok) or (r.status_code == 201):
        print("result of creating question group in the course: {}".format(r.text))
        page_response=r.json()
        if Verbose_Flag:
            print("page_response={}".format(page_response))
        # store the new id in the dictionary
        if Verbose_Flag:
            print("inserted question group={}".format(question_group_name))
            # '{"quiz_groups":[{"id":541,"quiz_id":2280,"name":"Newgroup","pick_count":1,"question_points":1.0,"position":2,"assessment_question_bank_id":null}]}')
        quiz_group_id=page_response['quiz_groups'][0]['id']
        if Verbose_Flag:
            print("quiz_group_id={}".format(quiz_group_id))
            return quiz_group_id

    return 0


def create_question_boolean(course_id, quiz_id, index, name, question_text, answers):
    #print("create_question_boolean:answers={}".format(answers))
    # Use the Canvas API to create a question for a quiz
    # POST /api/v1/courses/:course_id/quizzes/:quiz_id/questions

    # Request Parameters:
    url = "{0}/courses/{1}/quizzes/{2}/questions".format(baseUrl, course_id, quiz_id)
    if Verbose_Flag:
        print("url: {}".format(url))
    payload={'question':
             {
                 'question_name': name,
                 'question_text': question_text,
                 'question_type': 'true_false_question',
                 'question_category': 'Unknown',
                 'position': index,
                 'answers': answers,
             }
    }
    if Verbose_Flag:
        print("payload={}".format(payload))
    r = requests.post(url, headers = header, json=payload)
    if Verbose_Flag:
        print("result of post making a question: {}".format(r.text))
        print("r.status_code={}".format(r.status_code))
    if r.status_code == requests.codes.created:
        page_response=r.json()
        print("inserted question")
        return page_response['id']
    return False

def create_question_multiple_choice(course_id, quiz_id, index, name, question_text, answers):
    #print("create_question_multiple_choice:answers={}".format(answers))
    # Use the Canvas API to create a question for a quiz
    # POST /api/v1/courses/:course_id/quizzes/:quiz_id/questions

    # Request Parameters:
    url = "{0}/courses/{1}/quizzes/{2}/questions".format(baseUrl, course_id, quiz_id)
    if Verbose_Flag:
        print("url: {}".format(url))
    payload={'question':
             {
                 'question_name': name,
                 'question_text': question_text,
                 'question_type': 'multiple_choice_question',
                 'question_category': 'Unknown',
                 'position': index,
                 'answers': answers,
             }
    }
    if Verbose_Flag:
        print("payload={}".format(payload))
    r = requests.post(url, headers = header, json=payload)
    if Verbose_Flag:
        print("result of post making a question: {}".format(r.text))
        print("r.status_code={}".format(r.status_code))
    if r.status_code == requests.codes.created:
        page_response=r.json()
        print("inserted question")
        return page_response['id']
    return False


def create_question_essay(course_id, quiz_id, index, name, question_text):
    # Use the Canvas API to create a question for a quiz
    # POST /api/v1/courses/:course_id/quizzes/:quiz_id/questions

    # Request Parameters:
    url = "{0}/courses/{1}/quizzes/{2}/questions".format(baseUrl, course_id, quiz_id)
    if Verbose_Flag:
        print("url: {}".format(url))
    payload={'question':
             {
                 'question_name': name,
                 'question_text': question_text,
                 'question_type': 'essay_question',
                 'question_category': 'Unknown',
                 'position': index
             }
    }

    r = requests.post(url, headers = header, json=payload)
    if Verbose_Flag:
        print("result of post making a question: {}".format(r.text))
        print("r.status_code={}".format(r.status_code))
    if r.status_code == requests.codes.created:
        page_response=r.json()
        print("inserted question")
        return page_response['id']
    return False

def create_question_short_answer_question(course_id, quiz_id, index, name, question_text):
    # Use the Canvas API to create a question for a quiz
    # POST /api/v1/courses/:course_id/quizzes/:quiz_id/questions

    # Request Parameters:
    url = "{0}/courses/{1}/quizzes/{2}/questions".format(baseUrl, course_id, quiz_id)
    if Verbose_Flag:
        print("url: {}".format(url))
    payload={'question':
             {
                 'question_name': name,
                 'question_text': question_text,
                 'question_type': 'short_answer_question',
                 'question_category': 'Unknown',
                 'position': index
             }
    }

    r = requests.post(url, headers = header, json=payload)
    if Verbose_Flag:
        print("result of post making a question: {}".format(r.text))
        print("r.status_code={}".format(r.status_code))
    if r.status_code == requests.codes.created:
        page_response=r.json()
        print("inserted question")
        return page_response['id']
    return False


def create_question_multiple_dropdowns(course_id, quiz_id, index, name, question_text, answers):
    if Verbose_Flag:
        print("create_question_multiple_dropdowns:question_text={}".format(question_text))
        print("create_question_multiple_dropdowns:answers={}".format(answers))
    # Use the Canvas API to create a question for a quiz
    # POST /api/v1/courses/:course_id/quizzes/:quiz_id/questions

    # Request Parameters:
    url = "{0}/courses/{1}/quizzes/{2}/questions".format(baseUrl, course_id, quiz_id)
    if Verbose_Flag:
        print("url: {}".format(url))
    payload={'question':
             {
                 'question_name': name,
                 'question_text': question_text,
                 'question_type': 'multiple_dropdowns_question',
                 'question_category': 'Unknown',
                 'position': index,
                 'answers': answers,
             }
    }
    if Verbose_Flag:
        print("payload={}".format(payload))
    r = requests.post(url, headers = header, json=payload)
    if Verbose_Flag:
        print("result of post making a question: {}".format(r.text))
        print("r.status_code={}".format(r.status_code))
    if r.status_code == requests.codes.created:
        page_response=r.json()
        print("inserted question")
        return page_response['id']
    return False

def create_survey(course_id, cycle_number, school_acronym, PF_courses, AF_courses, relevant_courses_English, relevant_courses_Swedish, examiners):
    index=1
    survey=create_survey_quiz(course_id)

    graded_or_ungraded='<div class="enhanceable_content tabs"><ul>\n<li lang="en"><a href="#fragment-1">English</a></li>\n<li lang="sv"><a href="#fragment-2">På svenska</a></li>\n</ul>\n<div id="fragment-1">\n<p lang="en">Do you wish an A-F grade, rather than the default P/F (i.e. Pass/Fail) grade for your degree project?</p>\n<p>True: Grade A-F</p>\n<p>False: Pass/Fail (standard)</p>\n</div>\n<div id="fragment-2">\n<p lang="sv">Vill du ha ett betygsatt exjobb (A-F), i stället för ett vanligt med bara P/F (Pass/Fail)?</p>\n<p>Sant: Betygsatt exjobb (A-F)</p>\n<p>Falskt: Pass/Fail (standard)</p>\n</div>'

    create_question_boolean(course_id, survey, index,
                            'Graded or ungraded', graded_or_ungraded,
                            [{'answer_comments': '', 'answer_weight': 100, 'answer_text': 'True/Sant'}, {'answer_comments': '', 'answer_weight': 0, 'answer_text': 'False/Falskt'}])
    index += 1

    diva='<div class="enhanceable_content tabs"><ul>\n<li lang="en"><a href="#fragment-1">English</a></li>\n<li lang="sv"><a href="#fragment-2">På svenska</a></li>\n</ul>\n<div id="fragment-1">\n<p lang="en">Do you give KTH permission to make the full text of your final report available via DiVA?</p>\n<p lang="en"><strong>True</strong>: I accept publication via DiVA</p>\n<p lang="en"><strong>False</strong>: I do not accept publication via DiVA</p>\n<p lang="en"><strong>Note that in all cases the report is public and KTH must provide a copy to anyone on request.</strong></p>\n</div>\n<div id="fragment-2">\n<p lang="sv">Ger du KTH tillstånd att publicera hela din slutliga exjobbsrapport elektroniskt i databasen DiVA?</p>\n<p lang="sv"><strong>Sant:</strong> Jag godkänner publicering via DiVA</p>\n<p lang="sv"><strong>Falskt:</strong> Jag godkänner inte publicering via DiVA</p>\n<p lang="sv"><strong>Observera att din slutliga exjobbsrapport alltid är offentlig, och att KTH alltid måste tillhandahålla en kopia om någon begär det.</strong></p>\n</div>'
    create_question_boolean(course_id, survey, index, 'Publishing in DiVA', diva, [{'answer_comments': '', 'answer_weight': 100, 'answer_text': 'True/Sant'}, {'answer_comments': '', 'answer_weight': 0, 'answer_text': 'False/Falskt'}])
    index += 1


    course_code='''<p>Kurskod/Course code: Pass/Fail grading (standard): [PF] or Graded A-F/Betygsatt exjobb (A-F): [AF]</p>'''
    course_code_answers=course_code_alternatives(PF_courses, AF_courses)
    course_code_description=course_code_descriptions(PF_courses, AF_courses, relevant_courses_English, relevant_courses_Swedish)
    create_question_multiple_dropdowns(course_id, survey, index, 'Kurskod/Course code', course_code_description+course_code, course_code_answers)
    index += 1
        

    prelim_title='<div class="enhanceable_content tabs"><ul>\n<li lang="en"><a href="#fragment-1">English</a></li>\n<li lang="sv"><a href="#fragment-2">På svenska</a></li>\n</ul>\n<div id="fragment-1">\n<p lang="en">Tentative title\n</p>\n</div>\n<div id="fragment-2">\n<p lang="sv">Preliminär titel\n</p>\n</div>'
    create_question_essay(course_id, survey, index, 'Preliminär titel/Tentative title', prelim_title)
    index += 1

    # examiner
    examiner_question='''<div class="enhanceable_content tabs"><ul><li lang="en"><a href="#fragment-1">English</a></li><li lang="sv"><a href="#fragment-2">P&aring; svenska</a></li></ul><div id="fragment-1"><p lang="en">Potential examiner:</p></div><div id="fragment-2"><p lang="sv">F&ouml;rslag p&aring; examinator:</p></div></div><p> [e1]</p>'''

    course_code_description=course_code_descriptions(PF_courses, AF_courses, relevant_courses_English, relevant_courses_Swedish)
    examiner_answers=potential_examiners_answer(examiners)
    create_question_multiple_dropdowns(course_id, survey, index, 'Examinator/Examiner', examiner_question, examiner_answers)
    index += 1


    start_date='<div class="enhanceable_content tabs"><ul><li lang="en"><a href="#fragment-1">English</a></li><li lang="sv"><a href="#fragment-2">P&aring; svenska</a></li></ul><div id="fragment-1"><p lang="en">Planned start:</p></div><div id="fragment-2"><p lang="sv">Startdatum:</p></div></div><p>[year].[month].[day]</p>' 
    start_date_answers=[{'weight': 100, 'text': '2018', 'blank_id': 'year'},
                        {'weight': 100, 'text': '2019', 'blank_id': 'year'},
                        {'weight': 100, 'text': '2020', 'blank_id': 'year'},
                        {'weight': 100, 'text': '01', 'blank_id': 'month'},
                        {'weight': 100, 'text': '02', 'blank_id': 'month'},
                        {'weight': 100, 'text': '03', 'blank_id': 'month'},
                        {'weight': 100, 'text': '04', 'blank_id': 'month'},
                        {'weight': 100, 'text': '05', 'blank_id': 'month'},
                        {'weight': 100, 'text': '06', 'blank_id': 'month'},
                        {'weight': 100, 'text': '07', 'blank_id': 'month'},
                        {'weight': 100, 'text': '08', 'blank_id': 'month'},
                        {'weight': 100, 'text': '09', 'blank_id': 'month'},
                        {'weight': 100, 'text': '10', 'blank_id': 'month'},
                        {'weight': 100, 'text': '11', 'blank_id': 'month'},
                        {'weight': 100, 'text': '12', 'blank_id': 'month'},
                        {'weight': 100, 'text': '01', 'blank_id': 'day'},
                        {'weight': 100, 'text': '02', 'blank_id': 'day'},
                        {'weight': 100, 'text': '03', 'blank_id': 'day'},
                        {'weight': 100, 'text': '04', 'blank_id': 'day'},
                        {'weight': 100, 'text': '05', 'blank_id': 'day'},
                        {'weight': 100, 'text': '06', 'blank_id': 'day'},
                        {'weight': 100, 'text': '07', 'blank_id': 'day'},
                        {'weight': 100, 'text': '08', 'blank_id': 'day'},
                        {'weight': 100, 'text': '09', 'blank_id': 'day'},
                        {'weight': 100, 'text': '10', 'blank_id': 'day'},
                        {'weight': 100, 'text': '11', 'blank_id': 'day'},
                        {'weight': 100, 'text': '12', 'blank_id': 'day'},
                        {'weight': 100, 'text': '13', 'blank_id': 'day'},
                        {'weight': 100, 'text': '14', 'blank_id': 'day'},
                        {'weight': 100, 'text': '15', 'blank_id': 'day'},
                        {'weight': 100, 'text': '16', 'blank_id': 'day'},
                        {'weight': 100, 'text': '17', 'blank_id': 'day'},
                        {'weight': 100, 'text': '18', 'blank_id': 'day'},
                        {'weight': 100, 'text': '19', 'blank_id': 'day'},
                        {'weight': 100, 'text': '20', 'blank_id': 'day'},
                        {'weight': 100, 'text': '21', 'blank_id': 'day'},
                        {'weight': 100, 'text': '22', 'blank_id': 'day'},
                        {'weight': 100, 'text': '23', 'blank_id': 'day'},
                        {'weight': 100, 'text': '24', 'blank_id': 'day'},
                        {'weight': 100, 'text': '25', 'blank_id': 'day'},
                        {'weight': 100, 'text': '26', 'blank_id': 'day'},
                        {'weight': 100, 'text': '27', 'blank_id': 'day'},
                        {'weight': 100, 'text': '28', 'blank_id': 'day'},
                        {'weight': 100, 'text': '29', 'blank_id': 'day'},
                        {'weight': 100, 'text': '30', 'blank_id': 'day'},
                        {'weight': 100, 'text': '31', 'blank_id': 'day'}]

    create_question_multiple_dropdowns(course_id, survey, index, 'Startdatum/Planned start', start_date, start_date_answers)
    index += 1

    company='<div class="enhanceable_content tabs"><ul><li lang="en"><a href="#fragment-1">English</a></li><li lang="sv"><a href="#fragment-2">På svenska</a></li></ul><div id="fragment-1"><p lang="en">At a company, indicate name:</p></div><div id="fragment-2"><p lang="sv">På företag, ange vilket</p></div>'
    create_question_essay(course_id, survey, index, 'På företag, ange vilket/At a company, indicate name', company)
    index += 1

    country='<div class="enhanceable_content tabs"><ul><li lang="en"><a href="#fragment-1">English</a></li><li lang="sv"><a href="#fragment-2">På svenska</a></li></ul><div id="fragment-1"><p lang="en">Outside Sweden, indic. Country (Enter two character country code)</p></div><div id="fragment-2"><p lang="sv">Utomlands, ange land (Ange landskod med två tecken)</p></div>'
    create_question_short_answer_question(course_id, survey, index, 'Utomlands, ange land/Outside Sweden, indic. Country', country)
    index += 1

    university='<div class="enhanceable_content tabs">\n<ul><li lang="en"><a href="#fragment-1">English</a></li><li lang="sv"><a href="#fragment-2">P&aring; svenska</a></li></ul><div id="fragment-1"><p lang="en">At another university</p></div><div id="fragment-2"><p lang="sv">P&aring; annan h&ouml;gskola</p></div></div>'
    create_question_essay(course_id, survey, index, 'På annan högskola/At another university', university)
    index += 1

    contact='<div class="enhanceable_content tabs">\n<ul><li lang="en"><a href="#fragment-1">English</a></li><li lang="sv"><a href="#fragment-2">P&aring; svenska</a></li></ul><div id="fragment-1"><p lang="en">Enter the name and contact details of your contact at a company, other university, etc.</p></div><div id="fragment-2"><p lang="sv">Ange namn, e-postadress och annan kontaktinformation f&ouml;r din kontaktperson vid f&ouml;retaget, det andra universitetet, eller motsvarande.</p></div></div>'
    create_question_essay(course_id, survey, index, 'Kontaktperson/Contact person', contact)
    index += 1


def insert_column_name(course_id, column_name):
    global Verbose_Flag

    # Use the Canvas API to Create a custom gradebook column
    # POST /api/v1/courses/:course_id/custom_gradebook_columns
    #   Create a custom gradebook column
    # Request Parameters:
    #Parameter		Type	Description
    #column[title]	Required	string	no description
    #column[position]		integer	The position of the column relative to other custom columns
    #column[hidden]		boolean	Hidden columns are not displayed in the gradebook
    # column[teacher_notes]		boolean	 Set this if the column is created by a teacher. The gradebook only supports one teacher_notes column.

    url = "{0}/courses/{1}/custom_gradebook_columns".format(baseUrl,course_id)
    if Verbose_Flag:
       print("url: {}".format(url))
    payload={'column[title]': column_name}
    r = requests.post(url, headers = header, data=payload)
    if Verbose_Flag:
        print("result of post creating custom column: {}".format(r.text))
    if r.status_code == requests.codes.ok:
        page_response=r.json()
        print("inserted column: {}".format(column_name))
        return True
    return False

def list_custom_columns(course_id):
    columns_found_thus_far=[]
    # Use the Canvas API to get the list of custom column for this course
    #GET /api/v1/courses/:course_id/custom_gradebook_columns

    url = "{0}/courses/{1}/custom_gradebook_columns".format(baseUrl,course_id)
    if Verbose_Flag:
        print("url: {}".format(url))

    r = requests.get(url, headers = header)
    if Verbose_Flag:
        print("result of getting custom_gradebook_columns: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()

        for p_response in page_response:  
            columns_found_thus_far.append(p_response)

        # the following is needed when the reponse has been paginated
        # i.e., when the response is split into pieces - each returning only some of the list of modules
        # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
        while r.links['current']['url'] != r.links['last']['url']:  
            r = requests.get(r.links['next']['url'], headers=header)  
            page_response = r.json()  
            for p_response in page_response:  
                columns_found_thus_far.append(p_response)

    return columns_found_thus_far

def create_custom_columns(course_id, cycle_number):
    existing_columns=list_custom_columns(course_id)
    print("existing_columns={}".format(existing_columns))

    column_names=['Group', 'Course_code', 'Planned_start_date', 'Tentative_title', 'Examiner', 'Supervisor', 'KTH_unit', 'Place', 'Contact', 'Student_approves_fulltext', 'TRITA', 'DiVA_URN', 'GA_Approval', 'Ladok_Final_grade_entered']

    if cycle_number == '2':
        column_names.remove('Group') # as 2nd cycle degree projects can only be done by individual students

    for c in existing_columns:  # no need to insert existing columns
        column_names.remove(c)

    for c in column_names:
        insert_column_name(course_id, c)

def sections_in_course(course_id):
    sections_found_thus_far=[]
    # Use the Canvas API to get the list of sections for this course
    #GET /api/v1/courses/:course_id/section

    url = "{0}/courses/{1}/sections".format(baseUrl,course_id)
    if Verbose_Flag:
        print("url: {}".format(url))

    r = requests.get(url, headers = header)
    if Verbose_Flag:
        print("result of getting sections: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()

        for p_response in page_response:  
            sections_found_thus_far.append(p_response)

        # the following is needed when the reponse has been paginated
        # i.e., when the response is split into pieces - each returning only some of the list of modules
        # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
        while r.links['current']['url'] != r.links['last']['url']:  
            r = requests.get(r.links['next']['url'], headers=header)  
            page_response = r.json()  
            for p_response in page_response:  
                sections_found_thus_far.append(p_response)

    return sections_found_thus_far

def create_sections_in_course(course_id, section_names):
    sections_found_thus_far=[]

    # Use the Canvas API to create sections for this course
    #POST /api/v1/courses/:course_id/sections

    url = "{0}/courses/{1}/sections".format(baseUrl,course_id)
    if Verbose_Flag:
        print("url: {}".format(url))

    for section_name in section_names:
        #course_section[name]
        payload={'course_section[name]': section_name}
        r = requests.post(url, headers = header, data=payload)

        if Verbose_Flag:
            print("result of creating section: {}".format(r.text))

        if r.status_code == requests.codes.ok:
            page_response=r.json()

            for p_response in page_response:  
                sections_found_thus_far.append(p_response)

    return sections_found_thus_far

def create_sections_for_examiners_and_programs(course_id, examiners, programs):
    if Verbose_Flag:
        print("create_sections_for_examiners_and_programs({0}, {1}, {2}".format(course_id, examiners, programs))
    create_sections_in_course(course_id, sorted(examiners))

    program_names=[]
    for s in programs:
        program_names.append("Program: {0}-{1}".format(s, programs[s]['title_en'] ))

    create_sections_in_course(course_id, program_names)

def create_course_page(course_id, page_title, page_contents):
    #Create page WikiPagesApiController#create
    #POST /api/v1/courses/:course_id/pages

    url = "{0}/courses/{1}/pages".format(baseUrl,course_id)
    if Verbose_Flag:
        print("url: {}".format(url))

    payload={'wiki_page':
             {
                 'title': page_title,
                 'body': page_contents,
                 'published': 'true'
                 }
    }
    r = requests.post(url, headers = header, json=payload)

    if Verbose_Flag:
        print("result of creating a page: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        page_response=r.json()

    return page_response

def create_module_page_item(course_id, module_id, page_id, item_name, page_url):
    # Use the Canvas API to create a module item in the course and module
    #POST /api/v1/courses/:course_id/modules/:module_id/items
    url = "{0}/courses/{1}/modules/{2}/items".format(baseUrl, course_id, module_id)
    if Verbose_Flag:
        print("creating module assignment item for course_id={0} module_id={1} assignment_id={1}".format(course_id, module_id, page_id))
    payload = {'module_item':
               {
                   'title': item_name,
                   'type': 'Page',
                   'content_id': page_id,
                   'page_url': page_url
               }
    }

    r = requests.post(url, headers = header, json = payload)
    if Verbose_Flag:
        print("result of creating module page item: {}".format(r.text))

    if r.status_code == requests.codes.ok:
        modules_response=r.json()
        module_id=modules_response["id"]
        return module_id
    return  module_id


def create_basic_pages(course_id, cycle_number, existing_modules):
    basic_pages={
        'Introduction': ['Welcome to Degree Project Course, second Cycle /Välkommen',
                         'Grants from KTH Opportunities Fund / Bidrag från KTH Opportunities Fund',
                         'Instructions for degree project / Instruktioner för examensarbete',
                         'Material lectures, templates etc/ Material Föreläsningar, Mallar mm',
                         'Templates/Mallar',
                         'Courses and course codes/Kurser och Kurskod',
                         'After completing degree project/Efter att ha avslutat examensarbete',
                         'Recover from failed degree project/ Återuppta underkänt examensarbete'],

        'Working Material': ['Blank English-Swedish page'],
        'For Faculty': ['Generate cover/Skapa omslag']
        }
    pages_content={'Instructions for degree project / Instruktioner för examensarbete':

'''<p><span lang="en">Degree project for master students, advanced level, 30 credit points</span> (<span lang="sv">Examensarbete för masterstudenter, 30 hp</span>)</p>
<div class="enhanceable_content tabs">
<ul>
<li lang="en"><a href="#fragment-1">English</a></li>
<li lang="sv"><a href="#fragment-2">På svenska</a></li>
</ul>
<div id="fragment-1">
<p lang="en">This information is for students that are going to participate in a degree project course at the Master's level.</p>
<p lang="en">Please read the information concerning the different degree project courses at <a title="Kurser/Courses" href="https://kth.instructure.com/courses/1586/pages/kurser-slash-courses" data-api-endpoint="https://kth.instructure.com/api/v1/courses/1586/pages/kurser-slash-courses" data-api-returntype="Page">Kurser/Courses</a>.</p>
<p lang="en">As a first step, a project proposal must be created and handed in. Templates for the project proposal can be found in <a title="Mallar/Templates" href="https://kth.instructure.com/courses/1586/pages/mallar-slash-templates" data-api-endpoint="https://kth.instructure.com/api/v1/courses/1586/pages/mallar-slash-templates" data-api-returntype="Page">Mallar/Templates</a>. The templates are in Swedish and English and the contents are the same irrespective of language <span>and degree project</span>.</p>
<p lang="en">The project proposal is used for assigning examiners and supervisors. The proposals are also used for evaluating the degree project’s characteristics and scope. Hence, the project proposals serve as a basis for discussion. Even without a specific project, it is still possible to assign an examiner and a supervisor, thus students should hand in their project proposal to indicate their interest area(s). These interest areas are used to assign the most suitable examiner and/or supervisor.</p>
<p lang="en">Fill in the project proposal with available information. If any pieces of information are unknown, please indicate this in the project proposal. Hand in the project proposal by uploading the file via the <a title="Projekt Plan/Project plan" href="https://kth.instructure.com/courses/1586/assignments/4272" data-api-endpoint="https://kth.instructure.com/api/v1/courses/1586/assignments/4272" data-api-returntype="Assignment">Projekt Plan/Project plan </a>assignment.</p>
<p lang="en">A time ordered list of deliverables can be found under <a href="https://kth.instructure.com/courses/1586/assignments" data-api-endpoint="https://kth.instructure.com/api/v1/courses/1586/assignments" data-api-returntype="[Assignment]">Assignments</a>.</p>
</div>
<div id="fragment-2">
<p lang="sv">Denna information gäller för studenter som ska gå examensarbetskurs.</p>
<p lang="sv">Här följer information om examensarbete, på avancerad nivå, för Civ. ingengörer, master med flera.</p>
<p lang="sv">Läs informationen som rör det examensarbete ni ska göra (se <a title="Kurser/Courses" href="https://kth.instructure.com/courses/1586/pages/kurser-slash-courses" data-api-endpoint="https://kth.instructure.com/api/v1/courses/1586/pages/kurser-slash-courses" data-api-returntype="Page">Kurser/Courses</a>).   </p>
<p lang="sv">Oavsett examensarbete ska projektförslag upprättas och lämnas in. Mallar för projektförslag (tidigare kallat projektplan) finns att hämta i <a title="Mallar/Templates" href="https://kth.instructure.com/courses/1586/pages/mallar-slash-templates" data-api-endpoint="https://kth.instructure.com/api/v1/courses/1586/pages/mallar-slash-templates" data-api-returntype="Page">Mallar/Templates</a>. Mallarna är på svenska som engelska och har samma innehåll, det vill säga oavsett språk och examensarbete.</p>
<p lang="sv">Projektförslagen används för att tilldela examinator och handledare. Förslagen är även till för att bedöma examensarbetets karaktär och omfång. Således fungerar projektförslagen även som diskussionsunderlag. Även om projekt saknas, går det att tilldela examinator och handledare, så alla studenter ska lämna in ett projektförslag. I dessa fall, sker tilldelning utifrån intresseområden.</p>
<p lang="sv">Fyll i projektförslaget utifrån den information som finns att tillgå. Om det finns oklarheter med examensarbetet, skriv det i projektförslaget. Lämna in projektförslaget genom att ladda upp filen i <a title="Projekt Plan/Project plan" href="https://kth.instructure.com/courses/1586/assignments/4272" data-api-endpoint="https://kth.instructure.com/api/v1/courses/1586/assignments/4272" data-api-returntype="Assignment">Projekt Plan/Project plan</a> inlämning.</p>
<p lang="sv">En tid ordnad lista över delresultaten finns under <a href="https://kth.instructure.com/courses/1586/assignments" data-api-endpoint="https://kth.instructure.com/api/v1/courses/1586/assignments" data-api-returntype="[Assignment]">Uppgifter</a>.</p>
</div>
</div>''',
                  'Welcome to Degree Project Course, second Cycle /Välkommen':
                  '''
<p><span style="color: red;"></span><span lang="en">Welcome</span> (<span lang="sv">Välkommen</span>)</p>
<div class="enhanceable_content tabs">
<ul>
<li lang="en"><a href="#fragment-en">English</a></li>
<li lang="sv"><a href="#fragment-sv">På svenska</a></li>
</ul>
<p lang="en"> </p>
<p><strong>Information in English <br></strong></p>
<p>Here follows information about degree projects, at the bachelor and master levels.</p>
<p>In the Events Documents folder, there is information about degree projects for bachelor and master, both in Swedish and English. Please read the information that concerns your degree project.</p>
<p>No matter the level of the degree project, a project proposal must be created and handed in. Templates for the project proposal can be found in the File folder. The templates are in Swedish and English and the contents are the same irrespective of language and degree project (bachelor or master).</p>
<p>The project proposal is used to aid the search for examiners and supervisors at KTH. The proposal is also used to assess the degree project’s characteristics and scope. Hence, the project proposal serves as a basis for discussion. In the event of lacking a project, the project proposal is still useful as a declaration of interest in a subject, problem, or research area. The declared areas of interest can then be used to find a suitable examiner and/or supervisor.</p>
<p>Fill in the project proposal with the available information. Information that is unknown should be stated as such, rather than being omitted. <span style="font-size: 1rem;">Hand in the project proposal by uploading the file in the appropriate Canvas activity and assignment. If the degree project is a bachelor degree project, choose the Canvas activity that contains the name “First Cycle”, i.e. bachelor level. If it is a master degree project, choose the activity that contains ”Second Cycle”. Choose the course code that corresponds to your own education program. Choose only one course code and hand in only one degree project proposal. </span></p>
<p><em><strong>OBSERVE: </strong></em>After degree project, you should apply for a degree certificate. For more information, see:</p>
<p><a href="https://www.kth.se/en/student/program/examen/examen-hur-och-var-ansoker-man-1.2234?programme=tebsm">Apply for degree certificate </a></p>
<p> </p>
<div id="fragment-sv">
<p><strong lang="en"> Information på Svenska</strong></p>
<p><em>For information in Swedish, see https://www.kth.se/social/group/examensarbete-ict-sk/</em></p>
</div>
</div>
                  '''
    }

    for m in existing_modules:
        if m['name'] == 'Gatekeeper protected module 1':
            id_of_protected_module=m['id']

    for bp in basic_pages:
        if bp == 'Introduction':
            module_id=check_for_module(course_id,  bp)
            if not module_id:
                module_id=create_module(course_id, bp, id_of_protected_module)
            pages_in_module=basic_pages[bp]
            print("pages_in_module={}".format(pages_in_module))

            for p in pages_in_module:
                print("p={}".format(p))
                page_title=p
                page_content=pages_content.get(p, [])
                print("page_content={}".format(page_content))
                if page_content:                 
                    cp=create_course_page(course_id, page_title, page_content)
                    print("cp={}".format(cp))
                    print("page title={}".format(cp['title']))
                    print("page url={}".format(cp['url']))
                    print("page id={}".format(cp['page_id']))
                    create_module_page_item(course_id, module_id, cp['page_id'], cp['title'], cp['url'])
        else:
            create_module(course_id, bp, None)

def main():
    global Verbose_Flag

    default_picture_size=128

    parser = optparse.OptionParser()

    parser.add_option('-v', '--verbose',
                      dest="verbose",
                      default=False,
                      action="store_true",
                      help="Print lots of output to stdout"
    )
    parser.add_option("--config", dest="config_filename",
                      help="read configuration from FILE", metavar="FILE")

    parser.add_option('-m', '--modules',
                      dest="modules",
                      default=False,
                      action="store_true",
                      help="create the two basic modules"
    )

    parser.add_option('-p', '--pages',
                      dest="pages",
                      default=False,
                      action="store_true",
                      help="create the basic pages"
    )

    parser.add_option('-s', '--survey',
                      dest="survey",
                      default=False,
                      action="store_true",
                      help="create the survey"
    )

    parser.add_option('-S', '--sections',
                      dest="sections",
                      default=False,
                      action="store_true",
                      help="create sections for examiners and programs"
    )

    parser.add_option('-c', '--columns',
                      dest="columns",
                      default=False,
                      action="store_true",
                      help="create the custom columns"
    )

    options, remainder = parser.parse_args()

    Verbose_Flag=options.verbose
    if Verbose_Flag:
        print("ARGV      : {}".format(sys.argv[1:]))
        print("VERBOSE   : {}".format(options.verbose))
        print("REMAINING : {}".format(remainder))
        print("Configuration file : {}".format(options.config_filename))

    initialize(options)

    if (len(remainder) < 2):
        print("Insuffient arguments - must provide cycle_number course_id\n")
    else:
        cycle_number=remainder[0]
        course_id=remainder[1]

        if (options.survey or options.sections) and (len(remainder) > 2):
            school_acronym=remainder[2]

    if options.modules:
        create_basic_modules(course_id)

    existing_modules=list_modules(course_id)
    if Verbose_Flag:
        if existing_modules:
            print("existing_modules={0}".format(existing_modules))

    if options.survey or options.sections:
        if Verbose_Flag:
            print("school_acronym={}".format(school_acronym))
        # compute the list of degree project course codes
        all_dept_codes=get_dept_codes(Swedish_language_code)
        if Verbose_Flag:
            print("all_dept_codes={}".format(all_dept_codes))

        dept_codes=dept_codes_in_a_school(school_acronym, all_dept_codes)
        if Verbose_Flag:
            print("dept_codes={}".format(dept_codes))

        courses_English=degree_project_courses(dept_codes, English_language_code)
        courses_Swedish=degree_project_courses(dept_codes, Swedish_language_code)
        if Verbose_Flag:
            print("courses English={0} and Swedish={1}".format(courses_English, courses_Swedish))
        
        #relevant_courses_English=list(filter(lambda x: x['cycle'] == cycle_number, courses_English))
        #relevant_courses_Swedish=list(filter(lambda x: x['cycle'] == cycle_number, courses_Swedish))

        relevant_courses_English=dict()
        for c in courses_English:
            if c['cycle'] == cycle_number:
                relevant_courses_English[c['code']]=c

        relevant_courses_Swedish=dict()
        for c in courses_Swedish:
            if c['cycle'] == cycle_number:
                relevant_courses_Swedish[c['code']]=c

        if Verbose_Flag:
            print("relevant_courses English={0} and Swedish={1}".format(relevant_courses_English, relevant_courses_Swedish))
            # relevant courses are of the format:{'code': 'II246X', 'title': 'Degree Project in Computer Science and Engineering, Second Cycle', 'href': 'https://www.kth.se/student/kurser/kurs/II246X?l=en', 'info': '', 'credits': '30.0', 'level': 'Second cycle', 'state': 'ESTABLISHED', 'dept_code': 'J', 'department': 'EECS/School of Electrical Engineering and Computer Science', 'cycle': '2', 'subject': 'Degree Project in Computer Science and Engineering'},

        grading_scales=course_gradingscale(relevant_courses_Swedish)
        PF_courses=[]
        for i in grading_scales:
            if grading_scales[i] == 'PF':
                PF_courses.append(i)

        AF_courses=[]
        for i in grading_scales:
            if grading_scales[i] == 'AF':
                AF_courses.append(i)

        if Verbose_Flag:
            print("PF_courses={0} and AF_courses={1}".format(PF_courses, AF_courses))

        all_course_examiners=course_examiners(relevant_courses_Swedish)
        # list of names of those who are no longer examiners at KTH
        examiners_to_remove = [ 'Anne Håkansson',  'Jiajia Chen',  'Paolo Monti',  'Lirong Zheng']
    
        all_examiners=set()
        for course in all_course_examiners:
            for e in all_course_examiners[course]:
                all_examiners.add(e)

        # clean up list of examiners - removing those who should no longer be listed, but are listed in KOPPS
        for e in examiners_to_remove:
            if Verbose_Flag:
                print("examiner to remove={}".format(e))
            if e in all_examiners:
                all_examiners.remove(e)

    if options.survey:
        create_survey(course_id, cycle_number, school_acronym, PF_courses, AF_courses, relevant_courses_English, relevant_courses_Swedish, all_examiners)

    if options.sections:
        all_programs=programs_and_owner_and_titles()
        programs_in_the_school=programs_in_school(all_programs, school_acronym)
        programs_in_the_school_with_titles=programs_in_school_with_titles(all_programs, school_acronym)
        create_sections_for_examiners_and_programs(course_id, all_examiners, programs_in_the_school_with_titles)

    if options.columns:
        create_custom_columns(course_id, cycle_number)
        
    if options.pages:
        create_basic_pages(course_id, cycle_number, existing_modules)
        

if __name__ == "__main__": main()


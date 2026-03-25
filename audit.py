#!/usr/bin/env python3

import sys, os, yaml
import argparse
from canvasapi import Canvas

def check_syllabus_visibility(course, term, update=False):
    """For a specific course, check that course is:
     - in this term and published
     - has a syllabus visible to the institution (public_syllabus_to_auth)
       or is otherwise public
    """
    if course.enrollment_term_id != term:
        return 0
    if course.workflow_state != 'available':
        return 0

    problem_tabs = [t for t in course.get_tabs() if t.id == 'syllabus' and hasattr(t, 'hidden') and t.hidden == True]
    if len(problem_tabs) > 0:
        print("***", course.name, "has syllabus page hidden")

    if course.public_syllabus_to_auth or course.public_syllabus:
        return 0
    print("-->", course.name, course.workflow_state, course.enrollment_term_id)

    if update:
        if not (course.public_syllabus_to_auth or course.public_syllabus):
            course.update(course={'public_syllabus_to_auth':True})
    return 1

def check_access_time(course, term, update=False):
    """For a specific course, check that course is:
     - in this term and published
     - has a the start and end dates defined by the term's definition
    """
    if not hasattr(course, 'name') or not hasattr(course, 'enrollment_term_id'):
        return 0

    if course.enrollment_term_id != term:
        return 0
    if course.workflow_state != 'available':
        return 0
    
    if course.restrict_enrollments_to_course_dates is False:
        # this means course start/end is igored, in favor of term start/end
        # https://canvas.instructure.com/doc/api/courses.html
        return 0
    print("-->", course.name, course.restrict_enrollments_to_course_dates, course.start_at, course.end_at)

    if update:
        if course.restrict_enrollments_to_course_dates:
            course.update(course={'restrict_enrollments_to_course_dates':False})
    return 1

def check_all_syllabi(OPT):
    """Counts, and optionally updates, all courses
    """
    canvas = Canvas(OPT['API_URL'], OPT['API_KEY'])

    atotal = vtotal = 0
    no_accounts_found = True

    for a in canvas.get_accounts():
        print(a.id, a.name)
        no_accounts_found = False
        for c in a.get_courses(enrollment_term_id=OPT['TERM'], published=True):
            if OPT['visibility']:
                vtotal += check_syllabus_visibility(c, term=OPT['TERM'], update=OPT['update'])
            if OPT['access']:
                atotal += check_access_time(c, term=OPT['TERM'], update=OPT['update'])

    if no_accounts_found:
        # we are apparently not being run from an admin account
        for c in canvas.get_courses(enrollment_term_id=OPT['TERM'], published=True):
            if OPT['visibility']:
                vtotal += check_syllabus_visibility(c, term=OPT['TERM'], update=OPT['update'])
            if OPT['access']:
                atotal += check_access_time(c, term=OPT['TERM'], update=OPT['update'])

    if OPT['access']:
        if not OPT['update']:
            print("There are", atotal, "courses that were not accessible per term timeline")
        else:
            print("There were", atotal, "courses that were updated to match term")

    if OPT['visibility']:
        if not OPT['update']:
            print("There are", vtotal, "courses that are not accessible")
        else:
            print("There were", vtotal, "courses that were updated")

if __name__ == '__main__':
    """Audits to see if syllabi are available at the institutional level
    """
    parser = argparse.ArgumentParser(description='Scrape Canvas syllabi',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--config", type=str, 
        dest='config', required=True,
        help="Path to YAML config file")
    parser.add_argument("--access", action='store_true',
        dest='access', default=False, required=False,
        help="To check course start/end access times")
    parser.add_argument("--visibility", action='store_true',
        dest='visibility', default=False, required=False,
        help="To check visibility")
    parser.add_argument("--update", action='store_true',
        dest='update', default=False, required=False,
        help="To update visibility")
    parser.add_argument("--verbose", action='store_true',
        dest='verbose', default=False, required=False)
    OPT = vars(parser.parse_args())

    # get options from the yml config file
    try:
        with open(OPT['config'], 'r') as file:
            config = yaml.load(file)
            OPT.update(config)
    except yaml.YAMLError as e:
        print("Error in configuration file:", e)

    check_all_syllabi(OPT)



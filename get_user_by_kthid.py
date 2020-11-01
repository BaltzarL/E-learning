#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# ./get_user_by_kthid.py kthid
#
# Output: user information
#
#
# "-t" or "--testing" to enable small tests to be done
# 
#
# with the option "-v" or "--verbose" you get lots of output - showing in detail the operations of the program
#
# Can also be called with an alternative configuration file:
# ./get_user_by_kthid.py u1d13i2c
#
# Example:
#
#   ./get_user_by_kthid.py --config config-test.json u1d13i2c
#
# ./get_user_by_kthid.py u1d13i2c
# user={'defaultLanguage': 'en', 'acceptedTerms': True, 'isAdminHidden': False, 'avatar': {'visibility': 'public'}, '_id': 'u1d13i2c', 'kthId': 'u1d13i2c', 'username': 'maguire', 'homeDirectory': '\\\\ug.kth.se\\dfs\\home\\m\\a\\maguire', 'title': {'sv': 'PROFESSOR', 'en': 'PROFESSOR'}, 'streetAddress': 'ISAFJORDSGATAN 26', 'emailAddress': 'maguire@kth.se', 'telephoneNumber': '', 'isStaff': True, 'isStudent': False, 'firstName': 'Gerald Quentin', 'lastName': 'Maguire Jr', 'city': 'Stockholm', 'postalCode': '10044', 'remark': 'COMPUTER COMMUNICATION LAB', 'lastSynced': '2020-10-28T13:36:56.000Z', 'researcher': {'researchGate': '', 'googleScholarId': 'HJgs_3YAAAAJ', 'scopusId': '8414298400', 'researcherId': 'G-4584-2011', 'orcid': '0000-0002-6066-746X'}, 'courses': {'visibility': 'public', 'codes': ['II2202', 'II246X', 'IL226X', 'II123X', 'II143X', 'IK2553', 'II142X', 'IL246X', 'II245X', 'IL228X', 'IT225X', 'IK1552', 'IK2555', 'II122X', 'IL142X', 'IL248X', 'IF245X', 'IT245X', 'II226X', 'IL122X', 'II225X', 'IF225X', 'IK2560', 'II2210', 'EA256X', 'IA250X', 'DA246X', 'IA150X', 'EA258X', 'EA246X', 'DA240X', 'DA256X', 'DA258X'], 'items': [{'title': {'sv': 'Forskningsmetodik och vetenskapligt skrivande', 'en': 'Research Methodology and Scientific Writing'}, 'roles': ['examiner', 'courseresponsible', 'teachers'], 'code': 'II2202', 'koppsUrl': 'https://www.kth.se/student/kurser/kurs/II2202', 'courseWebUrl': 'https://www.kth.se/social/course/II2202/'}, {'title': {'sv': 'Examensarbete inom datalogi och datateknik, avancerad nivå', 'en': 'Degree Project in Computer Science and Engineering, Second Cycle'}, 'roles': ['examiner'], 'code': 'II246X', 'koppsUrl': 'https://www.kth.se/student/kurser/kurs/II246X', 'courseWebUrl': 'https://www.kth.se/social/course/II246X/'}, {'title': {'sv': 'Examensarbete inom elektroteknik, avancerad nivå', 'en': 'Degree Project in Electrical Engineering, Second Cycle'}, 'roles': ['examiner'], 'code': 'IL226X', 'koppsUrl': 'https://www.kth.se/student/kurser/kurs/IL226X', 'courseWebUrl': 'https://www.kth.se/social/course/IL226X/'}, {'title': {'sv': 'Examensarbete inom informations- och kommunikationsteknik, grundnivå', 'en': 'Degree Project in Information and Communication Technology, First Cycle'}, 'roles': ['examiner'], 'code': 'II123X', 'koppsUrl': 'https://www.kth.se/student/kurser/kurs/II123X', 'courseWebUrl': 'https://www.kth.se/social/course/II123X/'}, {'title': {'sv': 'Examensarbete inom informations- och kommunikationsteknik, grundnivå', 'en': 'Degree Project in Information and  Communication Technology, First Cycle'}, 'roles': ['examiner'], 'code': 'II143X', 'koppsUrl': 'https://www.kth.se/student/kurser/kurs/II143X', 'courseWebUrl': 'https://www.kth.se/social/course/II143X/'}, {'title': {'sv': 'Projekt i datorkommunikation', 'en': 'Project in Computer Communication'}, 'roles': ['examiner'], 'code': 'IK2553', 'koppsUrl': 'https://www.kth.se/student/kurser/kurs/IK2553', 'courseWebUrl': 'https://www.kth.se/social/course/IK2553/'}, {'title': {'sv': 'Examensarbete inom datateknik, grundnivå', 'en': 'Degree Project in Computer Engineering, First Cycle'}, 'roles': ['examiner'], 'code': 'II142X', 'koppsUrl': 'https://www.kth.se/student/kurser/kurs/II142X', 'courseWebUrl': 'https://www.kth.se/social/course/II142X/'}, {'title': {'sv': 'Examensarbete inom elektroteknik, avancerad nivå', 'en': 'Degree Project in Electrical Engineering, Second Cycle'}, 'roles': ['examiner'], 'code': 'IL246X', 'koppsUrl': 'https://www.kth.se/student/kurser/kurs/IL246X', 'courseWebUrl': 'https://www.kth.se/social/course/IL246X/'}, {'title': {'sv': 'Examensarbete inom informations- och kommunikationsteknik, avancerad nivå', 'en': 'Degree Project in Information and Communication Technology, Second Cycle'}, 'roles': ['examiner'], 'code': 'II245X', 'koppsUrl': 'https://www.kth.se/student/kurser/kurs/II245X', 'courseWebUrl': 'https://www.kth.se/social/course/II245X/'}, {'title': {'sv': 'Examensarbete inom informations- och kommunikationsteknik, avancerad nivå', 'en': 'Degree Project in Information and Communication Technology, Second Cycle'}, 'roles': ['examiner'], 'code': 'IL228X', 'koppsUrl': 'https://www.kth.se/student/kurser/kurs/IL228X', 'courseWebUrl': 'https://www.kth.se/social/course/IL228X/'}, {'title': {'sv': 'Examensarbete inom mikroelektronik, avancerad nivå', 'en': 'Degree Project in Micro Electronics, Second Cycle'}, 'roles': ['examiner'], 'code': 'IT225X', 'koppsUrl': 'https://www.kth.se/student/kurser/kurs/IT225X', 'courseWebUrl': 'https://www.kth.se/social/course/IT225X/'}, {'title': {'sv': 'Internetteknik', 'en': 'Internetworking'}, 'roles': ['examiner', 'courseresponsible', 'teachers'], 'code': 'IK1552', 'koppsUrl': 'https://www.kth.se/student/kurser/kurs/IK1552', 'courseWebUrl': 'https://www.kth.se/social/course/IK1552/'}, {'title': {'sv': 'Trådlösa och mobila nätverksarkitekturer', 'en': 'Wireless and Mobile Network Architectures'}, 'roles': ['examiner', 'courseresponsible', 'teachers'], 'code': 'IK2555', 'koppsUrl': 'https://www.kth.se/student/kurser/kurs/IK2555', 'courseWebUrl': 'https://www.kth.se/social/course/IK2555/'}, {'title': {'sv': 'Examensarbete inom datateknik, grundnivå', 'en': 'Degree Project in Computer Engineering, First Cycle'}, 'roles': ['examiner'], 'code': 'II122X', 'koppsUrl': 'https://www.kth.se/student/kurser/kurs/II122X', 'courseWebUrl': 'https://www.kth.se/social/course/II122X/'}, {'title': {'sv': 'Examensarbete inom elektronik och datorteknik, grundnivå', 'en': 'Degree Project in Electronics and Computer Engineering, First Cycle'}, 'roles': ['examiner'], 'code': 'IL142X', 'koppsUrl': 'https://www.kth.se/student/kurser/kurs/IL142X', 'courseWebUrl': 'https://www.kth.se/social/course/IL142X/'}, {'title': {'sv': 'Examensarbete inom informations- och kommunikationsteknik, avancerad nivå', 'en': 'Degree Project in Information and Communication Technology, Second Cycle'}, 'roles': ['examiner'], 'code': 'IL248X', 'koppsUrl': 'https://www.kth.se/student/kurser/kurs/IL248X', 'courseWebUrl': 'https://www.kth.se/social/course/IL248X/'}, {'title': {'sv': 'Examensarbete inom mikroelektronik, avancerad nivå', 'en': 'Degree Project in Micro Electronics, Second Cycle'}, 'roles': ['examiner'], 'code': 'IF245X', 'koppsUrl': 'https://www.kth.se/student/kurser/kurs/IF245X', 'courseWebUrl': 'https://www.kth.se/social/course/IF245X/'}, {'title': {'sv': 'Examensarbete inom mikroelektronik, avancerad nivå', 'en': 'Degree Project in Micro Electronics, Second Cycle'}, 'roles': ['examiner'], 'code': 'IT245X', 'koppsUrl': 'https://www.kth.se/student/kurser/kurs/IT245X', 'courseWebUrl': 'https://www.kth.se/social/course/IT245X/'}, {'title': {'sv': 'Examensarbete inom datalogi och datateknik, avancerad nivå', 'en': 'Degree Project in Computer Science and Engineering, Second Cycle'}, 'roles': ['examiner'], 'code': 'II226X', 'koppsUrl': 'https://www.kth.se/student/kurser/kurs/II226X', 'courseWebUrl': 'https://www.kth.se/social/course/II226X/'}, {'title': {'sv': 'Examensarbete inom elektronik och datorteknik, grundnivå', 'en': 'Degree Project in Electronics and Computer Engineering, First Cycle'}, 'roles': ['examiner'], 'code': 'IL122X', 'koppsUrl': 'https://www.kth.se/student/kurser/kurs/IL122X', 'courseWebUrl': 'https://www.kth.se/social/course/IL122X/'}, {'title': {'sv': 'Examensarbete inom informations- och kommunikationsteknik, avancerad nivå', 'en': 'Degree Project in Information and Communication Technology, Second Cycle'}, 'roles': ['examiner'], 'code': 'II225X', 'koppsUrl': 'https://www.kth.se/student/kurser/kurs/II225X', 'courseWebUrl': 'https://www.kth.se/social/course/II225X/'}, {'title': {'sv': 'Examensarbete inom mikroelektronik, avancerad nivå', 'en': 'Degree Project in Micro Electronics, Second Cycle'}, 'roles': ['examiner'], 'code': 'IF225X', 'koppsUrl': 'https://www.kth.se/student/kurser/kurs/IF225X', 'courseWebUrl': 'https://www.kth.se/social/course/IF225X/'}, {'title': {'sv': 'Mobila nätverk och tjänster', 'en': 'Mobile Networks and Services'}, 'roles': ['teachers'], 'code': 'IK2560', 'koppsUrl': 'https://www.kth.se/student/kurser/kurs/IK2560', 'courseWebUrl': 'https://www.kth.se/social/course/IK2560/'}, {'title': {'sv': 'Etik och hållbar utveckling för ingenjörer', 'en': 'Ethics and Sustainable Development for Engineers'}, 'roles': ['examiner', 'courseresponsible', 'teachers'], 'code': 'II2210', 'koppsUrl': 'https://www.kth.se/student/kurser/kurs/II2210', 'courseWebUrl': 'https://www.kth.se/social/course/II2210/'}, {'title': {'sv': 'Examensarbete inom elektroteknik med inriktning mot ICT innovation, avancerad nivå', 'en': 'Degree Project in Electrical Engineering, specialising in ICT Innovation, Second Cycle'}, 'roles': ['examiner'], 'code': 'EA256X', 'koppsUrl': 'https://www.kth.se/student/kurser/kurs/EA256X', 'courseWebUrl': 'https://www.kth.se/social/course/EA256X/'}, {'title': {'sv': 'Examensarbete inom informationsteknik, avancerad niva', 'en': 'Degree Project in Information and Communication Technology, Second Cycle'}, 'roles': ['examiner'], 'code': 'IA250X', 'koppsUrl': 'https://www.kth.se/student/kurser/kurs/IA250X', 'courseWebUrl': 'https://www.kth.se/social/course/IA250X/'}, {'title': {'sv': 'Examensarbete inom datalogi och datateknik med inriktning mot kommunikationssystem, avancerad nivå', 'en': 'Degree Project in Computer Science and Engineering, specialising in Communication Systems, Second Cycle'}, 'roles': ['examiner'], 'code': 'DA246X', 'koppsUrl': 'https://www.kth.se/student/kurser/kurs/DA246X', 'courseWebUrl': 'https://www.kth.se/social/course/DA246X/'}, {'title': {'sv': 'Examensarbete inom informationsteknik, grundnivå', 'en': 'Degree Project in Information and Communication Technology, First Cycle'}, 'roles': ['examiner'], 'code': 'IA150X', 'koppsUrl': 'https://www.kth.se/student/kurser/kurs/IA150X', 'courseWebUrl': 'https://www.kth.se/social/course/IA150X/'}, {'title': {'sv': 'Examensarbete inom elektroteknik med inriktning mot ICT innovation, avancerad nivå', 'en': 'Degree Project in Electrical Engineering, specialising in ICT Innovation, Second Cycle'}, 'roles': ['examiner'], 'code': 'EA258X', 'koppsUrl': 'https://www.kth.se/student/kurser/kurs/EA258X', 'courseWebUrl': 'https://www.kth.se/social/course/EA258X/'}, {'title': {'sv': 'Examensarbete inom elektroteknik med inriktning mot kommunikationssystem, avancerad nivå', 'en': 'Degree Project in Electrical Engineering, specializing in Communication Systems, Second Cycle'}, 'roles': ['examiner'], 'code': 'EA246X', 'koppsUrl': 'https://www.kth.se/student/kurser/kurs/EA246X', 'courseWebUrl': 'https://www.kth.se/social/course/EA246X/'}, {'title': {'sv': 'Examensarbete inom datalogi och datateknik med inriktning mot programvaruteknik för distribuerade system, avancerad nivå', 'en': 'Degree Project in Computer Science and Engineering, specializing in Software Engineering for Distributed Systems, Second Cycle'}, 'roles': ['examiner'], 'code': 'DA240X', 'koppsUrl': 'https://www.kth.se/student/kurser/kurs/DA240X', 'courseWebUrl': 'https://www.kth.se/social/course/DA240X/'}, {'title': {'sv': 'Examensarbete inom datalogi och datateknik med inriktning mot ICT innovation, avancerad nivå', 'en': 'Degree Project in Computer Science and Engineering, specialising in ICT Innovation, Second Cycle'}, 'roles': ['examiner'], 'code': 'DA256X', 'koppsUrl': 'https://www.kth.se/student/kurser/kurs/DA256X', 'courseWebUrl': 'https://www.kth.se/social/course/DA256X/'}, {'title': {'sv': 'Examensarbete inom datalogi och datateknik med inriktning mot ICT innovation, avancerad nivå', 'en': 'Degree Project in Computer Science and Engineering, specialising in ICT Innovation, Second Cycle'}, 'roles': ['examiner'], 'code': 'DA258X', 'koppsUrl': 'https://www.kth.se/student/kurser/kurs/DA258X', 'courseWebUrl': 'https://www.kth.se/social/course/DA258X/'}]}, 'worksFor': {'items': [{'key': 'app.katalog3.J.JH', 'path': 'j/jh', 'location': '', 'name': 'CS DATAVETENSKAP', 'nameEn': 'DEPARTMENT OF COMPUTER SCIENCE'}, {'key': 'app.katalog3.J.JH.JHF', 'path': 'j/jh/jhf', 'location': 'KISTAGÅNGEN 16, 16440 KISTA', 'name': 'KOMMUNIKATIONSSYSTEM', 'nameEn': 'DIVISION OF COMMUNICATION SYSTEMS'}]}, 'pages': [], 'links': {'visibility': 'public', 'items': [{'url': 'http://people.kth.se/~maguire/', 'name': 'Personal web page at KTH'}, {'url': 'https://www.ae-info.org/ae/Member/Maguire_Jr._Gerald_Quentin', 'name': 'page at Academia Europaea'}]}, 'description': {'visibility': 'public', 'sv': '<p>Om du verkligen vill kontakta mig eller hitta information om mig, se min hemsida:\xa0<a href="http://people.kth.se/~maguire/">http://people.kth.se/~maguire/</a></p>\r\n', 'en': '<p>If you actually want to contact me or find information related to me, see my web page:\xa0<a href="http://people.kth.se/~maguire/">http://people.kth.se/~maguire/</a></p>\r\n'}, 'images': {'big': 'https://www.kth.se/social/files/576d7ae3f2765459470e7b0e/chip-identicon-52e6e0ae2260166c91cd528ba0c72263_large.png', 'visibility': 'public'}, 'room': {'placesId': 'fad3809a-344b-4572-9795-5b423e0a9b2a', 'title': '4478'}, 'socialId': '55564', 'createdAt': '2006-01-09T13:13:59.000Z', 'visibility': 'public'}
#
# G. Q. Maguire Jr.
#
#
# 2020.11.01
#

import requests, time
import pprint
import optparse
import sys
import json

# Use Python Pandas to create XLSX files
import pandas as pd

global host	# the base URL
global header	# the header for all HTML requests
global payload	# place to store additionally payload when needed for options to HTML requests

# 
def initialize(options):
       global host, header, payload

       # styled based upon https://martin-thoma.com/configuration-files-in-python/
       if options.config_filename:
              config_file=options.config_filename
       else:
              config_file='config.json'

       try:
              with open(config_file) as json_data_file:
                     configuration = json.load(json_data_file)
                     key=configuration["KTH_API"]["key"]
                     host=configuration["KTH_API"]["host"]
                     header = {'api_key': key, 'Content-Type': 'application/json', 'Accept': 'application/json' }
                     payload = {}
       except:
              print("Unable to open configuration file named {}".format(config_file))
              print("Please create a suitable configuration file, the default name is config.json")
              sys.exit()


def get_user_by_kthid(kthid):
       # Use the KTH API to get the user information give an orcid
       #"#{$kth_api_host}/profile/v1/kthId/#{kthid}"

       url = "{0}/profile/v1/kthId/{1}".format(host, kthid)
       if Verbose_Flag:
              print("url: {}".format(url))

       r = requests.get(url, headers = header)
       if Verbose_Flag:
              print("result of getting profile: {}".format(r.text))

       if r.status_code == requests.codes.ok:
              page_response=r.json()
              return page_response
       return []


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

    parser.add_option('-t', '--testing',
                      dest="testing",
                      default=False,
                      action="store_true",
                      help="execute test code"
    )

    options, remainder = parser.parse_args()

    Verbose_Flag=options.verbose
    if Verbose_Flag:
        print("ARGV      : {}".format(sys.argv[1:]))
        print("VERBOSE   : {}".format(options.verbose))
        print("REMAINING : {}".format(remainder))
        print("Configuration file : {}".format(options.config_filename))

    initialize(options)

    if (len(remainder) < 1):
        print("Insuffient arguments - must provide kthid")
        sys.exit()
    else:
        kthid=remainder[0]
    if options.testing:
        print("testing for kthid={}".format(kthid))

    user=get_user_by_kthid(kthid)
    print("user={}".format(user))

if __name__ == "__main__": main()


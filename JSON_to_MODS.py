#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- mode: python; python-indent-offset: 4 -*-
#
# ./JSON_to_MODS.py [-c course_id] --json file.json [--cycle 1|2] [--credits 7.5|15.0|30.0|50.0] [--exam 1|2|3|4|5|6|7|8 or or the name of the exam] [--area area_of_degree] [--area2 area_of_second_degree] [--trita trita_string] [--school ABE|CBH|EECS|ITM|SCI]
#
# Purpose: The program creates a MODS file using the information from the arguments and a JSON file.
# The JSON file can be produced by extract_pseudo_JSON-from_PDF.py
#
# Output: outputs the MODS file: MODS.pdf
#
# Example:
#  enter data from a JSON file
# ./JSON_to_MODS.py -c 11  --json event.json
# ./JSON_to_MODS.py -c 11 --config config-test.json  --json oscar.json
#
# ./JSON_to_MODS.py -c 11  --json event.json --testing --exam 4
#
#
# The dates from Canvas are in ISO 8601 format.
# 
# 2021-06-25 G. Q. Maguire Jr.
# Base on earlier xmlGenerator.py and JSON_to_cover.py
#

import re
import sys

import json
import argparse
import os			# to make OS calls, here to get time zone info
#import time
import pprint

# for dealing with XML
from eulxml import xmlmap
from eulxml.xmlmap import load_xmlobject_from_file, mods
import lxml.etree as etree

from eulxml.xmlmap import  mods as modsFile
from xml.dom import minidom

#from collections import defaultdict

import datetime
import isodate                  # for parsing ISO 8601 dates and times
import pytz                     # for time zones
from dateutil.tz import tzlocal

def utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=datetime.timezone.utc).astimezone(tz=None)

def local_to_utc(LocalTime):
    EpochSecond = time.mktime(LocalTime.timetuple())
    utcTime = datetime.datetime.utcfromtimestamp(EpochSecond)
    return utcTime

def datetime_to_local_string(canvas_time):
    global Use_local_time_for_output_flag
    t1=isodate.parse_datetime(canvas_time)
    if Use_local_time_for_output_flag:
        t2=t1.astimezone()
        return t2.strftime("%Y-%m-%d %H:%M")
    else:
        return t1.strftime("%Y-%m-%d %H:%M")

schools_info={'ABE': {'swe': 'Skolan för Arkitektur och samhällsbyggnad',
                      'eng': 'School of Architecture and the Built Environment'},
              'ITM': {'swe': 'Skolan för Industriell teknik och management',
                      'eng': 'School of Industrial Engineering and Management'},
              'SCI': {'swe': 'Skolan för Teknikvetenskap',
                      'eng': 'School of Engineering Sciences'},
              'CBH': {'swe': 'Skolan för Kemi, bioteknologi och hälsa',
                      'eng': 'School of Engineering Sciences in Chemistry, Biotechnology and Health'},
              'EECS': {'swe': 'Skolan för Elektroteknik och datavetenskap',
                      'eng': 'School of Electrical Engineering and Computer Science'}
              }

programcodes={
    'ARKIT': {'cycle': 2,
	      'swe': 'Arkitektutbildning',
              'eng': 'Degree Programme in Architecture'},
    
    'CBIOT': {'cycle': 2,
	      'swe': 'Civilingenjörsutbildning i bioteknik',
              'eng': 'Degree Programme in Biotechnology'},
    
    'CDATE': {'cycle': 2,
	      'swe': 'Civilingenjörsutbildning i datateknik',
              'eng': 'Degree Programme in Computer Science and Engineering'},
    
    'CDEPR': {'cycle': 2,
	      'swe': 'Civilingenjörsutbildning i design och produktframtagning',
              'eng': 'Degree Programme in Design and Product Realisation'},
    
    'CELTE': {'cycle': 2,
	      'swe': 'Civilingenjörsutbildning i elektroteknik',
              'eng': 'Degree Programme in Electrical Engineering'},
    
    'CENMI': {'cycle': 2,
	      'swe': 'Civilingenjörsutbildning i energi och miljö',
              'eng': 'Degree Programme in Energy and Environment'},
    
    'CFATE': {'cycle': 2,
	      'swe': 'Civilingenjörsutbildning i farkostteknik',
              'eng': 'Degree Programme in Vehicle Engineering'},
    
    'CINEK': {'cycle': 2,
	      'swe': 'Civilingenjörsutbildning i industriell ekonomi',
              'eng': 'Degree Programme in Industrial Engineering and Management'},
    
    'CINTE': {'cycle': 2,
	      'swe': 'Civilingenjörsutbildning i informationsteknik',
              'eng': 'Degree Programme in Information and Communication Technology'},
    
    'CITEH': {'cycle': 2,
	      'swe': 'Civilingenjörsutbildning i industriell teknik och hållbarhet',
              'eng': 'Degree Programme in Industrial Technology and Sustainability'},
    
    'CLGYM': {'cycle': 2,
	      'swe': 'Civilingenjör och lärare',
              'eng': 'Master of Science in Engineering and in Education'},
    'CMAST': {'cycle': 2,
	      'swe': 'Civilingenjörsutbildning i maskinteknik',
              'eng': 'Degree Programme in Mechanical Engineering'},
    'CMATD': {'cycle': 2,
	      'swe': 'Civilingenjörsutbildning i materialdesign',
              'eng': 'Degree Programme in Materials Design and Engineering'},
    'CMEDT': {'cycle': 2,
	      'swe': 'Civilingenjörsutbildning i medicinsk teknik',
              'eng': 'Degree Programme in Medical Engineering'},
    'CMETE': {'cycle': 2,
	      'swe': 'Civilingenjörsutbildning i medieteknik',
              'eng': 'Degree Programme in Media Technology'},
    'COPEN': {'cycle': 2,
	      'swe': 'Civilingenjörsutbildning öppen ingång',
              'eng': 'Degree Programme Open Entrance'},
    'CSAMH': {'cycle': 2,
	      'swe': 'Civilingenjörsutbildning i samhällsbyggnad',
              'eng': 'Degree Programme in Civil Engineering and Urban Management'},
    'CTFYS': {'cycle': 2,
	      'swe': 'Civilingenjörsutbildning i teknisk fysik',
              'eng': 'Degree Programme in Engineering Physics'},
    'CTKEM': {'cycle': 2,
	      'swe': 'Civilingenjörsutbildning i teknisk kemi',
              'eng': 'Degree Programme in Engineering Chemistry'},
    'CTMAT': {'cycle': 2,
	      'swe': 'Civilingenjörsutbildning i teknisk matematik',
              'eng': 'Degree Programme in Engineering Mathematics'},
    'KPUFU': {'cycle': 2,
	      'swe': 'Kompletterande pedagogisk utbildning för ämneslärarexamen i matematik, naturvetenskap och teknik för forskarutbildade',
              'eng': 'Bridging Teacher Education Programme in Mathematics, Science and Technology for Graduates with a Third Cycle Degree'},
    'KPULU': {'cycle': 2,
	      'swe': 'Kompletterande pedagogisk utbildning',
              'eng': 'Bridging Teacher Education Programme'},
    'KUAUT': {'cycle': 2,
	      'swe': 'Kompletterande utbildning för arkitekter med avslutad utländsk utbildning',
              'eng': 'Bridging programme for architects with foreign qualifications'},
    'KUIUT': {'cycle': 2,
	      'swe': 'Kompletterande utbildning för ingenjörer med avslutad utländsk utbildning',
              'eng': 'Bridging programme for engineers with foreign qualifications'},
    'LÄRGR': {'cycle': 2,
	      'swe': 'Ämneslärarutbildning med inriktning mot teknik, årskurs 7-9',
              'eng': 'Subject Teacher Education in Technology, Secondary Education'},
    'TAEEM': {'cycle': 2,
	      'swe': 'Masterprogram, flyg- och rymdteknik',
              'eng': "Master's Programme, Aerospace Engineering, 120 credits"},
    'TAETM': {'cycle': 2,
	      'swe': 'Masterprogram, aeroelasticitet i turbomaskiner',
              'eng': "Master's Programme, Turbomachinery Aeromechanic University Training, 120 credits"},
    'TARKM': {'cycle': 2,
	      'swe': 'Masterprogram, arkitektur',
              'eng': "Master's Programme, Architecture, 120 credits"},
    'TBASA': {'cycle': 0,
	      'swe': 'Tekniskt basår, KTH Flemingsberg',
              'eng': 'Technical Preparatory Year'},
    'TBASD': {'cycle': 0,
	      'swe': 'Tekniskt basår, KTH Campus',
              'eng': 'Technical Preparatory Year'},
    'TBASE': {'cycle': 0,
	      'swe': 'Tekniskt basår, KTH Södertälje',
              'eng': 'Technical Preparatory Year'},
    'TBTMD': {'cycle': 0,
	      'swe': 'Tekniskt basår, termin 2, KTH Campus',
              'eng': 'Technical Preparatory Semester'},
    'TBTMH': {'cycle': 0,
	      'swe': 'Tekniskt basår, termin 2, KTH Flemingsberg',
              'eng': 'Technical Preparatory Semester'},
    'TBTMS': {'cycle': 0,
	      'swe': 'Tekniskt basår, termin 2, KTH Södertälje',
              'eng': 'Technical Preparatory Semester'},
    'TBYPH': {'cycle': 1,
	      'swe': 'Högskoleutbildning i byggproduktion',
              'eng': 'Degree Progr. in Construction Management'},
    'TCAEM': {'cycle': 2,
	      'swe': 'Masterprogram, husbyggnads- och anläggningsteknik',
              'eng': "Master's Programme, Civil and Architectural Engineering, 120 credits"},
    'TCOMK': {'cycle': 1,
	      'swe': 'Kandidatprogram, informations- och kommunikationsteknik',
              'eng': "Bachelor's Programme in Information and Communication Technology"},
    'TCOMM': {'cycle': 2,
	      'swe': 'Masterprogram, kommunikationssystem',
              'eng': "Master's Programme, Communication Systems, 120 credits"},
    'TCSCM': {'cycle': 2,
	      'swe': 'Masterprogram, datalogi',
              'eng': "Master's Programme, Computer Science, 120 credits"},
    'TDEBM': {'cycle': 2,
	      'swe': 'Magisterprogram, design och byggande i staden',
              'eng': "Master's Programme, Urban Development and Design, 60 credits"},
    'TDSEM': {'cycle': 2,
	      'swe': 'Masterprogram, decentraliserade smarta energisystem',
              'eng': "Master's Programme, Decentralized Smart Energy Systems, 120 credits"},
    'TDTNM': {'cycle': 2,
	      'swe': 'Masterprogram, datorsimuleringar inom teknik och naturvetenskap',
              'eng': "Master's Programme, Computer Simulations for Science and Engineering, 120 credits"},
    'TEBSM': {'cycle': 2,
	      'swe': 'Masterprogram, inbyggda system',
              'eng': "Master's Programme, Embedded Systems, 120 credits"},
    'TEEEM': {'cycle': 2,
	      'swe': 'Masterprogram, teknik och ledning för energi- och miljösystem',
              'eng': "Master's Programme, Management and Engineering of Environment and Energy, 120 credits"},
    'TEEGM': {'cycle': 2,
	      'swe': 'Masterprogram, miljöteknik',
              'eng': "Master's Programme, Environmental Engineering, 120 credits"},
    'TEFRM': {'cycle': 2,
	      'swe': 'Masterprogram, elektromagnetism, fusion och rymdteknik',
              'eng': "Master's Programme, Electromagnetics, Fusion and Space Engineering, 120 credits"},
    'TEILM': {'cycle': 2,
	      'swe': 'Magisterprogram, entreprenörskap och innovationsledning',
              'eng': "Master's Programme, Entrepreneurship and Innovation Management, 60 credits"},
    'TEINM': {'cycle': 2,
	      'swe': 'Masterprogram, innovations- och tillväxtekonomi',
              'eng': "Master's Programme, Economics of Innovation and Growth, 120 credits"},
    'TELPM': {'cycle': 2,
	      'swe': 'Masterprogram, elkraftteknik',
              'eng': "Master's Programme, Electric Power Engineering, 120 credits"},
    'TFAFK': {'cycle': 1,
	      'swe': 'Kandidatprogram, Fastighetsutveckling med fastighetsförmedling',
              'eng': "Bachelor's Programme in Property Development and Agency"},
    'TFAHM': {'cycle': 2,
	      'swe': 'Magisterprogram, fastigheter',
              'eng': "Master's Programme, Real Estate"},
    'TFOBM': {'cycle': 2,
	      'swe': 'Masterprogram, fastigheter och byggande',
              'eng': "Master's Programme, Real Estate and Construction Management, 120 credits"},
    'TFOFK': {'cycle': 1,
	      'swe': 'Kandidatprogram, fastighet och finans',
              'eng': "Bachelor's Programme in Real Estate and Finance"},
    'TFORM': {'cycle': 2,
	      'swe': 'Masterprogram, fordonsteknik',
              'eng': "Master's Programme, Vehicle Engineering, 120 credits"},
    'THSSM': {'cycle': 2,
	      'swe': 'Masterprogram, hållbar samhällsplanering och stadsutformning',
              'eng': "Master's Programme, Sustainable Urban Planning and Design, 120 credits"},
    'TIBYH': {'cycle': 1,
	      'swe': 'Högskoleingenjörsutbildning i byggteknik och design',
              'eng': "Degree Programme in Constructional Engineering and Design"},
    'TIDAA': {'cycle': 1,
	      'swe': 'Högskoleingenjörsutbildning i datateknik, Flemingsberg',
              'eng': "Degree Programme in Computer Engineering"},
    'TIDAB': {'cycle': 1,
	      'swe': 'Högskoleingenjörsutbildning i datateknik, Kista',
              'eng': "Degree Programme in Computer Engineering"},
    'TIDTM': {'cycle': 2,
	      'swe': 'Masterprogram, idrottsteknologi',
              'eng': "Master's Programme, Sports Technology"},
    'TIEDB': {'cycle': 2,
	      'swe': 'Högskoleingenjörsutbildning i elektronik och datorteknik',
              'eng': "Degree Programme in Electronics and Computer Engineering"},
    'TIEEM': {'cycle': 2,
	      'swe': 'Masterprogram, innovativ uthållig energiteknik',
              'eng': "Master's Programme, Innovative Sustainable Energy Engineering, 120 credits"},
    'TIELA': {'cycle': 1,
	      'swe': 'Högskoleingenjörsutbildning i elektroteknik, Flemingsberg',
              'eng': "Degree Programme in Electrical Engineering"},
    'TIEMM': {'cycle': 2,
	      'swe': 'Masterprogram, industriell ekonomi',
              'eng': "Master's Programme, Industrial Engineering and Management, 120 credits"},
    'TIETM': {'cycle': 2,
	      'swe': 'Masterprogram, innovativ energiteknik',
              'eng': "Master's Programme, Energy Innovation, 120 credits"},
    'TIHLM': {'cycle': 2,
	      'swe': 'Masterprogram, innovativ teknik för en hälsosam livsmiljö',
              'eng': "Master's Programme, Innovative Technology for Healthy Living"},
    'TIIPS': {'cycle': 1,
	      'swe': 'Högskoleingenjörsutbildning i industriell teknik och produktionsunderhåll',
              'eng': "Degree Programme in Industrial Technology and Production Maintenance"},
    'TIKED': {'cycle': 1,
	      'swe': 'Högskoleingenjörsutbildning i kemiteknik',
              'eng': "Degree Programme in Chemical Engineering"},
    'TIMAS': {'cycle': 1,
	      'swe': 'Högskoleingenjörsutbildning i maskinteknik, Södertälje',
              'eng': "Degree Programme in Mechanical Engineering"},
    'TIMBM': {'cycle': 2,
	      'swe': 'Masterprogram, Industriell och miljöinriktad bioteknologi',
              'eng': "Master's Programme, Industrial and Environmental Biotechnology, 120 credits"},
    'TIMEL': {'cycle': 1,
	      'swe': 'Högskoleingenjörsutbildning i medicinsk teknik',
              'eng': "Degree Programme in Medical Technology"},
    'TIMTM': {'cycle': 2,
	      'swe': 'Masterprogram, interaktiv medieteknik',
              'eng': "Master's Programme, Interactive Media Technology, 120 credits"},
    'TINEM': {'cycle': 2,
	      'swe': 'Masterprogram, industriell ekonomi',
              'eng': "Master's Programme, Industrial Management, 120 credits"},
    'TINNM': {'cycle': 2,
	      'swe': 'Masterprogram, information och nätverksteknologi',
              'eng': "Master's Programme, Information and Network Engineering, 120 credits"},
    'TIPDM': {'cycle': 2,
	      'swe': 'Masterprogram, integrerad produktdesign',
              'eng': "Master's Programme, Integrated Product Design, 120 credits"},
    'TIPUM': {'cycle': 2,
	      'swe': 'Masterprogram, industriell produktutveckling',
              'eng': "Master's Programme, Engineering Design, 120 credits"},
    'TITEH': {'cycle': 1,
	      'swe': 'Högskoleingenjörsutbildning i teknik och ekonomi',
              'eng': "Degree Programme in Engineering and Economics"},
    'TITHM': {'cycle': 2,
	      'swe': 'Masterprogram, hållbar produktionsutveckling',
              'eng': "Master's Programme, Sustainable Production Development, 120 credits"},
    'TIVNM': {'cycle': 2,
	      'swe': 'Masterprogram, ICT Innovation',
              'eng': "Master's Programme, ICT Innovation, 120 credits"},
    'TJVTM': {'cycle': 2,
	      'swe': 'Masterprogram, järnvägsteknik',
              'eng': "Master's Programme, Railway Engineering, 120 credits"},
    'TKEMM': {'cycle': 2,
	      'swe': 'Masterprogram, kemiteknik för energi och miljö',
              'eng': "Master's Programme, Chemical Engineering for Energy and Environment, 120 credits"},
    'TLODM': {'cycle': 2,
	      'swe': 'Magisterprogram, ljusdesign',
              'eng': "Master's Programme,  Architectural Lighting Design, 60 credits"},
    'TMAIM': {'cycle': 2,
	      'swe': 'Masterprogram, maskininlärning',
              'eng': "Master's Programme, Machine Learning, 120 credits"},
    'TMAKM': {'cycle': 2,
	      'swe': 'Masterprogram, matematik',
              'eng': "Master's Programme, Mathematics, 120 credits"},
    'TMBIM': {'cycle': 2,
	      'swe': 'Masterprogram, medicinsk bioteknologi',
              'eng': "Master's Programme, Medical Biotechnology, 120 credits"},
    'TMEGM': {'cycle': 2,
	      'swe': 'Masterprogram, marinteknik',
              'eng': "Master's Programme, Maritime Engineering, 120 credits"},
    'TMESM': {'cycle': 2,
	      'swe': 'Masterprogram, miljövänliga energisystem',
              'eng': "Master's Programme, Environomical Pathways for Sustainable Energy Systems, 120 credits"},
    'TMHIM': {'cycle': 2,
	      'swe': 'Masterprogram, miljöteknik och hållbar infrastruktur',
              'eng': "Master's Programme, Environmental Engineering and Sustainable Infrastructure, 120 credits"},
    'TMLEM': {'cycle': 2,
	      'swe': 'Masterprogram, medicinsk teknik',
              'eng': "Master's Programme, Medical Engineering, 120 credits"},
    'TMMMM': {'cycle': 2,
	      'swe': 'Masterprogram, makromolekylära material',
              'eng': "Master's Programme, Macromolecular Materials, 120 credits"},
    'TMMTM': {'cycle': 2,
	      'swe': 'Masterprogram, media management',
              'eng': "Master's Programme, Media Management, 120 credits"},
    'TMRSM': {'cycle': 2,
	      'swe': 'Masterprogram, marina system',
              'eng': "Master's Programme, Naval Architecture, 120 credits"},
    'TMTLM': {'cycle': 2,
	      'swe': 'Masterprogram, molekylära tekniker inom livsvetenskaperna',
              'eng': "Master's Programme, Molecular Techniques in Life Science, 120 credits"},
    'TMVTM': {'cycle': 2,
	      'swe': 'Masterprogram, molekylär vetenskap och teknik',
              'eng': "Master's Programme, Molecular Science and Engineering, 120 credits"},
    'TNEEM': {'cycle': 2,
	      'swe': 'Masterprogram, kärnenergiteknik',
              'eng': "Master's Programme, Nuclear Energy Engineering, 120 credits"},
    'TNTEM': {'cycle': 2,
	      'swe': 'Masterprogram, nanoteknik',
              'eng': "Master's Programme, Nanotechnology, 120 credits"},
    'TPRMM': {'cycle': 2,
	      'swe': 'Masterprogram, industriell produktion',
              'eng': "Master's Programme, Production Engineering and Management, 120 credits"},
    'TSCRM': {'cycle': 2,
	      'swe': 'Masterprogram, systemteknik och robotik',
              'eng': "Master's Programme, Systems, Control and Robotics, 120 credits"},
    'TSEDM': {'cycle': 2,
	      'swe': 'Masterprogram, programvaruteknik för distribuerade system',
              'eng': "Master's Programme, Software Engineering of Distributed Systems, 120 credits"},
    'TSUEM': {'cycle': 2,
	      'swe': 'Masterprogram, hållbar energiteknik',
              'eng': "Master's Programme, Sustainable Energy Engineering, 120 credits"},
    'TSUTM': {'cycle': 2,
	      'swe': 'Masterprogram, teknik och hållbar utveckling',
              'eng': "Master's Programme, Sustainable Technology, 120 credits"},
    'TTAHM': {'cycle': 2,
	      'swe': 'Masterprogram, teknik, arbete och hälsa',
              'eng': "Master's Programme, Technology, Work and Health, 120 credits"},
    'TTEMM': {'cycle': 2,
	      'swe': 'Masterprogram, teknisk mekanik',
              'eng': "Master's Programme, Engineering Mechanics, 120 credits"},
    'TTFYM': {'cycle': 2,
	      'swe': 'Masterprogram, teknisk fysik',
              'eng': "Master's Programme, Engineering Physics, 120 credits"},
    'TTGTM': {'cycle': 2,
	      'swe': 'Masterprogram, transport och geoinformatik',
              'eng': "Master's Programme, Transport and Geoinformation Technology, 120 credits"},
    'TTMAM': {'cycle': 2,
	      'swe': 'Masterprogram, tillämpad matematik och beräkningsmatematik',
              'eng': "Master's Programme, Applied and Computational Mathematics, 120 credits"},
    'TTMIM': {'cycle': 2,
	      'swe': 'Masterprogram, transport, mobilitet och innovation',
              'eng': "Master's Programme, Transport, Mobility and Innovation"},
    'TTMVM': {'cycle': 2,
	      'swe': 'Masterprogram, teknisk materialvetenskap',
              'eng': "Master's Programme, Engineering Materials Science, 120 credits"},
    'TURSM': {'cycle': 2,
	      'swe': 'Magisterprogram, urbana studier',
              'eng': "Master's Programme, Urbanism Studies, 60 credits"}
}

def cycle_of_program(s):
    # replace ’ #x2019 with ' #x27
    s=s.replace(u"\u2019", "'")
    for p in programcodes:
        pname_eng=programcodes[p]['eng']
        pname_swe=programcodes[p]['swe']
        e_offset=s.find(pname_eng)
        s_offset=s.find(pname_swe)
        if (e_offset >= 0) or (s_offset >= 0):
            return programcodes[p]['cycle']
    # secondary check
    if s.find("Magisterprogram") >= 0 or s.find("Masterprogram") >= 0 or s.find("Master's") >= 0 or s.find("Master of Science") >= 0 or s.find("Civilingenjör") >= 0:
        return 2
    if s.find("Kandidatprogram") >= 0 or s.find("Bachelor's") >= 0 or s.find("Högskoleingenjör") >= 0:
        return 1
    print("cycle_of_program: Error in program name - did not match anything")
    return None

def programcode_from_degree(s):
    # replace ’ #x2019 with ' #x27
    s=s.replace(u"\u2019", "'")
    for p in programcodes:
        pname_eng=programcodes[p]['eng']
        pname_swe=programcodes[p]['swe']
        e_offset=s.find(pname_eng)
        s_offset=s.find(pname_swe)
        if (e_offset >= 0) or (s_offset >= 0):
            return p
    return None
#----------------------------------------------------------------------

def mathincluded(html):
    # look for LaTeX math in the html
    if html.find('\\(') >= 0 and html.find('\\)') >= 0:
        return True
    if html.find('\\[') >= 0 and html.find('\\]') >= 0:
        return True
    if html.find('$$') >= 0:
        return True
    return False

def transform_urls(html):
    # look for \\url{xxxxx} in the html
    start_of_url=html.find('\\url{')
    # print("start_of_url={}".format(start_of_url))
    while start_of_url >= 0:
        end_of_url=html.find('}', start_of_url+6)
        # print("end_of_url={}".format(end_of_url))
        url=html[start_of_url+5:end_of_url]
        # print("url={}".format(url))
        # <a href="xxxx">xxx</a>
        html_anchor="<a href='{0}'>{0}</a>".format(url)
        # print("html_anchor={}".format(html_anchor))
        html=url=html[0:start_of_url]+html_anchor+html[end_of_url+1:]
        # print("html={}".format(html))
        start_of_url=html.find('\\url{')
        # print("start_of_url={}".format(start_of_url))
    return html


def transform_math_for_diva(html):
    # \( equation \)
    start_of_eqn=html.find('\\(')
    # print("start_of_eqn={}".format(start_of_eqn))
    while start_of_eqn >= 0:
        offset=start_of_eqn+3
        end_of_eqn=html.find('\\)', offset)
        # print("end_of_eqn={}".format(end_of_eqn))
        eqn=html[start_of_eqn+2:end_of_eqn]
        # print("eqn={}".format(eqn))
        # <span class=\"math-tex\">\\(x =  {-b \\pm \\sqrt{b^2-4ac} \\over 2a}\\)</span>
        eqn_string="<span class=\'math-tex\'>\\({0}\\)</span>".format(eqn)
        # print("eqn_string={}".format(eqn_string))
        html_part1=url=html[0:start_of_eqn]+eqn_string
        offset=len(html_part1)
        html=html_part1+html[end_of_eqn+2:]
        # print("html={}".format(html))
        start_of_eqn=html.find('\\(', offset)
        # print("start_of_eqn={}".format(start_of_eqn))
    # \[ equation \]
    start_of_eqn=html.find('\\[')
    print("start_of_eqn={}".format(start_of_eqn))
    while start_of_eqn >= 0:
        offset=start_of_eqn+3
        end_of_eqn=html.find('\\]', offset)
        # print("end_of_eqn={}".format(end_of_eqn))
        eqn=html[start_of_eqn+2:end_of_eqn]
        # print("eqn={}".format(eqn))
        # <span class=\"math-tex\">\\(x =  {-b \\pm \\sqrt{b^2-4ac} \\over 2a}\\)</span>
        eqn_string="<span class=\'math-tex\'>\\[{0}\\]</span>".format(eqn)
        # print("eqn_string={}".format(eqn_string))
        html_part1=url=html[0:start_of_eqn]+eqn_string
        offset=len(html_part1)
        html=html_part1+html[end_of_eqn+2:]
        # print("html={}".format(html))
        start_of_eqn=html.find('\\[', offset)
        # print("start_of_eqn={}".format(start_of_eqn))
    # $$ equation $$
    start_of_eqn=html.find('$$')
    # print("start_of_eqn={}".format(start_of_eqn))
    while start_of_eqn >= 0:
        offset=start_of_eqn+3
        end_of_eqn=html.find('$$', offset)
        # print("end_of_eqn={}".format(end_of_eqn))
        eqn=html[start_of_eqn+2:end_of_eqn]
        # print("eqn={}".format(eqn))
        # <span class=\"math-tex\">\\(x =  {-b \\pm \\sqrt{b^2-4ac} \\over 2a}\\)</span>
        eqn_string="<span class=\'math-tex\'>\\[{0}\\]</span>".format(eqn)
        # print("eqn_string={}".format(eqn_string))
        html_part1=url=html[0:start_of_eqn]+eqn_string
        offset=len(html_part1)
        html=html_part1+html[end_of_eqn+2:]
        # print("html={}".format(html))
        start_of_eqn=html.find('$$', offset)
        # print("start_of_eqn={}".format(start_of_eqn))
    #
    return html


national_subject_categories_dict={
    '102': {'eng': ['Natural Sciences', 'Computer and Information Sciences'],
              'swe':  ['Naturvetenskap', 'Data- och informationsvetenskap (Datateknik)']
            },
    '10201': {'eng': ['Natural Sciences', 'Computer and Information Sciences', 'Computer Sciences'],
              'swe':  ['Naturvetenskap', 'Data- och informationsvetenskap', 'Datavetenskap (datalogi)']
            },

    '10202': {'eng': ['Natural Sciences', 'Computer and Information Sciences', 'Information Systems'],
              'swe':  ['Naturvetenskap', 'Data- och informationsvetenskap', 'Systemvetenskap, informationssystem och informatik']
            },

    '10203': {'eng': ['Natural Sciences', 'Computer and Information Sciences', 'Bioinformatics (Computational Biology)'],
              'swe':  ['Naturvetenskap', 'Data- och informationsvetenskap', 'Bioinformatik (beräkningsbiologi)']
            },

    '10204': {'eng': ['Natural Sciences', 'Computer and Information Sciences', 'Human Computer Interaction'],
              'swe':  ['Naturvetenskap', 'Data- och informationsvetenskap', 'Människa-datorinteraktion (interaktionsdesign)']
            },

    '10205': {'eng': ['Natural Sciences', 'Computer and Information Sciences', 'Software Engineering'],
              'swe':  ['Naturvetenskap', 'Data- och informationsvetenskap', 'Programvaruteknik']
            },

    '10206':  {'eng': ['Natural Sciences', 'Computer and Information Sciences', 'Computer Engineering'],
              'swe':  ['Naturvetenskap', 'Data- och informationsvetenskap', 'Datorteknik']
            },
    '10207':  {'eng': ['Natural Sciences', 'Computer and Information Sciences', 'Computer Vision and Robotics (Autonomous Systems)'],
              'swe':  ['Naturvetenskap', 'Data- och informationsvetenskap', 'Datorseende och robotik (autonoma system)']
            },
    '10208':  {'eng': ['Natural Sciences', 'Computer and Information Sciences', 'Language Technology (Computational Linguistics)'],
              'swe':  ['Naturvetenskap', 'Data- och informationsvetenskap', 'Språkteknologi (språkvetenskaplig databehandling)']
            },
    '10209':  {'eng': ['Natural Sciences', 'Computer and Information Sciences', 'Media and Communication Technology'],
              'swe':  ['Naturvetenskap', 'Data- och informationsvetenskap', 'Medieteknik']
            },

    '10299':  {'eng': ['Natural Sciences', 'Computer and Information Sciences', 'Other Computer and Information Science'],
              'swe':  ['Naturvetenskap', 'Data- och informationsvetenskap', 'Annan data- och informationsvetenskap']
            },

    '202': {'eng': ['Engineering and Technology', 'Electrical Engineering, Electronic Engineering, Information Engineering'],
              'swe': ['Teknik och teknologier', 'Elektroteknik och elektronik']
              },
    '20201': {'eng': ['Engineering and Technology', 'Electrical Engineering, Electronic Engineering, Information Engineering', ''],
              'swe': ['Teknik och teknologier', 'Elektroteknik och elektronik', 'Robotteknik och automation Robotics']
              },
    '20202': {'eng': ['Engineering and Technology', 'Electrical Engineering, Electronic Engineering, Information Engineering', 'Control Engineering'],
              'swe': ['Teknik och teknologier', 'Elektroteknik och elektronik', 'Reglerteknik']
              },
    '20203': {'eng': ['Engineering and Technology', 'Electrical Engineering, Electronic Engineering, Information Engineering', 'Communication Systems'],
              'swe': ['Teknik och teknologier', 'Elektroteknik och elektronik', 'Kommunikationssystem']
              },
    '20204': {'eng': ['Engineering and Technology', 'Electrical Engineering, Electronic Engineering, Information Engineering', 'Telecommunications'],
              'swe': ['Teknik och teknologier', 'Elektroteknik och elektronik', 'Telekommunikation']
              },
    '20205': {'eng': ['Engineering and Technology', 'Electrical Engineering, Electronic Engineering, Information Engineering', 'Signal Processing'],
              'swe': ['Teknik och teknologier', 'Elektroteknik och elektronik', 'Signalbehandling']
              },
    '20206': {'eng': ['Engineering and Technology', 'Electrical Engineering, Electronic Engineering, Information Engineering', 'Computer Systems'],
              'swe': ['Teknik och teknologier', 'Elektroteknik och elektronik', 'Datorsystem']
              },
    '20207': {'eng': ['Engineering and Technology', 'Electrical Engineering, Electronic Engineering, Information Engineering', 'Embedded Systems'],
              'swe': ['Teknik och teknologier', 'Elektroteknik och elektronik', 'Inbäddad systemteknik']
              },
    '20299': {'eng': ['Engineering and Technology', 'Electrical Engineering, Electronic Engineering, Information Engineering', 'Other Electrical Engineering, Electronic Engineering, Information Engineering'],
              'swe': ['Teknik och teknologier', 'Elektroteknik och elektronik', 'Annan elektroteknik och elektronik']
              }
}


education_program_diva={
    '10522': {'eng': 'Bachelor of Science in Engineering',
              'swe': 'Högskoleingenjörsexamen'
              },
    '9800': {'eng': 'Bachelor of Science in Engineering -  Constructional Engineering and Design',
              'swe': 'Högskoleingenjörsexamen - Byggteknik och design'
              },
    '9801': {'eng': 'Bachelor of Science in Engineering -  Constructional Engineering and Economics',
              'swe': 'Högskoleingenjörsexamen - Byggteknik och ekonomi'
              },
    '9880': {'eng': 'Bachelor of Science in Engineering - Chemical Engineering',
              'swe': 'Högskoleingenjörsexamen - Kemiteknik'
              },
    '9989': {'eng': 'Bachelor of Science in Engineering - Computer Engineering and Economics',
              'swe': 'Högskoleingenjörsexamen - Datateknik och ekonomi'
              },

    '9921': {'eng': 'Bachelor of Science in Engineering - Computer Engineering',
              'swe': 'Högskoleingenjörsexamen - Datateknik'
              },

    '9990': {'eng': 'Bachelor of Science in Engineering - Computer Engineering',
              'swe': 'Högskoleingenjörsexamen - Datateknik'
              },
    '10751': {'eng': 'Bachelor of Science in Engineering - Constructional Engineering and Health',
              'swe': 'Högskoleingenjörsexamen - Byggteknik och hälsa'
              },
    '9949': {'eng': 'Bachelor of Science in Engineering - Electrical Engineering and Economics',
              'swe': 'Högskoleingenjörsexamen - Elektroteknik och ekonomi'
              },
    '9907': {'eng': 'Bachelor of Science in Engineering - Electrical Engineering',
              'swe': 'Högskoleingenjörsexamen - Elektroteknik'
              },
    '9948': {'eng': 'Bachelor of Science in Engineering - Electrical Engineering',
              'swe': 'Högskoleingenjörsexamen - Elektroteknik'
              },
    '9922': {'eng': 'Bachelor of Science in Engineering - Electronics and Computer Engineering',
              'swe': 'Högskoleingenjörsexamen - Elektronik och datorteknik'
              },
    '9992': {'eng': 'Bachelor of Science in Engineering - Engineering and Economics',
              'swe': 'Högskoleingenjörsexamen - Teknik och ekonomi'
              },
    '9951': {'eng': 'Bachelor of Science in Engineering - Mechanical Engineering and Economics',
              'swe': 'Högskoleingenjörsexamen - Maskinteknik och ekonomi'
              },
    '9950': {'eng': 'Bachelor of Science in Engineering - Mechanical Engineering',
              'swe': 'Högskoleingenjörsexamen - Maskinteknik'
              },
    '9991': {'eng': 'Bachelor of Science in Engineering - Medical Technology',
              'swe': 'Högskoleingenjörsexamen - Medicinsk teknik'
              },
    '10523': {'eng': 'Bachelor of Science',
              'swe': 'Teknologie kandidatexamen'
              },
    '10950': {'eng': 'Bachelor of Science - Architecture',
              'swe': 'Teknologie kandidatexamen - Arkitektur'
              },
    '9924': {'eng': 'Bachelor of Science - Business Engineering',
              'swe': 'Teknologie kandidatexamen - Affärssystem'
              },
    '17650': {'eng': 'Bachelor of Science - Energy and Environment',
              'swe': 'Teknologie kandidatexamen - Energi och miljö'
              },
    '9925': {'eng': 'Bachelor of Science - Information and Communication Technology',
              'swe': 'Teknologie kandidatexamen - Informations- och kommunikationsteknik'
              },
    '9994': {'eng': 'Bachelor of Science - Medical Informatics',
              'swe': 'Teknologie kandidatexamen - Medicinsk informatik'
              },
    '9805': {'eng': 'Bachelor of Science - Property Development and Agency',
              'swe': 'Teknologie kandidatexamen - Fastighetsutveckling med fastighetsförmedling'
              },
    '9804': {'eng': 'Bachelor of Science - Real Estate and Finance',
              'swe': 'Teknologie kandidatexamen - Fastighet och finans'
              },
    '9892': {'eng': 'Bachelor of Science - Simulation Technology and Virtual Design',
              'swe': 'Teknologie kandidatexamen - Simuleringsteknik och virtuell design'
              },
    '10524': {'eng': 'Degree of Master',
              'swe': 'Teknologie magisterexamen'
              },
    '9858': {'eng': 'Degree of Master - Design and Building',
              'swe': 'Teknologie magisterexamen - Design och byggande'
              },
    '9956': {'eng': 'Master of Science - Applied Logistics',
              'swe': 'Teknologie magisterexamen - Tillämpad logistik'
              },
    '9999': {'eng': 'Master of Science - Architectural Lighting Design',
              'swe': 'Teknologie magisterexamen - Ljusdesign'
              },
    '9997': {'eng': 'Master of Science - Computer Networks',
              'swe': 'Teknologie magisterexamen - Datornätverk'
              },
    '9953': {'eng': 'Master of Science - Entrepreneurship and Innovation Management',
              'swe': 'Teknologie magisterexamen - Entreprenörskap och innovationsledning'
              },
    '9998': {'eng': 'Master of Science - Ergonomics and Human-Technology-Organisation',
              'swe': 'Teknologie magisterexamen - Ergonomi och Människa-Teknik-Organisation'
              },
    '9954': {'eng': 'Master of Science - Product Realisation',
              'swe': 'Teknologie magisterexamen - Produktframtagning'
              },
    '9955': {'eng': 'Master of Science - Project Management and Operational Development',
              'swe': 'Teknologie magisterexamen - Projektledning och verksamhetsutveckling'
              },
    '9996': {'eng': 'Master of Science - Work and Health',
              'swe': 'Teknologie magisterexamen - Arbete och hälsa'
              },
    '14553': {'eng': 'Teknologie magisterexamen - Teknik, hälsa och arbetsmiljöutveckling',
              'swe': 'Teknologie magisterexamen - Teknik, hälsa och arbetsmiljöutveckling'
              },
    '10525': {'eng': 'Degree of Master',
              'swe': 'Teknologie masterexamen'
              },
    '9850': {'eng': 'Degree of Master -  Architectural Enginering',
              'swe': 'Teknologie masterexamen - Huskonstruktion'
              },
    '28050': {'eng': 'Degree of Master -  Urbanism Studies',
              'swe': 'Teknologie masterexamen - Urbana studier'
              },
    '9882': {'eng': 'Degree of Master - Chemical Engineering for Energy and Environment',
              'swe': 'Teknologie masterexamen - Kemiteknik för energi och miljö'
              },
    '24400': {'eng': 'Degree of Master - Civil and Architectural Engineering',
              'swe': 'Teknologie masterexamen - Husbyggnads- och anläggningsteknik'
              },
    '9864': {'eng': 'Degree of Master - Economics of Innovation and Growth',
              'swe': 'Teknologie masterexamen - Innovations- och tillväxtekonomi'
              },
    '9863': {'eng': 'Degree of Master - Environmental Engineering and Sustainable Infrastructure',
              'swe': 'Teknologie masterexamen - Miljöteknik och hållbar infrastruktur'
              },
    '9862': {'eng': 'Degree of Master - Geodesy and Geoinformatics',
              'swe': 'Teknologie masterexamen - Geodesi och geoinformatik'
              },
    '9865': {'eng': 'Degree of Master - Infrastructure Engineering',
              'swe': 'Teknologie masterexamen - Teknisk infrastruktur'
              },
    '9868': {'eng': 'Degree of Master - Land Management',
              'swe': 'Teknologie masterexamen - Fastighetsvetenskap'
              },
    '9883': {'eng': 'Degree of Master - Macromolecular Materials',
              'swe': 'Teknologie masterexamen - Makromolekylära material'
              },
    '9885': {'eng': 'Degree of Master - Materials and Sensors System for Environmental Technologies',
              'swe': 'Teknologie masterexamen - Material och sensorsystem för miljötekniska tillämpningar'
              },
    '9884': {'eng': 'Degree of Master - Molecular Science and Engineering',
              'swe': 'Teknologie masterexamen - Molekylär vetenskap och teknik'
              },
    '9861': {'eng': 'Degree of Master - Real Estate Development and Financial Services',
              'swe': 'Teknologie masterexamen - Fastighetsutveckling och finansiella tjänster'
              },
    '13400': {'eng': 'Degree of Master - Spatial Planning',
              'swe': 'Teknologie masterexamen - Samhällsplanering'
              },
    '9552': {'eng': 'Degree of Master - Sustainable Urban Planning and Design',
              'swe': 'Teknologie masterexamen - Hållbar samhällsplanering och stadsutformning'
              },
    '9866': {'eng': 'Degree of Master - Transport Systems',
              'swe': 'Teknologie masterexamen - Transportsystem'
              },
    '13401': {'eng': 'Degree of Master - Urban Planning and Design',
              'swe': 'Teknologie masterexamen - Urban planering och design'
              },
    '9867': {'eng': 'Degree of Master - Water System Technology',
              'swe': 'Teknologie masterexamen - Vattensystemteknik'
              },
    '9977': {'eng': 'Master of Science - Aerospace Engineering',
              'swe': 'Teknologie masterexamen - Flyg- och rymdteknik'
              },
    '23002': {'eng': 'Master of Science - Applied and Computational Mathematics',
              'swe': 'Teknologie masterexamen - Tillämpad matematik och beräkningsmatematik'
              },
    '10001': {'eng': 'Master of Science - Architectural Lighting Design and Health',
              'swe': 'Teknologie masterexamen - Ljus, design och hälsa'
              },
    '9860': {'eng': 'Master of Science - Architecture',
              'swe': 'Teknologie masterexamen - Arkitektur'
              },
    '9894': {'eng': 'Master of Science - Computational and Systems Biology',
              'swe': 'Teknologie masterexamen - Beräknings- och systembiologi'
              },
    '9875': {'eng': 'Master of Science - Computational Chemistry and Computational Physics',
              'swe': 'Teknologie masterexamen - Beräkningskemi och beräkningsfysik'
              },
    '9895': {'eng': 'Master of Science - Computer Science',
              'swe': 'Teknologie masterexamen - Datalogi'
              },
    '9901': {'eng': 'Master of Science - Computer Simulation for Science and Engineering',
              'swe': 'Teknologie masterexamen - Datorsimuleringar inom teknik och naturvetenskap'
              },
    '9930': {'eng': 'Master of Science - Design and Implementation of ICT Products and Systems',
              'swe': 'Teknologie masterexamen - Konstruktion och realisering av IT-produkter och -system'
              },
    '9938': {'eng': 'Master of Science - Distributed Computing',
              'swe': 'Teknologie masterexamen - Distribuerade system'
              },
    '9910': {'eng': 'Master of Science - Electric Power Engineering',
              'swe': 'Teknologie masterexamen - Elkraftteknik'
              },
    '9909': {'eng': 'Master of Science - Electrophysics',
              'swe': 'Teknologie masterexamen - Elektrofysik'
              },
    '9928': {'eng': 'Master of Science - Embedded Systems',
              'swe': 'Teknologie masterexamen - Inbyggda system'
              },
    '9983': {'eng': 'Master of Science - Engineeering Physics',
              'swe': 'Teknologie masterexamen - Teknisk fysik'
              },
    '9935': {'eng': 'Master of Science - Engineering and Management of Information Systems',
              'swe': 'Teknologie masterexamen - Teknik och ledning för informationssystem'
              },
    '9962': {'eng': 'Master of Science - Engineering Design',
              'swe': 'Teknologie masterexamen - Industriell produktutveckling'
              },
    '9965': {'eng': 'Master of Science - Engineering Materials Science',
              'swe': 'Teknologie masterexamen - Teknisk materialvetenskap'
              },
    '9982': {'eng': 'Master of Science - Engineering Mechanics',
              'swe': 'Teknologie masterexamen - Teknisk mekanik'
              },
    '9969': {'eng': 'Master of Science - Environomical Pathways for Sustainable Energy Systems',
              'swe': 'Teknologie masterexamen - Miljövänliga energisystem'
              },
    '9899': {'eng': 'Master of Science - Human-Computer Interaction',
              'swe': 'Teknologie masterexamen - Människa-datorinteraktion'
              },
    '9873': {'eng': 'Master of Science - Industrial and Environmental Biotechnology',
              'swe': 'Teknologie masterexamen - Industriell och miljöinriktad bioteknologi'
              },
    '9959': {'eng': 'Master of Science - Industrial Engineering and Management',
              'swe': 'Teknologie masterexamen - Industriell ekonomi'
              },
    '9929': {'eng': 'Master of Science - Information and Communication Systems Security',
              'swe': 'Teknologie masterexamen - Informations- och kommunikationssäkerhet'
              },
    '9966': {'eng': 'Master of Science - Innovative Sustainable Energy Engineering',
              'swe': 'Teknologie masterexamen - Innovativ uthållig energiteknik'
              },
    '9963': {'eng': 'Master of Science - Integrated Product Design',
              'swe': 'Teknologie masterexamen - Integrerad produktdesign'
              },
    '9934': {'eng': 'Master of Science - Interactive Systems Engineering',
              'swe': 'Teknologie masterexamen - Teknik för interaktiva system'
              },
    '13450': {'eng': 'Master of Science - Internetworking',
              'swe': 'Teknologie masterexamen - Internetteknik'
              },
    '9896': {'eng': 'Master of Science - Machine Learning',
              'swe': 'Teknologie masterexamen - Maskininlärning'
              },
    '9968': {'eng': 'Master of Science - Management and Engineering of Environment and Energy',
              'swe': 'Teknologie masterexamen - Teknik och ledning för energi- och miljösystem'
              },
    '9984': {'eng': 'Master of Science - Maritime Engineering',
              'swe': 'Teknologie masterexamen - Marinteknik'
              },
    '11254': {'eng': 'Master of Science - Materials Science and Engineering',
              'swe': 'Teknologie masterexamen - Materialteknik'
              },
    '9981': {'eng': 'Master of Science - Mathematics',
              'swe': 'Teknologie masterexamen - Matematik'
              },
    '9897': {'eng': 'Master of Science - Media Management',
              'swe': 'Teknologie masterexamen - Media management'
              },
    '9898': {'eng': 'Master of Science - Media Technology',
              'swe': 'Teknologie masterexamen - Medieteknik'
              },
    '9874': {'eng': 'Master of Science - Medical Biotechnology',
              'swe': 'Teknologie masterexamen - Medicinsk bioteknologi'
              },
    '10003': {'eng': 'Master of Science - Medical Engineering',
              'swe': 'Teknologie masterexamen - Medicinsk teknik'
              },
    '9931': {'eng': 'Master of Science - Nanotechnology',
              'swe': 'Teknologie masterexamen - Nanoteknik'
              },
    '9980': {'eng': 'Master of Science - Naval Architecture',
              'swe': 'Teknologie masterexamen - Marina system'
              },
    '9911': {'eng': 'Master of Science - Network Services and Systems',
              'swe': 'Teknologie masterexamen - Nätverkstjänster och system'
              },
    '9979': {'eng': 'Master of Science - Nuclear Energy Engineering',
              'swe': 'Teknologie masterexamen - Kärnenergiteknik'
              },
    '9914': {'eng': 'Master of Science - Nuclear Fusion Science and Engineering Physics',
              'swe': 'Teknologie masterexamen - Fusionsenergi och teknisk fysik'
              },
    '9927': {'eng': 'Master of Science - Photonics',
              'swe': 'Teknologie masterexamen - Fotonik'
              },
    '9961': {'eng': 'Master of Science - Production Engineering and Management',
              'swe': 'Teknologie masterexamen - Industriell produktion'
              },
    '9859': {'eng': 'Master of Science - Real Estate Management',
              'swe': 'Teknologie masterexamen - Fastighetsföretagande'
              },
    '9915': {'eng': 'Master of Science - School of Electrical Engineering (EES) - Master of Science - Research on Information and Communication Technologies',
              'swe': 'Teknologie masterexamen - Informations- och kommunikationsteknik, forskningsförberedande'
              },
    '9900': {'eng': 'Master of Science - Scientific Computing',
              'swe': 'Teknologie masterexamen - Tekniska beräkningar'
              },
    '9932': {'eng': 'Master of Science - Software Engineering of Distributed Systems',
              'swe': 'Teknologie masterexamen - Programvaruteknik för distribuerade system'
              },
    '9958': {'eng': 'Master of Science - Sustainable Energy Engineering',
              'swe': 'Teknologie masterexamen - Hållbar energiteknik'
              },
    '9964': {'eng': 'Master of Science - Sustainable Technology',
              'swe': 'Teknologie masterexamen - Teknik och hållbar utveckling'
              },
    '9933': {'eng': 'Master of Science - System-on-Chip Design',
              'swe': 'Teknologie masterexamen - Systemkonstruktion på kisel'
              },
    '9902': {'eng': 'Master of Science - Systems Biology',
              'swe': 'Teknologie masterexamen - Systembiologi'
              },
    '9912': {'eng': 'Master of Science - Systems, Control and Robotics',
              'swe': 'Teknologie masterexamen - Systemteknik och robotik'
              },
    '21652': {'eng': 'Master of Science - Transport and Geoinformation Technology',
              'swe': 'Teknologie masterexamen - Transport och geoinformatik'
              },
    '9970': {'eng': 'Master of Science - Turbomachinery Aeromechanic University Training',
              'swe': 'Teknologie masterexamen - Aeroelasticitet i turbomaskiner'
              },
    '9978': {'eng': 'Master of Science - Vehicle Engineering',
              'swe': 'Teknologie masterexamen - Fordonsteknik'
              },
    '9913': {'eng': 'Master of Science - Wireless Systems',
              'swe': 'Teknologie masterexamen - Trådlösa system'
              },
    '9939': {'eng': 'Master of Science -Communication Systems',
              'swe': 'Teknologie masterexamen - Kommunikationssystem'
              },
    '10002': {'eng': 'Master of Science -Medical Imaging',
              'swe': 'Teknologie masterexamen - Medicinsk bildbehandling'
              },
    '9937': {'eng': 'Master of Science -Security and Mobile Computing',
              'swe': 'Teknologie masterexamen - Säker och mobil kommunikation'
              },
    '10521': {'eng': 'Higher Education Diploma',
              'swe': 'Högskoleexamen'
              },
    '9802': {'eng': 'Higher Education Diploma - Construction Management',
              'swe': 'Högskoleexamen - Byggproduktion'
              },
    '9803': {'eng': 'Higher Education Diploma - Constructional Technology and Real Estate Agency',
              'swe': 'Högskoleexamen - Byggteknik och fastighetsförmedling'
              },
    '10520': {'eng': 'Master of Architecture',
              'swe': 'Arkitektexamen'
              },
    '9558': {'eng': 'Master of Architecture - Architecture',
              'swe': 'Arkitektexamen - Arkitektur'
              },
    '10500': {'eng': 'Master of Science in Engineering',
              'swe': 'Civilingenjörsexamen'
              },
    '9905': {'eng': 'Master of Science in Engineering -  Electrical Engineering',
              'swe': 'Civilingenjörsexamen - Elektroteknik'
              },
    '9871': {'eng': 'Master of Science in Engineering - Biotechnology',
              'swe': 'Civilingenjörsexamen - Bioteknik'
              },
    '9878': {'eng': 'Master of Science in Engineering - Chemical Science and Engineering',
              'swe': 'Civilingenjörsexamen - Kemivetenskap'
              },
    '9889': {'eng': 'Master of Science in Engineering - Computer Science and Technology',
              'swe': 'Civilingenjörsexamen - Datateknik'
              },
    '9942': {'eng': 'Master of Science in Engineering - Design and Product Realisation',
              'swe': 'Civilingenjörsexamen - Design och produktframtagning'
              },
    '9943': {'eng': 'Master of Science in Engineering - Energy and Environment',
              'swe': 'Civilingenjörsexamen - Energi och miljö'
              },
    '9973': {'eng': 'Master of Science in Engineering - Engineering and of Education',
              'swe': 'Civilingenjörsexamen - Civilingenjör och lärare'
              },
    '9944': {'eng': 'Master of Science in Engineering - Industrial Engineering and Management',
              'swe': 'Civilingenjörsexamen - Industriell ekonomi'
              },
    '9918': {'eng': 'Master of Science in Engineering - Information and Communication Technology',
              'swe': 'Civilingenjörsexamen - Informationsteknik'
              },
    '9946': {'eng': 'Master of Science in Engineering - Materials Design and Engineering',
              'swe': 'Civilingenjörsexamen - Materialdesign'
              },
    '9945': {'eng': 'Master of Science in Engineering - Mechanical Engineering',
              'swe': 'Civilingenjörsexamen - Maskinteknik'
              },
    '9890': {'eng': 'Master of Science in Engineering - Media Technology',
              'swe': 'Civilingenjörsexamen - Medieteknik'
              },
    '9987': {'eng': 'Master of Science in Engineering - Medical Engineering',
              'swe': 'Civilingenjörsexamen - Medicinsk teknik'
              },
    '9919': {'eng': 'Master of Science in Engineering - Microelectronics',
              'swe': 'Civilingenjörsexamen - Mikroelektronik'
              },
    '10526': {'eng': 'Master of Science in Engineering - Urban Management',
              'swe': 'Civilingenjörsexamen - Samhällsbyggnad'
              },
    '9974': {'eng': 'Master of Science in Engineering - Vehicle Engineering',
              'swe': 'Civilingenjörsexamen - Farkostteknik'
              },
    '9975': {'eng': 'Master of Science in Engineering -Engineering Physics',
              'swe': 'Civilingenjörsexamen - Teknisk fysik'
              },
    '29550': {'eng': 'Other programmes',
              'swe': 'Övriga utbildningsprogram'
              },
    '29551': {'eng': 'Subject Teacher Education in Technology, Secondary Education',
              'swe': 'Ämneslärarutbildning med inriktning mot teknik, årskurs 7-9'
              },
    '9557': {'eng': 'Z - School of Architecture and the Built Environment (ABE)',
              'swe': 'Z - Skolan för arkitektur och samhällsbyggnad (ABE)'
              },
    '9852': {'eng': 'School of Architecture and the Built Environment (ABE)  - Master of Science in Engineering',
              'swe': 'Skolan för arkitektur och samhällsbyggnad (ABE) - Civilingengörsexamen'
              }
}

# Subject/course codes
subject_area_codes_diva={
    '10260': {'eng': 'Accelerator Technique',
              'swe': 'Acceleratorteknik'
              },
    '10306': {'eng': 'Aeronautical Engineering',
              'swe': 'Flygteknik'
              },
    '10261': {'eng': 'Analytical Chemistry',
              'swe': 'Analytisk kemi'
              },
    '10262': {'eng': 'Antenna Systems Technology',
              'swe': 'Antennsystemteknik'
              },
    '10423': {'eng': 'Applied Information Technology',
              'swe': 'Tillämpad informationsteknik'
              },
    '10424': {'eng': 'Applied Logistics',
              'swe': 'Tillämpad logistik'
              },
    '10426': {'eng': 'Applied Material Physics',
              'swe': 'Tillämpad materialfysik'
              },
    '10427': {'eng': 'Applied Materials Technology',
              'swe': 'Tillämpad materialteknologi'
              },
    '10425': {'eng': 'Applied Mathematical Analysis',
              'swe': 'Tillämpad matematisk analys'
              },
    '28053': {'eng': 'Applied Mathematics and Industrial Economics',
              'swe': 'Tillämpad matematik och industriell ekonomi'
              },
    '10422': {'eng': 'Applied Physics',
              'swe': 'Tillämpad fysik'
              },
    '10428': {'eng': 'Applied Process Metallurgy',
              'swe': 'Tillämpad processmetallurgi'
              },
    '10369': {'eng': 'Applied Thermodynamics',
              'swe': 'Mekanisk värmeteori'
              },
    '10429': {'eng': 'Applied Thermodynamics',
              'swe': 'Tillämpad termodynamik'
              },
    '10258': {'eng': 'Architectural Lighting Design and Health',
              'swe': 'Ljusdesign och hälsa'
              },
    '10349': {'eng': 'Architectural Lighting Design',
              'swe': 'Ljusdesign'
              },
    '10264': {'eng': 'Architecture',
              'swe': 'Arkitektur'
              },
    '10397': {'eng': 'Automatic Control',
              'swe': 'Reglerteknik'
              },
    '10269': {'eng': 'Biocomposites',
              'swe': 'Biokompositer'
              },
    '10410': {'eng': 'Biomechanics',
              'swe': 'Teknik i vården, biomekanik'
              },
    '10270': {'eng': 'Biomedical Engineering',
              'swe': 'Biomedicinsk teknik'
              },
    '10253': {'eng': 'Biotechnology',
              'swe': 'Bioteknologi'
              },
    '10271': {'eng': 'Biotechnology',
              'swe': 'Bioteknik'
              },
    '10273': {'eng': 'Building and Real Estate Economics',
              'swe': 'Bygg- och fastighetsekonomi'
              },
    '10484': {'eng': 'Building Design',
              'swe': 'Projektering'
              },
    '10275': {'eng': 'Building Materials',
              'swe': 'Byggnadsmateriallära'
              },
    '10471': {'eng': 'Building Services Engineering and Energy',
              'swe': 'Installationsteknik och energi'
              },
    '10277': {'eng': 'Building Technology',
              'swe': 'Byggnadsteknik'
              },
    '10449': {'eng': 'Building Technology',
              'swe': 'Byggteknik'
              },
    '10266': {'eng': 'Built Environment Analysis',
              'swe': 'Bebyggelseanalys'
              },
    '10485': {'eng': 'Built Environment',
              'swe': 'Samhällsbyggnad'
              },
    '10371': {'eng': 'Casting of Metals',
              'swe': 'Metallernas gjutning'
              },
    '10336': {'eng': 'Ceramic Materials',
              'swe': 'Keramiska material'
              },
    '10337': {'eng': 'Ceramics',
              'swe': 'Keramteknologi'
              },
    '10335': {'eng': 'Chemical Engineering',
              'swe': 'Kemiteknik'
              },
    '10472': {'eng': 'Chemical Science and Engineering',
              'swe': 'Kemivetenskap'
              },
    '10344': {'eng': 'Circuit Electronics',
              'swe': 'Kretselektronik'
              },
    '10481': {'eng': 'Civil Engineering Management',
              'swe': 'Produktionsteknik'
              },
    '10338': {'eng': 'Communication Networks',
              'swe': 'Kommunikationsnät'
              },
    '10340': {'eng': 'Communication Theory',
              'swe': 'Kommunikationsteori'
              },
    '10339': {'eng': 'Communications Systems',
              'swe': 'Kommunikationssystem'
              },
    '10420': {'eng': 'Computational Thermodynamics',
              'swe': 'Termodynamisk modellering'
              },
    '10279': {'eng': 'Computer and Systems Sciences',
              'swe': 'Data- och systemvetenskap'
              },
    '10281': {'eng': 'Computer Communication',
              'swe': 'Datorkommunikation'
              },
    '10452': {'eng': 'Computer Engineering with Business Economics',
              'swe': 'Datateknik med ekonomi'
              },
    '10453': {'eng': 'Computer Engineering with Industrial Economy',
              'swe': 'Datateknik med industriell ekonomi'
              },
    '10460': {'eng': 'Computer Networks and Communication',
              'swe': 'Datornätverk och kommunikation'
              },
    '10282': {'eng': 'Computer Networks',
              'swe': 'Datornätverk'
              },
    '10459': {'eng': 'Computer Networks',
              'swe': 'Datornät'
              },
    '10280': {'eng': 'Computer Science',
              'swe': 'Datalogi'
              },
    '10283': {'eng': 'Computer Systems',
              'swe': 'Datorsystem'
              },
    '10454': {'eng': 'Computer Technology and Graphic Programming',
              'swe': 'Datateknik och grafikprogrammering'
              },
    '10456': {'eng': 'Computer Technology and Real Time Programming',
              'swe': 'Datateknik och realtidsprogrammering'
              },
    '10455': {'eng': 'Computer Technology and Software Engineering',
              'swe': 'Datateknik och programutveckling'
              },
    '10457': {'eng': 'Computer Technology, Networks and Security',
              'swe': 'Datateknik, nätverk och säkerhet'
              },
    '10458': {'eng': 'Computer Technology, Program- and System Development',
              'swe': 'Datateknik, program- och systemutveckling'
              },
    '10268': {'eng': 'Concrete Structures',
              'swe': 'Betongbyggnad'
              },
    '10341': {'eng': 'Condensed Matter Physics',
              'swe': 'Kondenserade materiens fysik'
              },
    '10274': {'eng': 'Construction Management and Economics',
              'swe': 'Byggandets organisation och ekonomi'
              },
    '10278': {'eng': 'Construction Management',
              'swe': 'Byggprojektledning'
              },
    '10448': {'eng': 'Constructional Design',
              'swe': 'Byggdesign'
              },
    '10450': {'eng': 'Constructional Engineering and Design with Business Economics',
              'swe': 'Byggteknik och design med ekonomi'
              },
    '10451': {'eng': 'Constructional Engineering and Design',
              'swe': 'Byggteknik och design'
              },
    '10342': {'eng': 'Corrosion Science',
              'swe': 'Korrosionslära'
              },
    '10284': {'eng': 'Design and Building',
              'swe': 'Design och byggande'
              },
    '10445': {'eng': 'Design and Product Development',
              'swe': 'Design och produktframtagning'
              },
    '10446': {'eng': 'Design and Vehicle Engineering',
              'swe': 'Farkostteknik'
              },
    '10285': {'eng': 'Discrete Mathematics',
              'swe': 'Diskret matematik'
              },
    '10257': {'eng': 'Economics of Innovation and Growth',
              'swe': 'Innovations- och tillväxtekonomi'
              },
    '10289': {'eng': 'Electric Power Systems',
              'swe': 'Elektriska energisystem'
              },
    '10463': {'eng': 'Electrical Engineering with Industrial Economy',
              'swe': 'Elektroteknik med industriell ekonomi'
              },
    '10295': {'eng': 'Electrical Engineering',
              'swe': 'Elektroteknik'
              },
    '10290': {'eng': 'Electrical Machines and Drives',
              'swe': 'Elektriska maskiner och drivsystem'
              },
    '10291': {'eng': 'Electrical Machines and Power Electronic',
              'swe': 'Elektriska maskiner och kraftelektronik'
              },
    '10287': {'eng': 'Electrical Measurements',
              'swe': 'Elektrisk mätteknik'
              },
    '10288': {'eng': 'Electrical Plant Engineering',
              'swe': 'Elektriska anläggningar'
              },
    '10292': {'eng': 'Electroacoustics',
              'swe': 'Elektroakustik'
              },
    '10418': {'eng': 'Electromagnetic Theory',
              'swe': 'Teoretisk elektroteknik'
              },
    '10294': {'eng': 'Electronic System Design',
              'swe': 'Elektroniksystemkonstruktion'
              },
    '10293': {'eng': 'Electronic- and Computer Systems',
              'swe': 'Elektronik- och datorsystem'
              },
    '10461': {'eng': 'Electronics and Communications',
              'swe': 'Elektronik och kommunikation'
              },
    '10462': {'eng': 'Electronics Design',
              'swe': 'Elektronikkonstruktion'
              },
    '10466': {'eng': 'Embedded System Design',
              'swe': 'Inbyggda system'
              },
    '10296': {'eng': 'Energy and Climate Studies',
              'swe': 'Energi och klimatstudier'
              },
    '10297': {'eng': 'Energy and Furnace Technology',
              'swe': 'Energi- och ugnsteknik'
              },
    '10298': {'eng': 'Energy Processes',
              'swe': 'Energiprocesser'
              },
    '10251': {'eng': 'Energy Technology',
              'swe': 'Energiteknik'
              },
    '10487': {'eng': 'Engineering and Management',
              'swe': 'Teknik och management'
              },
    '10415': {'eng': 'Engineering Material Physics',
              'swe': 'Teknisk materialfysik'
              },
    '10488': {'eng': 'Engineering Physics',
              'swe': 'Teknisk fysik'
              },
    '10255': {'eng': 'Entrepreneurship and Innovation Management',
              'swe': 'Entreprenörskap och innovationsledning'
              },
    '10376': {'eng': 'Environmental Assessment',
              'swe': 'Miljöbedömning'
              },
    '10377': {'eng': 'Environmental Strategies',
              'swe': 'Miljöstrategisk analys'
              },
    '10300': {'eng': 'Ergonomics',
              'swe': 'Ergonomi'
              },
    '10447': {'eng': 'Facilities for Infrastructure',
              'swe': 'Anläggningar för infrastruktur'
              },
    '10304': {'eng': 'Fiber Technology',
              'swe': 'Fiberteknologi'
              },
    '10464': {'eng': 'Finance',
              'swe': 'Finans'
              },
    '28052': {'eng': 'Financial Mathematics',
              'swe': 'Finansiell matematik'
              },
    '10402': {'eng': 'Fluid Mechanics',
              'swe': 'Strömningsmekanik'
              },
    '10316': {'eng': 'Foundry Technology',
              'swe': 'Gjuteriteknik'
              },
    '10309': {'eng': 'Fusion Plasma Physics',
              'swe': 'Fusionsplasmafysik'
              },
    '10314': {'eng': 'Geodesy',
              'swe': 'Geodesi'
              },
    '10315': {'eng': 'Geoinformatics',
              'swe': 'Geoinformatik'
              },
    '10317': {'eng': 'Ground Water Chemistry',
              'swe': 'Grundvattenkemi'
              },
    '10440': {'eng': 'Heat Transfer',
              'swe': 'Värmetransporter'
              },
    '10435': {'eng': 'Heating and Ventilating Technology',
              'swe': 'Uppvärmnings- och ventilationsteknik'
              },
    '10321': {'eng': 'High Voltage Engineering',
              'swe': 'Högspänningsteknik'
              },
    '10439': {'eng': 'Highway Engineering',
              'swe': 'Vägteknik'
              },
    '10412': {'eng': 'History of Technology',
              'swe': 'Teknikhistoria'
              },
    '10380': {'eng': 'Human - Computer Interaction',
              'swe': 'Människa - datorinteraktion'
              },
    '10437': {'eng': 'Hydraulic Engineering',
              'swe': 'Vattenbyggnad'
              },
    '10322': {'eng': 'Industrial Biotechnology',
              'swe': 'Industriell bioteknologi'
              },
    '10469': {'eng': 'Industrial Business Administration and Manufacturing',
              'swe': 'Industriell ekonomi och produktion'
              },
    '10327': {'eng': 'Industrial Control Systems',
              'swe': 'Industriella styrsystem'
              },
    '10323': {'eng': 'Industrial Design',
              'swe': 'Industriell design'
              },
    '10324': {'eng': 'Industrial Ecology',
              'swe': 'Industriell ekologi'
              },
    '10325': {'eng': 'Industrial Economics and Management',
              'swe': 'Industriell ekonomi'
              },
    '10468': {'eng': 'Industrial Economy and Entrepreneurship',
              'swe': 'Industriell ekonomi och entreprenörsskap'
              },
    '10467': {'eng': 'Industrial IT',
              'swe': 'Industriell IT'
              },
    '10329': {'eng': 'Information and Communication Technology',
              'swe': 'Informations- och kommunikationsteknik'
              },
    '10328': {'eng': 'Information and Software Systems',
              'swe': 'Information- och programvarusystem'
              },
    '10330': {'eng': 'Information Technology',
              'swe': 'Informationsteknik'
              },
    '10470': {'eng': 'Innovation and Design',
              'swe': 'Innovation och design'
              },
    '10382': {'eng': 'Inorganic Chemistry',
              'swe': 'Oorganisk kemi'
              },
    '10331': {'eng': 'Integrated Product Development',
              'swe': 'Integrerad produktutveckling'
              },
    '10313': {'eng': 'Internal Combustion Engineering',
              'swe': 'Förbränningsmotorteknik'
              },
    '10354': {'eng': 'Land and Water Resources',
              'swe': 'Mark- och vattenresurslära'
              },
    '10254': {'eng': 'Land Management',
              'swe': 'Fastighetsvetenskap'
              },
    '10352': {'eng': 'Lightweight Structures',
              'swe': 'Lättkonstruktioner'
              },
    '10475': {'eng': 'Logistics, Business Administration and Manufacturing',
              'swe': 'Logistik, ekonomi och produktion'
              },
    '10350': {'eng': 'Logistics',
              'swe': 'Logistik'
              },
    '10356': {'eng': 'Machine Design',
              'swe': 'Maskinkonstruktion'
              },
    '10351': {'eng': 'Machine Elements',
              'swe': 'Läran om maskinelement'
              },
    '10355': {'eng': 'Machine Elements',
              'swe': 'Maskinelement'
              },
    '10363': {'eng': 'Material Physics',
              'swe': 'Materialfysik'
              },
    '10360': {'eng': 'Materials and Process Design',
              'swe': 'Material och processdesign'
              },
    '10444': {'eng': 'Materials Design and Engineering',
              'swe': 'Materialdesign'
              },
    '10361': {'eng': 'Materials Processing',
              'swe': 'Materialens processteknologi'
              },
    '10478': {'eng': 'Materials Science and Engineering',
              'swe': 'Materialvetenskap'
              },
    '10359': {'eng': 'Mathematical Statistics',
              'swe': 'Matematisk statistik'
              },
    '10358': {'eng': 'Mathematics',
              'swe': 'Matematik'
              },
    '10473': {'eng': 'Mechanical Design',
              'swe': 'Konstruktion'
              },
    '10477': {'eng': 'Mechanical Engineering with Industrial Economy',
              'swe': 'Maskinteknik med industriell ekonomi'
              },
    '10476': {'eng': 'Mechanical Engineering',
              'swe': 'Maskinteknik'
              },
    '10368': {'eng': 'Mechanical Metallurgy',
              'swe': 'Mekanisk metallografi'
              },
    '10367': {'eng': 'Mechanics',
              'swe': 'Mekanik'
              },
    '10479': {'eng': 'Mechatronics and Robotics',
              'swe': 'Mekatronik och robotik'
              },
    '10370': {'eng': 'Mechatronics',
              'swe': 'Mekatronik'
              },
    '10366': {'eng': 'Media Technology',
              'swe': 'Medieteknik'
              },
    '10365': {'eng': 'Medical Engineering',
              'swe': 'Medicinsk teknik'
              },
    '10364': {'eng': 'Medical Imaging',
              'swe': 'Medicinsk bildbehandling'
              },
    '10265': {'eng': 'Metal Working',
              'swe': 'Bearbetningsteknik'
              },
    '10375': {'eng': 'Micro Modelling in Process Science',
              'swe': 'Mikromodellering inom processvetenskap'
              },
    '10373': {'eng': 'Microcomputer Systems',
              'swe': 'Mikrodatorsystem'
              },
    '10374': {'eng': 'Microelectronics and Applied Physics',
              'swe': 'Mikroelektronik och tillämpad fysik'
              },
    '10480': {'eng': 'Mobile Communications Systems',
              'swe': 'Mobil kommunikation'
              },
    '10378': {'eng': 'Molecular Biotechnology',
              'swe': 'Molekylär bioteknik'
              },
    '10379': {'eng': 'Music Acoustics',
              'swe': 'Musikakustik'
              },
    '10353': {'eng': 'Naval Systems',
              'swe': 'Marina system'
              },
    '10346': {'eng': 'Nuclear Chemistry',
              'swe': 'Kärnkemi'
              },
    '10395': {'eng': 'Nuclear Reactor Engineering',
              'swe': 'Reaktorteknologi'
              },
    '10381': {'eng': 'Numerical Analysis',
              'swe': 'Numerisk analys'
              },
    '10383': {'eng': 'Optics',
              'swe': 'Optik'
              },
    '10384': {'eng': 'Optimization and Systems Theory',
              'swe': 'Optimeringslära och systemteori'
              },
    '10385': {'eng': 'Organic Chemistry',
              'swe': 'Organisk kemi'
              },
    '10386': {'eng': 'Paper Technology',
              'swe': 'Pappersteknik'
              },
    '10305': {'eng': 'Philosophy',
              'swe': 'Filosofi'
              },
    '10308': {'eng': 'Photonics with Microwave Engineering',
              'swe': 'Fotonik med mikrovågsteknik'
              },
    '10312': {'eng': 'Physical Chemistry',
              'swe': 'Fysikalisk kemi'
              },
    '10311': {'eng': 'Physical Electrotechnology',
              'swe': 'Fysikalisk elektroteknik'
              },
    '10372': {'eng': 'Physical Metallurgy',
              'swe': 'Metallografi'
              },
    '10310': {'eng': 'Physics',
              'swe': 'Fysik'
              },
    '10431': {'eng': 'Planning of Traffic and Transportation',
              'swe': 'Trafikplanering'
              },
    '10387': {'eng': 'Plasma Physics',
              'swe': 'Plasmafysik'
              },
    '10389': {'eng': 'Polymer Technology',
              'swe': 'Polymerteknologi'
              },
    '10388': {'eng': 'Polymeric Materials',
              'swe': 'Polymera material'
              },
    '10286': {'eng': 'Power Electronics',
              'swe': 'Effektelektronik'
              },
    '10362': {'eng': 'Process Science of Materials',
              'swe': 'Materialens processvetenskap'
              },
    '10390': {'eng': 'Product Realisation and Management',
              'swe': 'Produktframtagning'
              },
    '10326': {'eng': 'Production Engineering',
              'swe': 'Industriell produktion'
              },
    '10319': {'eng': 'Project in Fluid Power',
              'swe': 'Hydraulik och pneumatik'
              },
    '10392': {'eng': 'Project Management and Operational Development',
              'swe': 'Projektledning och verksamhetsutveckling'
              },
    '10357': {'eng': 'Pulp Technology',
              'swe': 'Massateknologi'
              },
    '10394': {'eng': 'Radio Communication Systems',
              'swe': 'Radiosystemteknik'
              },
    '10393': {'eng': 'Radio Electronics',
              'swe': 'Radioelektronik'
              },
    '10333': {'eng': 'Railway Operation',
              'swe': 'Järnväg och tågtrafik'
              },
    '10334': {'eng': 'Railway Technology',
              'swe': 'Järnvägsteknik'
              },
    '10347': {'eng': 'Reactor Safety',
              'swe': 'Kärnkraftsäkerhet'
              },
    '10252': {'eng': 'Real Estate Development and Land Law',
              'swe': 'Mark- och fastighetsjuridik'
              },
    '10302': {'eng': 'Real Estate Economics',
              'swe': 'Fastighetsekonomi'
              },
    '10465': {'eng': 'Real Estate Management',
              'swe': 'Förvaltning'
              },
    '10303': {'eng': 'Real Estate Planning',
              'swe': 'Fastighetsteknik'
              },
    '10345': {'eng': 'Refrigerating Engineering',
              'swe': 'Kylteknik'
              },
    '10396': {'eng': 'Regional Planning',
              'swe': 'Regional planering'
              },
    '10421': {'eng': 'Reliability Centred Asset Management for Electrical Power Systems',
              'swe': 'Tillförlitlighetsananlys för elkraftsystem'
              },
    '10398': {'eng': 'Risk and Safety',
              'swe': 'Risk och säkerhet'
              },
    '10407': {'eng': 'Safety Research',
              'swe': 'Säkerhetsforskning'
              },
    '10267': {'eng': 'Scientific Computing',
              'swe': 'Beräkningsteknik'
              },
    '10318': {'eng': 'Semiconductor Materials',
              'swe': 'Halvledarmaterial'
              },
    '10400': {'eng': 'Signal Processing',
              'swe': 'Signalbehandling'
              },
    '10483': {'eng': 'Software Design',
              'swe': 'Programvaruutveckling'
              },
    '10391': {'eng': 'Software Engineering',
              'swe': 'Programvaruteknik'
              },
    '10482': {'eng': 'Software Engineering',
              'swe': 'Programutveckling'
              },
    '10332': {'eng': 'Soil and Rock Mechanics',
              'swe': 'Jord- och bergmekanik'
              },
    '10320': {'eng': 'Solid Mechanics',
              'swe': 'Hållfasthetslära'
              },
    '10301': {'eng': 'Solid State Electronics',
              'swe': 'Fasta tillståndets elektronik'
              },
    '10348': {'eng': 'Sound and Image Processing',
              'swe': 'Ljud- och bildbehandling'
              },
    '10443': {'eng': 'Space and Plasma Physics',
              'swe': 'Rymd- och plasmafysik'
              },
    '10399': {'eng': 'Space Physics',
              'swe': 'Rymdfysik'
              },
    '10408': {'eng': 'Speech Communication',
              'swe': 'Talkommunikation'
              },
    '10409': {'eng': 'Speech Communication',
              'swe': 'Talöverföring'
              },
    '10403': {'eng': 'Steel Structures',
              'swe': 'Stålbyggnad'
              },
    '10272': {'eng': 'Structural Design and Bridges',
              'swe': 'Brobyggnad'
              },
    '10474': {'eng': 'Structural Engineering',
              'swe': 'Konstruktionsteknik'
              },
    '10276': {'eng': 'Structural Mechanics and Engineering',
              'swe': 'Byggnadsstatik'
              },
    '10442': {'eng': 'Surface Chemistry',
              'swe': 'Ytkemi'
              },
    '10441': {'eng': 'Surface Coating Technology',
              'swe': 'Ytbehandlingsteknik'
              },
    '10414': {'eng': 'Surveying',
              'swe': 'Teknisk geodesi'
              },
    '10436': {'eng': 'Sustainable Buildings',
              'swe': 'Uthålliga byggnader'
              },
    '10750': {'eng': 'Sustainable development',
              'swe': 'Hållbar utveckling'
              },
    '10486': {'eng': 'System Engineering',
              'swe': 'Systemutveckling'
              },
    '10404': {'eng': 'System-on-Chip',
              'swe': 'System på kisel'
              },
    '10405': {'eng': 'Systems Analysis and Economics',
              'swe': 'Systemanalys och ekonomi'
              },
    '10406': {'eng': 'Systems Engineering',
              'swe': 'Systemteknik'
              },
    '10413': {'eng': 'Technical Acoustics',
              'swe': 'Teknisk akustik'
              },
    '10411': {'eng': 'Technology and Learning',
              'swe': 'Teknik och lärande'
              },
    '10489': {'eng': 'Tele and Data Communication',
              'swe': 'Tele- och datakommunikation'
              },
    '10417': {'eng': 'Telecommunication Systems',
              'swe': 'Telekommunikationssystem'
              },
    '10416': {'eng': 'Teleinformatics',
              'swe': 'Teleinformatik'
              },
    '10419': {'eng': 'Theoretical Physics',
              'swe': 'Teoretisk fysik'
              },
    '10343': {'eng': 'Thermal Engineering',
              'swe': 'Kraft- och värmeteknologi'
              },
    '10430': {'eng': 'Traffic and Transport Planning',
              'swe': 'Trafik- och transportplanering'
              },
    '10432': {'eng': 'Transport- and Location Analysis',
              'swe': 'Transport- och lokaliseringsanalys'
              },
    '20650': {'eng': 'Urban and Regional Planning',
              'swe': 'Urban och regional planering'
              },
    '10401': {'eng': 'Urban Planning and Design',
              'swe': 'Stadsplanering och design'
              },
    '10307': {'eng': 'Vehicle Engineering',
              'swe': 'Fordonsteknik'
              },
    '10438': {'eng': 'Water Resources Engineering',
              'swe': 'Vattenvårdsteknik'
              },
    '10259': {'eng': 'Water, Sewage and Waste',
              'swe': 'VA och avfall'
              },
    '10433': {'eng': 'Wood Chemistry',
              'swe': 'Träkemi'
              },
    '10434': {'eng': 'Wood Technology and Processing',
              'swe': 'Träteknologi'
              },
    '10263': {'eng': 'Work Science',
              'swe': 'Arbetsvetenskap'
              },
    '34700': { 'eng': 'Master of Science in Engineering - Engineering Chemistry',
               'swe': 'Civilingenjörsexamen - Teknisk kemi'
               },
    '34550': { 'eng': 'Master of Science - Information and Network Engineering',
               'swe': 'Teknologie masterexamen - Information och nätverksteknologi'
               },
    '35000': { 'eng': 'Master of Science - Technology, Work and Health',
               'swe': 'Teknologie masterexamen - Teknik, arbete och hälsa'
               },
    '30301': { 'eng': 'Bridging Teacher Education Programme in Mathematics,Science and Technology for Graduates with a Third Cycle Degree',
               'swe': 'Kompletterande pedagogisk utbildning för ämneslärarexamen i matematik, naturvetenskap och teknik för forskarutbildade'
               },
    '30300': { 'eng': 'Bridging Teacher Education Programme',
               'swe': 'Kompletterande pedagogisk utbildning'
               }
}

levels_in_diva={
    'H1': { 'eng': 'Independent thesis Advanced level (degree of Master (One Year))',
            'swe': 'Självständigt arbete på avancerad nivå (magisterexamen)'
           },
    'H2': { 'eng': 'Independent thesis Advanced level (degree of Master (Two Years))',
            'swe': 'Självständigt arbete på avancerad nivå (masterexamen)'
           },
    
    'H3': { 'eng': 'Independent thesis Advanced level (professional degree)',
            'swe': 'Självständigt arbete på avancerad nivå (yrkesexamen)'
            },
    
    'M1': { 'eng': 'Independent thesis Basic level (university diploma)',
            'swe': 'Självständigt arbete på grundnivå (högskoleexamen)'
            },

    'M2': { 'eng': 'Independent thesis Basic level (degree of Bachelor)',
            'swe': 'Självständigt arbete på grundnivå (kandidatexamen)'
            },

    'M3': { 'eng': 'Independent thesis Basic level (professional degree)',
            'swe': 'Självständigt arbete på grundnivå (yrkesexamen)'
            },
    
    'M4': { 'eng': 'Independent thesis Basic level (Higher Education Diploma (Fine Arts))',
            'swe': 'Självständigt arbete på grundnivå (konstnärlig högskoleexamen)'
            },

    'M5': { 'eng': 'Independent thesis Basic level (degree of Bachelor of Fine Arts)',
            'swe': 'Självständigt arbete på grundnivå (konstnärlig kandidatexamen)'
            },
    
    'L1': { 'eng': 'Student paper first term',
            'swe': 'Studentarbete första termin'
            },
    
    'L2': { 'eng': '>Student paper second term',
            'swe': 'Studentarbete övrigt'
           },

    'L3': { 'eng': 'Student paper other',
            'swe': 'Studentarbete andra termin'
            }
}

def guess_diva_level_code_from_program(prgmcode):
    pname_swe=programcodes[prgmcode]['swe']
    if pname_swe.find('Civilingenjör') == 0 or pname_swe.find('Arkitektutbildning') == 0 or pname_swe.find("Masterprogram") == 0:
        return 'H2'
    elif pname_swe.find("Magisterprogram") == 0:
        return 'H1'
    elif pname_swe.find("Kandidatprogram") == 0:
        return 'M2'
    elif pname_swe.find("Högskoleingenjör") == 0:
        return 'M1'
    else:
        print("guess_diva_level_code_from_program: Cannot figure out diva_level_code from program code ({}) - did not match anything".format(prgmcode))
        return None


def lookup_subject_area_eng(s1):
    for s in subject_area_codes_diva:
        se=subject_area_codes_diva[s].get('eng', None)
        if se and se == s1:
            return s
    return None

university_credits_diva={
    '4': { 'credits': 5.0, # 5 HE credits
           'swe': '3 poäng / 5 hp'
          },
    '5': { 'credits': 7.5, # 7,5 HE credits
           'swe': '5 poäng / 7,5 hp'
          },
    '7': { 'credits': 10.0, # 10 HE credits
           'swe': '7 poäng / 19 hp'
           },
    '8': { 'credits': 12.0, #  12 HE credits
           'swe': '8 poäng / 12 hp'
           },
    '9': { 'credits': 14.0, # 14 HE credits
           'swe': '9 poäng / 14 hp'
           },
    '10': { 'credits': 15.0, # 15 HE credits
            'swe': '10 poäng / 15 hp'
            },
    '16': { 'credits': 16.0, # 16 HE credits
            'swe': '11 poäng / 16 hp'
            },
    '12': { 'credits': 18.0, # 18 HE credits
            'swe': '12 poäng / 18 hp'
            },
    '17': { 'credits': 20.0, # 20 HE credits
            'swe': '13 poäng / 20 hp'
            },
    '15': { 'credits': 22.5, # 22,5 HE credits
            'swe': '15 poäng / 22.5 hp'
            },
    '28': { 'credits': 28.0, # 28 HE credits
            'swe': '19 poäng / 28 hp'
            },
    '20': { 'credits': 30.0, # 30 HE credits
            'swe': '20 poäng / 30 hp'
        },
    '33': { 'credits': 35.0, # 33 HE credits
            'swe': '23 poäng / 35 hp'
            },
    '25': { 'credits': 37.5, # 37,5 HE credits
            'swe': '25 poäng / 37,5 hp'
            },
    '30': { 'credits': 45.0, # 45 HE credits
            'swe': '30 poäng / 45 hp'
            },
    '40': { 'credits': 60.0, # 60 HE credits
            'swe': '40 poäng / 60 hp'
            },
    '60': { 'credits': 90.0, # 90 HE credits
            'swe': '60 poäng / 90 hp'
            },
    '80': { 'credits': 120.0, # 120 HE credits
            'swe': '80 poäng / 120 hp'
            },
    '120': {'credits': 180.0, # 180 HE credits
            'swe': '120 poäng / 180 hp'
             },
    '140': {'credits': 210.0, # 210 HE credits
            'swe': '140 poäng / 210 hp'
             },
    '160': {'credits': 240.0, # 240 HE credits
            'swe': '160 poäng / 240 hp'
             },
    '200': {'credits': 300.0, # 300 HE credits
            'swe': '200 poäng / 300 hp'
             },
    '220': {'credits': 330.0, # 330 HE credits
            'swe': '220 poäng / 330 hp'
             }
}

def lookup_swe_string_credits_diva(fp):
    for s in university_credits_diva:
        cfp=university_credits_diva[s].get('credits', None)
        if cfp and abs(cfp - fp) < 0.4:
            return university_credits_diva[s]['swe']
    return None

def filter_education_programs(exam, area):
    possible_diva_codes_exam=set()
    possible_diva_codes=set()
    for p in education_program_diva:
        if exam.find('Bachelor') >= 0:
            if education_program_diva[p]['eng'].find(exam[0:7]) == 0 or education_program_diva[p]['swe'].find(exam[0:7]) == 0:
                possible_diva_codes_exam.add(p)
        else:
            if education_program_diva[p]['eng'].find(exam) >= 0 or education_program_diva[p]['swe'].find(exam) >= 0:
                possible_diva_codes_exam.add(p)

    for p in possible_diva_codes_exam:
        if education_program_diva[p]['eng'].find(area) >= 0 or education_program_diva[p]['swe'].find(area) >= 0:
            possible_diva_codes.add(p)
    return possible_diva_codes

def process_dict_to_XML(content, extras):
    global testing
    #
    import xml.etree.ElementTree as ET
    root = ET.Element("modsCollection")
    root.set("xmlns", "http://www.loc.gov/mods/v3")
    root.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
    root.set("xsi:schemaLocation", "http://www.loc.gov/mods/v3 http://www.loc.gov/standards/mods/v3/mods-3-2.xsd")
    mods = ET.Element("mods")
    root.append(mods)
    mods.set("xmlns", "http://www.loc.gov/mods/v3")
    mods.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
    mods.set("xmlns:xlink", "http://www.w3.org/1999/xlink")
    mods.set("version", "3.2")
    mods.set("xsi:schemaLocation", "http://www.loc.gov/mods/v3 http://www.loc.gov/standards/mods/v3/mods-3-2.xsd")
    #genre
    genre2= ET.Element("genre")
    mods.append(genre2)
    genre2.set("authority" , "diva")
    genre2.set("type", "publicationTypeCode")
    genre2.text="studentThesis"
    #
    genre= ET.Element("genre")
    mods.append(genre)
    genre.set("authority" , "diva")
    genre.set("type", "publicationType")
    genre.set("lang", "swe")
    genre.text="Studentuppsats (Examensarbete)"
    #
    genre3= ET.Element("genre")
    mods.append(genre3)
    genre3.set("authority" , "diva")
    genre3.set("type", "publicationType")
    genre3.set("lang", "eng")
    genre3.text="Student thesis"
    #
    genre4= ET.Element("genre")
    mods.append(genre4)
    genre4.set("authority" , "diva")
    genre4.set("type", "publicationType")
    genre4.set("lang", "nor")
    genre4.text="Oppgave"
    #
    author_names=list()
    for i in range(1, 10):
        which_author="Author{}".format(i)
        author=content.get(which_author, None)
        if author:
            writer = ET.Element("name")
            mods.append(writer)
            #
            writer.set("type", "personal")
            local_user_Id=author.get('Local User Id')
            if local_user_Id:
                writer.set("authority", "kth")
                writer.set("xlink:href", local_user_Id)
            last_name=author.get('Last name', None)
            if last_name:
                name = ET.SubElement(writer, "namePart")
                name.set("type", "family")
                name.text=last_name
            #
            first_name=author.get('First name', None)        
            if first_name:
                fn = ET.SubElement(writer, "namePart")
                fn.set("type", "given")
                fn.text=first_name
            #
            #<description>orcid.org=0000-0002-6066-746X</description>
            orcid=author.get('ORCiD', None)
            if orcid:
                orcid_entry=ET.SubElement(writer, "description")
                orcid_entry.text="orcid.org={}".format(orcid)
                #
            email=author.get('E-mail', None)
            if email:
                mail = ET.SubElement(writer, "description")
                mail.text = "email={}".format(email)

            role =ET.SubElement(writer, "role")
            roleTerm = ET.SubElement(role, "roleTerm")
            roleTerm.set("type" , "code")
            roleTerm.set("authority" , "marcrelator")
            roleTerm.text ="aut"
        else:                   # if there was no such author, then stop looping
            break
    #
    #Examinor
    # "Examiner1": {"Last name": "Maguire Jr.", "First name": "Gerald Q.", "Local User Id": "u1d13i2c", "E-mail": "maguire@kth.se", "organisation": {"L1": "School of Electrical Engineering and Computer Science ", "L2": "Computer Science"}}
    examiner_info=content.get('Examiner1')
    if examiner_info:
        examinator = ET.Element("name")
        mods.append(examinator)
        examinator.set("type", "personal")
        local_user_Id=examiner_info.get('Local User Id')
        if local_user_Id:
            examinator.set("authority", "kth")
            examinator.set("xlink:href", local_user_Id)
        last_name=examiner_info.get('Last name', None)
        if last_name:
            name = ET.SubElement(examinator , "namePart")
            name.set("type", "family")
            name.text=last_name
        #
        first_name=examiner_info.get('First name', None)        
        if first_name:
            fn = ET.SubElement(examinator , "namePart")
            fn.set("type", "given")
            fn.text=first_name
            #
        email=examiner_info.get('E-mail', None)
        if email:
            mail = ET.SubElement(examinator , "description")
            mail.text = "email={}".format(email)

        #<description>orcid.org=0000-0002-6066-746X</description>
        orcid=examiner_info.get('ORCiD', None)
        if orcid:
            orcid_entry=ET.SubElement(examinator , "description")
            orcid_entry.text="orcid.org={}".format(orcid)
        #
        e_org=examiner_info.get('organisation')
        if e_org:
            e_org_l1=e_org.get('L1')
            e_org_l2=e_org.get('L2')
            if e_org_l1 and e_org_l2:
                organization="KTH, {0}, {1}".format(e_org_l1.strip(), e_org_l2.strip())
            elif  e_org_l1 and not e_org_l2:
                organization="KTH, {0}".format(e_org_l1.strip())
            else:
                organization=None
            #\
            if organization:
                org = ET.SubElement(examinator , "affiliation")
                org.text = organization
                examiner_organization=organization
        #
        # job = ET.SubElement(examinator , "namePart")
        # job.set("type", "termsOfAddress")
        # job.text = content.get("jobTitle_examinar")
        #
        role=ET.SubElement(examinator, "role")
        roleTerm=ET.SubElement(role, "roleTerm")
        roleTerm.set("type" , "code")
        roleTerm.set("authority" , "marcrelator")
        roleTerm.text ="mon"

    #"Supervisor1": {"Last name": "Västberg", "First name": "Anders", "Local User Id": "u1ft3a12", "E-mail": "vastberg@kth.se", "organisation": {"L1": "School of Electrical Engineering and Computer Science ", "L2": "Computer Science"}}
    supervisr_names=list()
    for i in range(1, 10):
        which_supervisor="Supervisor{}".format(i)
        supervisor=content.get(which_supervisor, None)
        if supervisor:
            #supervisor
            handledare = ET.Element("name")
            mods.append(handledare)

            last_name=supervisor.get('Last name', None)
            if last_name:
                handledare.set("type", "personal")
                local_user_Id=supervisor.get('Local User Id')
                if local_user_Id:
                    handledare.set("authority", "kth")
                    handledare.set("xlink:href", local_user_Id)

                name = ET.SubElement(handledare , "namePart")
                name.set("type", "family")
                name.text= last_name

            first_name=supervisor.get('First name', None)
            if first_name:
                fn = ET.SubElement(handledare , "namePart")
                fn.set("type", "given")
                fn.text = first_name

            s_org=supervisor.get('organisation', None)
            if s_org:
                s_org_l1=s_org.get('L1')
                s_org_l2=s_org.get('L2')
                if s_org_l1 and s_org_l2:
                    organization="{0}, {1}".format(s_org_l1.strip(), s_org_l2.strip())
            elif  s_org_l1 and not s_org_l2:
                organization="{0}".format(s_org_l1.strip())
            else:
                s_org=supervisor.get('Other organisation', None)
                print("s_org={}".format(s_org))
                if s_org:
                    organization="{0}".format(s_org.strip())
                else:
                    organization=None

            if organization:
                org = ET.SubElement(handledare , "affiliation")
                org.text = organization

            email=supervisor.get('E-mail', None)
            if email:
                mail = ET.SubElement(handledare, "description")
                mail.text = "email={}".format(email)

            # jobh = ET.SubElement(handledare , "namePart")
            # jobh.set("type", "termsOfAddress")
            # jobh.text = content.get("jobTitle-en_supervisor")

            role =ET.SubElement(handledare , "role")
            roleTerm = ET.SubElement(role , "roleTerm")
            roleTerm.set("type" , "code")
            roleTerm.set("authority" , "marcrelator")
            roleTerm.text ="ths"
        else:                   # if there was no such supervisor, then stop looping
            break

    
    #organization
    orglist = []
    organisation = ET.Element("name")
    mods.append(organisation)
    for word in examiner_organization.split(","):
        org = ET.SubElement(organisation, "namePart")
        org.text = word
    role =ET.SubElement(organisation , "role")
    roleTerm = ET.SubElement(role , "roleTerm")
    roleTerm.set("type" , "code")
    roleTerm.set("authority" , "marcrelator")
    roleTerm.text ="pbl"

    # "Title": {"Main title": "This is the title in the language of the thesis", "Subtitle": "An subtitle in the language of the thesis", "Language": "eng"}, "Alternative title": {"Main title": "Detta är den svenska översättningen av titeln", "Subtitle": "Detta är den svenska översättningen av undertiteln", "Language": "swe"}
    title=content.get('Title', None)
    if title:
        thesis_main_title=title.get('Main title', None)
        language=title.get('Language', None)
        if language is None:
            language='eng'
            print("no language specied, guessing English")

        thesis_main_subtitle=title.get('Subtitle', None)

        #title and subtitle 
        heading = ET.Element("titleInfo ")
        mods.append(heading)
        heading.set("lang", language)
        name = ET.SubElement(heading , "title")
        name.text =  thesis_main_title
        if thesis_main_subtitle:
            subname = ET.SubElement(heading , "subTitle")
            subname.text = thesis_main_subtitle
   
    # <titleInfo type="alternative"
    alternative_title=content.get('Alternative title', None)
    if alternative_title:
        alternative_main_title=alternative_title.get('Main title', None)
        alternative_thesis_main_subtitle=alternative_title.get('Subtitle', None)

        alternative_language=alternative_title.get('Language', None)
        if alternative_language is None:
            alternative_language='swe'
            print("no language specied, guessing Swedish")

        heading2 = ET.Element("titleInfo ")
        mods.append(heading2)
        heading2.set("lang", alternative_language)
        heading2.set("type", "alternative")
        name = ET.SubElement(heading2, "title")
        name.text =  alternative_main_title
        if alternative_thesis_main_subtitle:
            subname = ET.SubElement(heading2, "subTitle")
            subname.text = alternative_thesis_main_subtitle

    #keywords
    keywords=content.get('keywords', None)
    if keywords:
        number_of_abstracts=len(keywords)
        if number_of_abstracts > 0:
            for lang in keywords:
                keyterms = ET.Element("subject ")
                mods.append(keyterms)
                keyterms.set("lang", lang)
                keywords_text=keywords[lang]
                keywords_text=keywords_text.replace('\n', ' ') # replace newlines with spaces
                for word in keywords_text.split(","):
                    topic= ET.SubElement(keyterms, "topic")
                    word=word.strip() # remove starting and ending white space
                    topic.text =  word.replace(",", "")

    abstracts=content.get('abstracts', None)
    if abstracts:
        number_of_abstracts=len(abstracts)
        if number_of_abstracts > 0:
            for lang in abstracts:
                abs = ET.Element("abstract ")
                mods.append(abs)
                abs.set("lang", lang)

                abstract_text=abstracts[lang]
                # take care of URLs
                if abstract_text.find('\\url{') >= 0:
                    abstract_text=transform_urls(abstract_text)

                # transform equations
                if mathincluded(abstract_text):
                    abstract_text=transform_math_for_diva(abstract_text)
                abs.text =  abstract_text

    other_info=content.get('Other information', None)
    if other_info:
        physical_description = ET.Element("physicalDescription")
        form = ET.SubElement(physical_description, "form")
        form.set("authority", "marcform")
        form.text="electronic"
        number_of_pages=other_info.get('Number of pages', None)
        if number_of_pages:
            extent = ET.SubElement(physical_description, "extent")
            extent.text=number_of_pages
        mods.append(physical_description)

        #<place><placeTerm>Stockholm</placeTerm></place><publisher>KTH Royal Institute of Technology</publisher>
        originInfo = ET.Element("originInfo")
        mods.append(originInfo)
        place = ET.SubElement(originInfo, "place")
        placeTerm = ET.SubElement(place, "placeTerm")
        placeTerm.text="Stockholm"
        publisher = ET.SubElement(originInfo, "publisher")
        publisher.text="KTH Royal Institute of Technology"

        year=other_info.get('Year', None)
        if year:
            date_issued = ET.SubElement(originInfo, "dateIssued")
            date_issued.text=year

        presentation_info=content.get('Presentation', None)
        if presentation_info:
            # <dateOther type="defence">2021-03-31T15:00:00</dateOther>
            datetime_of_presentation=presentation_info.get('Date', None)
            if datetime_of_presentation:
                defence = ET.SubElement(originInfo, "dateOther")
                defence.set('type', "defence")
                offset=datetime_of_presentation.find(' ')
                if offset > 0:
                    datetime_of_presentation=datetime_of_presentation[0:offset]+'T'+datetime_of_presentation[offset+1:]+':00'
                    defence.text=datetime_of_presentation



    type_of_resource = ET.Element("typeOfResource")
    type_of_resource.text="text"
    mods.append(type_of_resource)

    x=extras.get('trita', None)
    if x:
        trita = x
    else:
        trita = None

    relatedItem = ET.Element("relatedItem ")
    relatedItem.set('type', "series")
    ti = ET.SubElement(relatedItem, "titleInfo")
    series_title=ET.SubElement(ti, "title")
    # split trita string into series and number
    year_string="{}:".format(year)
    offset_to_number=trita.find(year_string)
    if offset_to_number >= 0:
        series_title.text=trita[0:offset_to_number-1]
        if testing:             # for testing we have to use a series from the old version of DiVA
            series_title.text="TRITA-ICT-EX"
    series_id=ET.SubElement(ti, "identifier")
    series_id.set('type', "local")
    if testing:             # for testing we have to use a series from the old version of DiVA
        series_id.text="5952"
    else:
        series_id.text="16855"    # corresponds to the series: TRITA-EECS-EX

    series_number=ET.SubElement(ti, "identifier")
    series_number.set('type', "issue number")
    series_number.text=trita[offset_to_number:]
    mods.append(relatedItem)

    # "Degree": {"Educational program": "Degree Programme in Media Technology", "Level": "2", "Course code": "DA231X", "Credits": "30.0", "Exam": "Degree of Master of Science in Engineering", "subjectArea": "Media Technology"}
    # <note type="level" lang="swe">Självständigt arbete på avancerad nivå (masterexamen)</note><note type="universityCredits" lang="swe">20 poäng / 30 hp</note><location>
    degree_info=content.get('Degree', None)
    if degree_info:
        programcode_info=degree_info.get('programcode', None)
        if programcode_info:
            diva_level_code=guess_diva_level_code_from_program(programcode_info)
            print("diva_level_code={}".format(diva_level_code))
            level = ET.Element("note")
            level.set('lang', "swe")
            level.set('type', "level")
            level.text=levels_in_diva[diva_level_code]['swe']
            mods.append(level)

        # <note type="degree" lang="en">Degree of Doctor of Philosophy</note><note type="degree" lang="sv">Filosofie doktorsexamen</note><language objectPart="defence">
        exam_info=degree_info.get('Exam', None)
        degree = ET.Element("note")
        degree.set('lang', "eng")
        degree.set('type', "degree")
        degree.text=exam_info
        mods.append(degree)


        subjectArea_info=degree_info.get('Credits', None)
        credits = ET.Element("note")
        credits.set('lang', "swe")
        credits.set('type', "universityCredits")
        credits.text=lookup_swe_string_credits_diva(float(subjectArea_info))
        #credits.text="20 poäng / 30 hp"
        mods.append(credits)

        subjectArea_info=degree_info.get('subjectArea', None)
        code_for_subject=lookup_subject_area_eng(subjectArea_info)
        print("subjectArea_info={0}, code_for_subject={1}, ".format(subjectArea_info, code_for_subject))

        if code_for_subject:
            educational_program=ET.Element("subject")
            educational_program.set('lang', "swe")
            educational_program.set('xlink:href', code_for_subject)
            ed_topic=ET.SubElement(educational_program, "topic")
            swe_subject_area=subject_area_codes_diva[code_for_subject].get('swe', None)
            ed_topic.text=swe_subject_area
            ed_topic1=ET.SubElement(educational_program, "genre")
            ed_topic1.text="Subject/course"
            mods.append(educational_program)
        
            educational_program=ET.Element("subject")
            educational_program.set('lang', "eng")
            educational_program.set('xlink:href', code_for_subject)
            ed_topic=ET.SubElement(educational_program, "topic")
            eng_subject_area=subject_area_codes_diva[code_for_subject].get('eng', None)
            ed_topic.text=eng_subject_area
            ed_topic1=ET.SubElement(educational_program, "genre")
            ed_topic1.text="Subject/course"
            mods.append(educational_program)
        else:
            print("missing code for subject: subjectArea_info={0}, ".format(subjectArea_info))

        possible_diva_codes=filter_education_programs(exam_info, subjectArea_info)
        if possible_diva_codes and len(possible_diva_codes) == 1:
            diva_code=list(possible_diva_codes)[0] # take the first an only element from the list
            print("diva_code={}".format(diva_code))
            # the following is hand crafted for a test
            educational_program=ET.Element("subject")
            educational_program.set('lang', "swe")
            educational_program.set('xlink:href', diva_code)
            ed_topic=ET.SubElement(educational_program, "topic")
            #ed_topic.text="Teknologie kandidatexamen - Informations- och kommunikationsteknik"
            ed_topic.text=education_program_diva[diva_code]['swe']
            ed_topic1=ET.SubElement(educational_program, "genre")
            ed_topic1.text="Educational program"
            mods.append(educational_program)

            educational_program=ET.Element("subject")
            educational_program.set('lang', "eng")
            educational_program.set('xlink:href', diva_code)
            ed_topic=ET.SubElement(educational_program, "topic")
            #ed_topic.text="Bachelor of Science - Information and Communication Technology"
            ed_topic.text=education_program_diva[diva_code]['eng']
            ed_topic1=ET.SubElement(educational_program, "genre")
            ed_topic1.text="Educational program"
            mods.append(educational_program)
        else:
            print("Unable to find a unique diva educational program code: exam_info='{0}', subjectArea_info='{1}', possible_diva_codes={2}".format(exam_info, subjectArea_info, possible_diva_codes))

    # <language><languageTerm type="code" authority="iso639-2b">eng</languageTerm></language><note type="venue">Ka-Sal C (Sven-Olof Öhrvik), Kistagången 16, Electrum 1, våningsplan 2, KTH Kista, Stockholm</note>
    # "Presentation": {"Date": "2021-06-18 11:00", "Language": "eng", "Room": "via Zoom https://kth-se.zoom.us/j/61684700718", "Address": "Isafjordsgatan 22 (Kistagången 16)", "City": "Stockholm"}
    #<language objectPart="defence"><languageTerm type="code" authority="iso639-2b">eng</languageTerm></language>
    presentation_info=content.get('Presentation', None)
    if presentation_info:
        lang_of_presentation=presentation_info.get('Language', None)
        if lang_of_presentation:
            language = ET.Element("language")
            language.set('objectPart', "defence")
            languageTerm=ET.SubElement(language, "languageTerm")
            languageTerm.set('type', "code")
            languageTerm.set('authority', "iso639-2b")
            languageTerm.text=lang_of_presentation
            mods.append(language)

            presentation_room=presentation_info.get('Room', None)
            presentation_address=presentation_info.get('Address', None)
            presentation_city=presentation_info.get('City', None)
            if presentation_room:
                venue = ET.Element("note")
                venue.set('type', "venue")
                venue.text=presentation_room
                if presentation_address:
                    venue.text=venue.text+','+presentation_address
                if presentation_city:
                    venue.text=venue.text+','+presentation_city
                mods.append(venue)

    # {"Partner_name": "SVT Interaktiv"},
    #    <note type="cooperation">Saab AB</note>
    cooperation_info=content.get('Cooperation', None)
    if cooperation_info:
        partner_info=cooperation_info.get('Partner_name', None)
        if partner_info:
            partner = ET.Element("note")
            partner.set('type', "cooperation")
            partner.text=partner_info
            mods.append(partner)

    #<subject lang="eng" authority="hsv" xlink:href="10201"><topic>Natural Sciences</topic><topic>Computer and Information Sciences</topic><topic>Computer Sciences</topic></subject><subject lang="swe" authority="hsv" xlink:href="10201"><topic>Naturvetenskap</topic><topic>Data- och informationsvetenskap</topic><topic>Datavetenskap (datalogi)</topic></subject><subject lang="eng" authority="hsv" xlink:href="20205"><topic>Engineering and Technology</topic><topic>Electrical Engineering, Electronic Engineering, Information Engineering</topic><topic>Signal Processing</topic></subject><subject lang="swe" authority="hsv" xlink:href="20205"><topic>Teknik och teknologier</topic><topic>Elektroteknik och elektronik</topic><topic>Signalbehandling</topic></subject>
    # National Subject Categories": "10201, 10206, 10204, 10209"}
    national_subject_categories=content.get('National Subject Categories', None)
    print("national_subject_categories={}".format(national_subject_categories))
    if national_subject_categories:
        categories=national_subject_categories.split(',')
        for c in categories:
            hsv_category=c.strip()
            cat_info=national_subject_categories_dict.get(hsv_category, None)
            if cat_info:
                subject=ET.Element("subject")
                subject.set('lang',"eng")
                subject.set('authority',"hsv")
                subject.set("xlink:href", hsv_category)

                eng_topics=cat_info.get('eng', None)
                if eng_topics:
                    num_topics=len(eng_topics)
                    if num_topics > 0:
                        for topic in eng_topics:
                            st=ET.SubElement(subject, "topic")
                            st.text=topic
                mods.append(subject)
                #
                subject=ET.Element("subject")
                subject.set('lang',"swe")
                subject.set('authority',"hsv")
                subject.set("xlink:href", hsv_category)

                swe_topics=cat_info.get('swe', None)
                if swe_topics:
                    num_topics=len(swe_topics)
                    if num_topics > 0:
                        for topic in swe_topics:
                            st=ET.SubElement(subject, "topic")
                            st.text=topic
                mods.append(subject)

    xmlData = ET.tostring(root, encoding='UTF-8') #  encoding='unicode'
    return xmlData


def main(argv):
    global Verbose_Flag
    global testing
    global course_id


    argp = argparse.ArgumentParser(description="JSON_to_MODS.py: to make a MODS file")

    argp.add_argument('-v', '--verbose', required=False,
                      default=False,
                      action="store_true",
                      help="Print lots of output to stdout")

    argp.add_argument("--config", type=str, default='config.json',
                      help="read configuration from file")

    argp.add_argument("-c", "--canvas_course_id", type=int,
                      # required=True,
                      help="canvas course_id")

    argp.add_argument('-t', '--testing',
                      default=False,
                      action="store_true",
                      help="execute test code"
                      )

    argp.add_argument('-j', '--json',
                      type=str,
                      default="event.json",
                      help="JSON file for extracted data"
                      )

    argp.add_argument('--cycle',
                      type=int,
                      help="cycle of thesis"
                      )

    argp.add_argument('--credits',
                      type=float,
                      help="number_of_credits of thesis"
                      )

    argp.add_argument('--exam',
                      type=int,
                      help="type of exam"
                      )

    argp.add_argument('--area',
                      type=str,
                      help="area of thesis"
                      )

    argp.add_argument('--area2',
                      type=str,
                      help="area of thesis for combined Cinving. and Master's"
                      )

    argp.add_argument('--trita',
                      type=str,
                      help="trita string for thesis"
                      )

    argp.add_argument('--school',
                      type=str,
                      help="school acronym"
                      )

    args = vars(argp.parse_args(argv))

    Verbose_Flag=args["verbose"]

    # If there is a course number argument, then initializae in prepartion for Canvas API calls
    # x=args["canvas_course_id"]
    # if x:
    #     if Verbose_Flag:
    #         print("baseUrl={}".format(baseUrl))

    # course_id=args["canvas_course_id"]
    # print("course_id={}".format(course_id))

    testing=args["testing"]
    print("testing={}".format(testing))

    extras=dict()

    x=args['cycle']
    if x:
        extras['cycle']=x

    x=args['credits']
    if x:
        extras['credits']=x

    x=args['exam']
    if x:
        extras['exam']=x

    x=args['area']
    if x:
        extras['area']=x

    x=args['area2']
    if x:
        extras['area2']=x

    x=args['trita']
    if x:
        extras['trita']=x

    x=args['school']
    if x:
        extras['school_acronym']=x

    d=None
    json_filename=args["json"]
    if json_filename:
        with open(json_filename, 'r', encoding='utf-8') as json_FH:
            try:
                json_string=json_FH.read()
                d=json.loads(json_string)
            except:
                print("Error in reading={}".format(event_string))
                return

            if Verbose_Flag:
                print("read JSON: {}".format(d))

        if d:
            xmlData=process_dict_to_XML(d, extras)
            if xmlData:             # write out results
                with open('modsXML.xml','wb+') as filehandle:
                    filehandle.write(xmlData)
                    filehandle.close()
                    if Verbose_Flag:
                        print("wrote MODS XML: {}".format(xmlData))
    else:
        print("Unknown source for the JSON: {}".format(json_filename))
        return
    

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))


def main(inputjson,outputdir):
    #os.chdir("../../../../../../../../output/parse_result")
    #print("currently mods module at directory: "+os.getcwd())

    with open('../../../../output/parse_result/cache/modsXML.xml','wb+') as filehandle:
        xmlData=modsData(inputjson)
        filehandle.write(xmlData)
        filehandle.close()
        shutil.move('../../../../output/parse_result/cache/modsXML.xml',outputdir+'/modsXML.mods')
    return os.getcwd()+'/'+outputdir+'/modsXML.mods'

        

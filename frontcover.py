#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- mode: python; python-indent-offset: 4 -*-
#
# ./frontcover.py --json input.json --pdf output.pdf --year YYYY
#
# Purpose: create KTH front cover
#
# Example:
#
# ./frontcover.py --json fordiva-example-cleaned.json --pdf output.pdf --year 2022
#
# To get the correct fpdf package od:
# pip install fpdf
#
# 2021-07-25 G. Q. Maguire Jr.
#
import re
import sys

import json
import argparse
import os			# to make OS calls, here to get time zone info

from datetime import datetime
from fpdf import FPDF 

# Graphical alyout of the front cover
# LTLine                       37.40   31.94   556.10  31.94    
# LTFigure                     38.00   736.25  110.85  809.10   
#   LTImage                    38.00   736.25  110.85  809.10   
# LTFigure                     451.65  790.15  556.50  809.10   
#   LTImage                    451.65  790.15  556.50  809.10   

kth_logo = {"x_offset": 38.00,  # The offset is to the upper left corner
            "y_offset": 809.10,
            "y_position": 736.25, # with x_offset the lower left corner
            "filename": "kth_logo.png",
            "height": 72.85,  # 809.10-736.25
            "width": 72.85    # 110.85-38.00
            }

kth_English_logotype = {"x_offset": 451.65,  # The offset is to the upper left corner
                        "y_offset": 809.10,
                        "y_position":790.15, # with x_offset the lower left corner
                        "filename": "KTH_ROYAL_INSTITUTE_OF_TECHNOLOGY_logotype.png",
                        "height": 18.95, # 809.10-790.15
                        "width": 104.85  # 556.50-451.65
                        }

bottom_rule = {"x_offset": 37.40,  # The offset is to the left corner
               "y_offset": 31.94,
               "thickness": 1.0,
               "width": 518.70 # 556.10-37.40
               }
# LTTextBoxHorizontal          38.52   37.09   196.55  45.09    Stockholm, Sweden Click here to enter year
place_and_year = {"x_offset": 38.52,
                  "y_offset": 45.09,
                  "y_position": 37.09, # with x_offset the lower left corner
                  "font": "Arial",
                  "font_size": 8.0
}

#  LTTextBoxHorizontal          71.03   654.68  526.68  680.95   Click here to enter your subject area. For example. Degree Project in Information and 
subject_area = {"x_offset": 71.03,
                "y_offset": 680.95,   # note that what is desired is the space from the bottom of the logo (55.30, i.e. 736.25-55.30)
                "y2_offset": 654.68,  # this is the position of the 2nd line in this field
                "y_position": 668.95, # with x_offset the lower left corner of the first line = 680.95-(12)
                "font": "Arial",
                "font_size": 12.0,
                "line_spacing": 1.08,
                "before": 0.0,
                "after": 8.0,
}

# LTTextBoxHorizontal          71.03   617.65  493.96  644.20   Click here to enter first or second cycle and credits. For example. First cycle 15 

level_credits = {"x_offset": 71.03,
                "y_offset": 644.20,   # note that what is desired is the space from the bottom of the subject_area (654.68-644.20=10.48)
                "y2_offset": 617.65,  # this is the position of the 2nd line in this field
                 "y_position": 632.20, # with x_offset the lower left corner of first line (644.20-12=632.20)
                "font": "Arial",
                "font_size": 12.0,
                "line_spacing": 1.08,
                 "before": 0.0,
                 "after": 8.0,
}

# LTTextBoxHorizontal          71.03   519.54  422.16  573.71   Click here to enter your title 
title_field = {"x_offset": 71.03,
               "y_offset": 573.71,   # note that what is desired is the space from the bottom of the level_credits field (617.65-573.71 43.94)
               "y_position": 519.54, # with x_offset the lower left corner
               "font": "Arial",
               "font_face": "bold",
               "font_size": 26.0,
               "line_spacing": 1.08,
               "before": 0.0,
               "after": 8.0,
}

# LTTextLineHorizontal       71.03   519.54  296.08  535.54   Click here to enter your subtitle
subtitle_field = {"x_offset": 71.03,
                  "y_offset": 535.54,   # note that what is desired is the space from the bottom of the title field
                  "y_position": 519.54, # with x_offset the lower left corner (this seems strange as it is the same as the title!
                  "font": "Arial",
                  "font_size": 16.0,
                  "line_spacing": 1.08,
                  "before": 0.0,
                  "after": 8.0,
}

# LTTextLineHorizontal       71.03   476.38  485.84  488.38   CLICK HERE TO ENTER THE NAME OF THE AUTHOR (FIRST AND LAST
authors_field = {"x_offset": 71.03,
               "y_offset": 488.38,   # note that what is desired is the space from the bottom of the subtitle field
               "y_position": 476.38, # with x_offset the lower left corner
               "font": "Arial",
               "font_face": "bold",
               "font_size": 12.0,
               "line_spacing": 1.08,
               "before": 0.0,
               "after": 8.0,
}

def filled_text_string(pdf, title_string, font_size, x_offset, paperwidth):
    global Verbose_Flag
    font_family=pdf.font_family           # current font family
    font_style=pdf.font_style            # current font style
    font_size=pdf.font_size_pt          # current font size in points
    current_text_lines=[]
    current_text_line=""
    working_width=paperwidth-2.0*x_offset 
    print("working_width={}".format(working_width))

    # for the characters in title_string, add them individually to the current_text_lines until the line is longer that 0.8* paperwidth
    for ts in title_string:
        if ts:
            current_text_line=current_text_line+ts
            string_size=pdf.get_string_width(current_text_line)
            if Verbose_Flag:
                print("string_size={0} for {1}".format(string_size, ts))
            # check if it is time to add a new line to the title
            if (ts == " " and string_size > 0.75*working_width) or (ts == "-" and string_size > 0.80*working_width):
                current_text_lines.append(current_text_line)
                current_text_line=""
    current_text_lines.append(current_text_line)
    return current_text_lines

def get_author_name(d_author):
    author_name="Unknown author"
    if d_author:
        last_name=d_author['Last name']
        first_name=d_author['First name']
        if first_name and last_name:
            author_name="{0} {1}".format(first_name, last_name)
        elif not first_name and last_name:
            author_name="{}".format(last_name)
        elif first_name and not last_name:
            author_name="{0}".format(first_name)
        else:
            print("Unable to determine author's name from {}".format(d_author))
    return author_name.upper()

def main(argv):
    global Verbose_Flag
    global Use_local_time_for_output_flag
    global testing

    argp = argparse.ArgumentParser(description="frontcover.py: make a New KTH frontcover based on the JSON data")

    argp.add_argument('-v', '--verbose', required=False,
                      default=False,
                      action="store_true",
                      help="Print lots of output to stdout")

    argp.add_argument('-t', '--testing',
                      default=False,
                      action="store_true",
                      help="execute test code"
                      )

    argp.add_argument('-p', '--pdf',
                      type=str,
                      default="test.pdf",
                      help="read PDF file"
                      )

    argp.add_argument('-j', '--json',
                      type=str,
                      default="input.json",
                      help="JSON file with degreeName, titles, etc."
                      )

    argp.add_argument('-y', '--year',
                      type=int,
                      default="{}".format(datetime.today().year),
                      help="year for cover"
                      )

    argp.add_argument('-e', '--english',
                      default=False,
                      action="store_true",
                      help="make English cover"
                      )


    args = vars(argp.parse_args(argv))

    Verbose_Flag=args["verbose"]
    
    English_flag=args["english"]

    filename=args["pdf"]
    if Verbose_Flag:
        print("filename={}".format(filename))

    year=args["year"]
    if Verbose_Flag:
        print("year={}".format(year))

    d=None
    json_filename=args["json"]
    if json_filename:
        try:
            with open(json_filename, 'r', encoding='utf-8') as json_FH:
                json_string=json_FH.read()
                d=json.loads(json_string)
        except FileNotFoundError:
            print("File not found: {json_filename}".format(json_filename))
            return

    if Verbose_Flag:
        print("read JSON: {}".format(d))

    #{'Author1': {'Last name': 'Student', 'First name': 'Fake A.', 'Local User Id': 'u100001', 'E-mail': 'a@kth.se', 'organisation': {'L1': 'School of Electrical Engineering and Computer Science'}},
    # 'Author2': {'Last name': 'Student', 'First name': 'Fake B.', 'Local User Id': 'u100002', 'E-mail': 'b@kth.se', 'organisation': {'L1': 'School of Architecture and the Built Environment'}}, 
    # 'Cycle': '1', 'Course code': 'IA150X', 'Credits': '15.0',
    # 'Degree1': {'Educational program': "Bachelor's Programme in Information and Communication Technology",
    #             'programcode': 'TCOMK', 'Degree': 'Bachelors degree', 'subjectArea': 'Technology'},
    # 'Title': {'Main title': 'This is the title in the language of the thesis',
    #           'Subtitle': 'A subtitle in the language of the thesis', 'Language': 'eng'}
    if not English_flag:
        if d['Title']:
            if d['Title'].get('Language', None) == 'eng':
                English_flag=True
            else:
                English_flag=False
    print("English_flag={}".format(English_flag))

    pdf = FPDF(orientation = 'P', unit = 'pt', format='A4')
    pdf.add_page()

    # insert the texts in pdf 
    paperheight=842.0
    #paperheight=841.920
    if pdf:
        lastpage = pdf.page
        print("lastpage={}".format(lastpage))
        width=pdf.fw_pt
        height = pdf.fh_pt
        paperheight = pdf.fh_pt
        paperwidth=pdf.fw_pt
        print("width={0}, height={1}".format(width, height))
 

    pdf.image(kth_logo['filename'], x = kth_logo['x_offset'], y = paperheight-kth_logo['y_offset'], w = kth_logo['width'], h = kth_logo['height'], type = 'png', link = '')   

    
    if English_flag:
        pdf.image(kth_English_logotype['filename'], x = kth_English_logotype['x_offset'], y = paperheight-kth_English_logotype['y_offset'], w = kth_English_logotype['width'], h = kth_English_logotype['height'], type = 'png', link = '')   

    pdf.set_draw_color(25, 84, 166) # kth-blue
    pdf.set_line_width(bottom_rule['thickness'])
    pdf.line(bottom_rule['x_offset'], paperheight-bottom_rule['y_offset'], bottom_rule['x_offset']+bottom_rule['width'], (paperheight-bottom_rule['y_offset']))

    pdf.add_font("Arial", '', '/usr/share/fonts/truetype/arial.ttf', uni=True) 
    pdf.set_font("Arial", size=int(place_and_year['font_size']))
    pdf.set_font_size(place_and_year['font_size'])
    pdf.set_text_color(0, 0, 0) # black

    if English_flag:
        place_year_string="Stockholm, Sweden {}".format(year)
    else:
        place_year_string="Stockholm, Sverige {}".format(year)
    pdf.text(place_and_year['x_offset'], paperheight - place_and_year['y_offset'] + 6.30, place_year_string) 

    pdf.set_font_size(subject_area['font_size'])
    pdf.set_text_color(0, 0, 0) # black
    subject_string="Degree Project in Technology"
    subject_area_y=paperheight - subject_area['y_offset'] + (12.0 - 2.52)
    pdf.text(subject_area['x_offset'], subject_area_y, subject_string) 

    pdf.set_font_size(level_credits['font_size'])
    pdf.set_text_color(0, 0, 0) # black
    level_string="First cycle"
    number_of_credits="15"
    if English_flag:
        level_credits_string="{0}, {1} credits".format(level_string, number_of_credits)
    else:
        level_credits_string="{0}, {1} hp".format(level_string, number_of_credits)

    level_credits_y=subject_area_y + (1.08*12.0 + 6 + 3)
    pdf.text(level_credits['x_offset'], level_credits_y, level_credits_string) 

    # arialbd.ttf
    if title_field['font_face'] == "bold":
        pdf.add_font("Arial", 'B', '/usr/share/fonts/truetype/arialbd.ttf', uni=True) 
    else:
        pdf.add_font("Arial", 'B', '/usr/share/fonts/truetype/arial.ttf', uni=True) 
    pdf.set_font("Arial", size=int(title_field['font_size']))
    pdf.set_font_size(title_field['font_size'])
    pdf.set_text_color(0, 0, 0) # black
    title_y=level_credits_y + 2.5*title_field['font_size'] #
    if d['Title']:
        main_title=d['Title'].get('Main title', None)
        if main_title:
            title_string="{0}".format(main_title)
            subtitle=d['Title'].get('Subtitle', None)
            if subtitle:
                subtitle_string=subtitle
            else:
                subtitle_string=None
        else:
            print("No Main Title found")

    filled_text_strings=filled_text_string(pdf, title_string, title_field['font_size'], title_field['x_offset'], paperwidth)
    print("len(filled_text_strings)={0}, filled_text_strings={1}".format(len(filled_text_strings), filled_text_strings))
    title_y=title_y+title_field['font_size']+6.0
    for text_string in filled_text_strings:
        if len(text_string) > 0:
            title_y=title_y+(1.08*title_field['font_size'])
            pdf.text(title_field['x_offset'], title_y, text_string) 


    if subtitle_string:
        pdf.add_font("Arial", '', '/usr/share/fonts/truetype/arial.ttf', uni=True) 
        pdf.set_font("Arial", size=int(subtitle_field['font_size']))
        pdf.set_font_size(subtitle_field['font_size'])
        pdf.set_text_color(0, 0, 0) # black
        subtitle_y=title_y + 1.8*subtitle_field['font_size'] #
        pdf.text(subtitle_field['x_offset'], subtitle_y, subtitle_string) 

    pdf.add_font("Arial", '', '/usr/share/fonts/truetype/arial.ttf', uni=True) 
    pdf.set_font("Arial", size=int(authors_field['font_size']))
    pdf.set_font_size(authors_field['font_size'])
    pdf.set_text_color(0, 0, 0) # black
    if subtitle_string:
        authors_y=subtitle_y + 3.5*authors_field['font_size'] #
    else:
        authors_y=title_y + 3.5*authors_field['font_size'] #
    if d['Author1']:
        author_name=get_author_name(d['Author1'])
        pdf.text(authors_field['x_offset'], authors_y, author_name) 

    if d['Author2']:
        author_name=get_author_name(d['Author2'])
        authors_y=authors_y + 1.08*authors_field['font_size']
        pdf.text(authors_field['x_offset'], authors_y, author_name) 

    pdf.output(filename)

    return

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))


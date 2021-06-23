#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- mode: python; python-indent-offset: 4 -*-
#
# ./extract_pseudo_JSON-from_PDF.py
#
# Purpose: Extract data from the end of a PDF file that has been put out by my LaTeX template for use when inserting a thesis into DiVA.
#
# Example:
# ./extract_pseudo_JSON-from_PDF.py --pdf test5.pdf
# default output file is calendar_event.json
#
# ./extract_pseudo_JSON-from_PDF.py --pdf test5.pdf --json event.json
##
# 2021-04-22 G. Q. Maguire Jr.
#
import re
import sys

import json
import argparse
import os			# to make OS calls, here to get time zone info

from io import StringIO

from pdfminer.converter import TextConverter, HTMLConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser

from pdfminer.high_level import extract_pages
from io import BytesIO

def remove_comment_to_EOL(s):
    global Verbose_Flag
    offset=s.find('%')
    while (offset) >= 0:
        if (offset == 0) or (s[offset-1] != '\\'):
            # remove to EOL
            EOL_offset=s.find('\n', offset)
            if EOL_offset > 0:
                if (offset == 0):
                    s=s[EOL_offset+1:]
                else:
                    s=s[0:offset] + '\n' +s[EOL_offset+1:]
        offset=s.find('%', offset)
    return s



def replace_latex_symbol(s, symbol, insert_symbol):
    global Verbose_Flag
    cmd_offset=s.find(symbol)
    while (cmd_offset) > 0:
        s1=s[:cmd_offset]
        s2=s[cmd_offset+len(symbol):]
        s=s1+insert_symbol+s2
        cmd_offset=s.find(symbol, cmd_offset)
    return s


# usage: replace_latex_command(s1, '\\textit{', '<i>', '</i>')
def replace_latex_command(s, command, insert_at_start, insert_at_end):
    global Verbose_Flag
    cmd_offset=s.find(command)
    while (cmd_offset) > 0:
        s1=s[:cmd_offset]
        end_offset=s.find('}', cmd_offset+len(command))
        s2=s[cmd_offset+len(command):end_offset]
        s3=s[end_offset+1:]
        s=s1+insert_at_start+s2+insert_at_end+s3
        cmd_offset=s.find(command, cmd_offset)
    return s

# \textregistered
# \textcopyright
# \texttrademark
def clean_up_abstract(s):
    #print("in clean_up_abstract abstract={}".format(s))
    if s[0] == '\n':
        s=s[1:]
    s=remove_comment_to_EOL(s)
    s='<p>'+s+'</p>'
    #s=s.replace('<span style="font-family: TeXGyreHeros-Bold; font-size:5px">', '<span style="font-weight:bold">')
    #s=s.replace('<span style="font-family: TeXGyreHeros-Italic; font-size:5px">', '<span style="font-style:italic">')
    #s=s.replace('<span style="font-family: TeXGyreHeros-Regular; font-size:5px">', '<span>')
    #s=s.replace('<span style="font-family: TeXGyreCursor-Regular; font-size:5px">', '<span>')
    s=s.replace('\x0c', '')
    s=s.replace('\n\n', '</p><p>')
    s=s.replace('\\&', '&amp;')
    s=s.replace('\\linebreak[4]', '')
    s=replace_latex_command(s, '\\textit{', '<i>', '</i>')
    s=replace_latex_command(s, '\\textbf{', '<bold>', '</bold>')
    s=replace_latex_command(s, '\\texttt{', '<tt>', '</tt>')
    s=replace_latex_command(s, '\\textsubscript{', '<sub>', '</sub>')
    s=replace_latex_command(s, '\\textsuperscript{', '<sup>', '</sup>')
    s=replace_latex_symbol(s, '\\textregistered', '&reg;')
    s=replace_latex_symbol(s, '\\texttrademark', '&trade;')
    s=replace_latex_symbol(s, '\\textcopyright', '&copy;')
    s=s.replace('\\begin{itemize}</p><p>\\item', '</p><ul><li>')
    s=s.replace('\\item', '</li><li>')
    s=s.replace('</p><p>\\end{itemize}</p>', '</li></ul>')
    s=s.replace('\\end{itemize}', '</li></ul>')
    s=s.replace('\\begin{enumerate}</p><p>\\item', '</p><ul><li>')
    s=s.replace('</p><p>\\end{enumerate}</p>', '</li></ul>')
    s=s.replace('\n', ' ')
    # handle defines.tex macros
    s=s.replace('\\eg', 'e.g.')
    s=s.replace('\\Eg', 'E.g.')
    s=s.replace('\\ie', 'i.e.')
    s=s.replace('\\Ie', 'I.e.')
    s=s.replace('\\etc', 'etc.')
    s=s.replace('\\etal', 'et al.')
    s=s.replace('\\first', '(i) ')
    s=s.replace('\\second', '(ii) ')
    s=s.replace('\\third', '(iii) ')
    s=s.replace('\\forth', '(iv) ')
    s=s.replace('\\fifth', '(v) ')
    s=s.replace('\\sizth', '(vi) ')
    s=s.replace('\\seventh', '(vii) ')
    s=s.replace('\\eighth', '(viii) ')
    #
    trailing_empty_paragraph='<p> </p>'
    if s.endswith(trailing_empty_paragraph):
        s=s[:-len(trailing_empty_paragraph)]
    trailing_empty_paragraph='<p></p>'
    if s.endswith(trailing_empty_paragraph):
        s=s[:-len(trailing_empty_paragraph)]
    return s


def check_for_acronyms(a):
    if (a.find('\\gls{') >= 0) or (a.find('\\glspl{') >= 0) or \
       (a.find('\\Gls{') >= 0) or (a.find('\\Glspl{') >= 0) or \
       (a.find('\\acrlong{') >= 0) or (a.find('\\acrshort{') >= 0) \
       or (a.find('\\acrfull{') >= 0):
        return True
    return False

def get_acronyms(acronyms_filename):
    acronym_dict=dict()
    #
    newacronym_pattern='newacronym{'
    acronym_separator='}{'
    trailing_marker='}'
    #
    with open(acronyms_filename, 'r', encoding='utf-8') as input_FH:
        for line in input_FH:
            offset=line.find(newacronym_pattern)
            if offset < 0:
                continue
            # process an acronym definition
            l1=line[offset+len(newacronym_pattern):]
            # look for first part
            offset1=l1.find(acronym_separator)
            if offset1 < 0:
                print("Error in parsing line: {}".format(line))
                continue
            # extract label (first part of definition)
            label=l1[:offset1]
            # look for acronyms (second part of definition)
            remaining_str=l1[offset1+len(acronym_separator):]
            offset2=remaining_str.find(acronym_separator)
            if offset2 < 0:
                print("Error in parsing line: {}".format(line))
                continue
            # extract second part
            acronym=remaining_str[:offset2]
            # look for thirs part
            remaining_str=remaining_str[offset2+len(acronym_separator):]
            offset3=remaining_str.find(trailing_marker)
            if offset3 < 0:
                print("Error in parsing line: {}".format(line))
                continue
            # extract third part (phrase)
            phrase=remaining_str[:offset3]
            #
            acronym_dict[label]={'acronym': acronym, 'phrase': phrase}
    #
    return acronym_dict

def replace_first_gls(a, offset, acronym_dict):
    global spelled_out
    a_prefix=a[:offset]
    end_of_acronym=a.find('}', offset+5)
    if end_of_acronym < 0:
        print("could not find end of acronym label")
        return a
    label=a[offset+5:end_of_acronym]
    a_postfix=a[end_of_acronym+1:]
    ad=acronym_dict.get(label, None)
    if ad:
        phrase=ad.get('phrase', None)
        acronym=ad.get('acronym', None)
        already_spelled_out=spelled_out.get(label, None)
        if already_spelled_out:
            if acronym:
                a=a_prefix+acronym+a_postfix
            else:
                print("acronym missing for label={}".format(label))
        else:
            if phrase and acronym:
                full_phrase="{0} ({1})".format(phrase, acronym)
                a=a_prefix+full_phrase+a_postfix
                spelled_out[label]=True
            else:
                print("phrase or acronym are missing for label={}".format(label))
    else:
        print("Missing acronym for {}".format(label))
        return None
    #
    return a

def replace_first_glspl(a, offset, acronym_dict):
    global spelled_out
    a_prefix=a[:offset]
    end_of_acronym=a.find('}', offset+7)
    if end_of_acronym < 0:
        print("could not find end of acronym label")
        return a
    label=a[offset+7:end_of_acronym]
    a_postfix=a[end_of_acronym+1:]
    ad=acronym_dict.get(label, None)
    if ad:
        phrase=ad.get('phrase', None)
        acronym=ad.get('acronym', None)
        already_spelled_out=spelled_out.get(label, None)
        if already_spelled_out:
            if acronym:
                a=a_prefix+acronym+a_postfix
            else:
                print("acronym missing for label={}".format(label))
        else:
            if phrase and acronym:
                full_phrase="{0} ({1})".format(phrase, acronym)
                a=a_prefix+full_phrase+a_postfix
                spelled_out[label]=True
            else:
                print("phrase or acronym are missing for label={}".format(label))
    else:
        print("Missing acronym for {}".format(label))
        return None
    #
    return a

def spellout_acronyms_in_abstract(acronym_dict, a):
    # look for use of acronyms (i.e., a reference to an acronym's label) and spell out as needed
    # keep list of labels of acronyms found and spellout out
    global spelled_out
    spelled_out=dict()
    # Note that because we initialize it for each call of this routine, the acronyms will be spellout appropriately in each abstract
    #
    # first handle all cases where the full version is to be included
    acrfull_template='\\acrfull{'
    acrfull_offset=a.find(acrfull_template)
    while acrfull_offset >= 0:
        a_prefix=a[:acrfull_offset]
        end_of_acronym=a.find('}', acrfull_offset+len(acrfull_template))
        if end_of_acronym < 0:
            print("could not find end of acronym label")
            break
        label=a[acrfull_offset+len(acrfull_template):end_of_acronym]
        a_postfix=a[end_of_acronym+1:]
        ad=acronym_dict.get(label, None)
        if ad:
            phrase=ad.get('phrase', None)
            acronym=ad.get('acronym', None)
            if phrase and acronym:
                full_phrase="{0} ({1})".format(phrase, acronym)
                a=a_prefix+full_phrase+a_postfix
                spelled_out[label]=True
            else:
                print("phrase or acronym are missing for label={}".format(label))
            #
            acrfull_offset=a.find(acrfull_template, end_of_acronym)
    #
    # second handle all cases where the long version is to be included
    acrlong_template='\\acrlong{'
    acrlong_offset=a.find(acrlong_template)
    while acrlong_offset >= 0:
        a_prefix=a[:acrlong_offset]
        end_of_acronym=a.find('}', acrlong_offset+len(acrlong_template))
        if end_of_acronym < 0:
            print("could not find end of acronym label")
            break
        label=a[acrlong_offset+len(acrlong_template):end_of_acronym]
        a_postfix=a[end_of_acronym+1:]
        ad=acronym_dict.get(label, None)
        if ad:
            phrase=ad.get('phrase', None)
            if phrase:
                a=a_prefix+phrase+a_postfix
            else:
                print("phrase or acronym are missing for label={}".format(label))
            #
            acrlong_offset=a.find(acrlong_template, end_of_acronym)
    #
    #
    # third handle all cases where the long version is to be included
    acrshort_template='\\acrshort{'
    acrshort_offset=a.find(acrshort_template)
    while acrshort_offset >= 0:
        a_prefix=a[:acrshort_offset]
        end_of_acronym=a.find('}', acrshort_offset+len(acrshort_template))
        if end_of_acronym < 0:
            print("could not find end of acronym label")
            break
        label=a[acrshort_offset+len(acrshort_template):end_of_acronym]
        a_postfix=a[end_of_acronym+1:]
        ad=acronym_dict.get(label, None)
        if ad:
            acronym=ad.get('acronym', None)
            if acronym:
                a=a_prefix+acronym+a_postfix
            else:
                print("phrase or acronym are missing for label={}".format(label))
            #
            acrshort_offset=a.find(acrshort_template, end_of_acronym)
    #
    # handle cases where the acronym is conditionally spelled out and introduced or only the acronym is inserted
    # gls_offset=a.find('\\gls{')
    # lspl_offset=a.find('\\glspl{')
    # ggls_offset=a.find('\\Gls{')
    # gglspl_offset=a.find('\\Glspl{')
    # 
    s1=re.search('\\\\gls\{', a, re.IGNORECASE)
    s2=re.search('\\\\glspl\{', a, re.IGNORECASE)
    # find the earliest one
    while s1 or s2:
        if s1 and s2:
            gls_offset=s1.span()[0]
            glspl_offset=s2.span()[0]
            if  gls_offset < glspl_offset:
                # gls case occurs first
                a1=replace_first_gls(a, gls_offset, acronym_dict)
                if a1:
                    a=a1
                else:           # if the replacement failed, bail out
                    return a
            else:
                a=replace_first_glspl(a, glspl_offset, acronym_dict)
        elif s1 and not s2:
            gls_offset=s1.span()[0]
            a1=replace_first_gls(a, gls_offset, acronym_dict)
            if a1:
                a=a1
            else:
                return a
        else: # case of no s1 and s2:
            glspl_offset=s2.span()[0]
            a1=replace_first_glspl(a, glspl_offset, acronym_dict)
            if a1:
                a=a1
            else:
                return a
        s1=re.search('\\\\gls\{', a, re.IGNORECASE)
        s2=re.search('\\\\glspl\{', a, re.IGNORECASE)
    return a

def main(argv):
    global Verbose_Flag
    global Use_local_time_for_output_flag
    global testing

    argp = argparse.ArgumentParser(description="extract_pseudo_JSON-from_PDF.py: Extract the pseudo JSON from the end of the thesis PDF file")

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
                      default="calendar_event.json",
                      help="JSON file for extracted calendar event"
                      )

    argp.add_argument('-a', '--acronyms',
                      type=str,
                      default="acronyms.tex",
                      help="acronyms filename"
                      )



    args = vars(argp.parse_args(argv))

    Verbose_Flag=args["verbose"]

    filename=args["pdf"]
    if Verbose_Flag:
        print("filename={}".format(filename))

    #output_string = StringIO()
    output_string = BytesIO()
    with open(filename, 'rb') as in_file:
        parser = PDFParser(in_file)
        doc = PDFDocument(parser)
        rsrcmgr = PDFResourceManager()
        device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
        #device = HTMLConverter(rsrcmgr, output_string, laparams=LAParams(), layoutmode='normal', codec='utf-8')

        interpreter = PDFPageInterpreter(rsrcmgr, device)
        for page in PDFPage.create_pages(doc):
            interpreter.process_page(page)

        text=output_string.getvalue().decode('UTF-8')
        if Verbose_Flag:
            print(text)

    diva_start=text.find("For DIVA")
    if diva_start > 0:
        diva_data=text[:]
        diva_data=diva_data[diva_start:]
        diva_start=diva_data.find("{")
        if diva_start >= 0:
            diva_data=diva_data[diva_start:]
            end_block=diva_data.find('”Number of lang instances”:') # note these are right double quote marks
            if end_block > 0:
                end_block=diva_data.find(',', end_block)
                if end_block > 0:
                    dict_string=diva_data[:]
                    dict_string=dict_string[:end_block]+'}'

                    dict_string=dict_string.replace('”', '"')
                    #dict_string=dict_string.replace('&quot;', '"')
                    #dict_string=dict_string.replace('<br>', '\n')
                    #dict_string=dict_string.replace('<br>"', '\n"')
                    #dict_string=dict_string.replace('<br>}', '\n}')
                    dict_string=dict_string.replace(',\n\n}', '\n}')
                    dict_string=dict_string.replace(',\n}', '\n}')
                    print("dict_string={}".format(dict_string))
                    d=json.loads(dict_string)
                    print("d={}".format(d))

                    abs_keywords=diva_data[(end_block+1):]
                    if Verbose_Flag:
                        print("abs_keywords={}".format(abs_keywords))
                    quad__euro_marker='€€€€'
                    number_of_quad_euros=abs_keywords.count(quad__euro_marker)
                    if Verbose_Flag:
                        print("number_of_quad_euros={}".format(number_of_quad_euros))
                    abstracts=dict()
                    keywords=dict()
                    if (number_of_quad_euros % 2) == 1:
                        print("Odd number of markers")

                    save_abs_keywords=abs_keywords[:]

                    number_of_pairs_of_markers=int(number_of_quad_euros/2)
                    for i in range(0, number_of_pairs_of_markers):
                        abstract_key_prefix='”Abstract['
                        key_offset=abs_keywords.find(abstract_key_prefix)
                        if key_offset > 0:
                            # found a key for an abstract
                            # get language code
                            lang_code_start=key_offset+len(abstract_key_prefix)
                            lang_code=abs_keywords[lang_code_start:lang_code_start+3]
                            quad__euro_marker_start=abs_keywords.find(quad__euro_marker, lang_code_start)
                            if quad__euro_marker_start >= 0:
                                quad__euro_marker_end=abs_keywords.find(quad__euro_marker, quad__euro_marker_start + 5)
                                abstracts[lang_code]=abs_keywords[quad__euro_marker_start+5:quad__euro_marker_end]
                                #br_offset=abstracts[lang_code].find('<br>')
                                #if br_offset >= 0:
                                #    abstracts[lang_code]=abstracts[lang_code][br_offset+4:]

                                abs_keywords=abs_keywords[quad__euro_marker_end+1:]
                        

                    abs_keywords=save_abs_keywords[:]

                    for i in range(0, number_of_pairs_of_markers):
                        abstract_key_prefix='”Keywords['
                        key_offset=abs_keywords.find(abstract_key_prefix)
                        if key_offset > 0:
                            # found a key for an abstract
                            # get language code
                            lang_code_start=key_offset+len(abstract_key_prefix)
                            lang_code=abs_keywords[lang_code_start:lang_code_start+3]
                            quad__euro_marker_start=abs_keywords.find(quad__euro_marker, lang_code_start)
                            if quad__euro_marker_start > 0:
                                quad__euro_marker_end=abs_keywords.find(quad__euro_marker, quad__euro_marker_start + 5)
                                keywords[lang_code]=abs_keywords[quad__euro_marker_start+5:quad__euro_marker_end]
                                br_offset=keywords[lang_code].find('<br>')
                                if br_offset >= 0:
                                    keywords[lang_code]=keywords[lang_code][br_offset+4:]
                                abs_keywords=abs_keywords[quad__euro_marker_end+1:]
                        

                    for a in abstracts:
                        abstracts[a]=clean_up_abstract(abstracts[a])

                    any_acronyms_in_abstracts=False
                    for a in abstracts:
                        acronyms_present=check_for_acronyms(abstracts[a])
                        if acronyms_present:
                            any_acronyms_in_abstracts=True

                    if any_acronyms_in_abstracts:
                        acronyms_filename=args["acronyms"]
                        print("Acronyms found, getting acronyms from {}".format(acronyms_filename))
                        acronym_dict=get_acronyms(acronyms_filename)
                        if len(acronym_dict) == 0:
                            print("no acronyms found in {}".format(acronyms_filename))
                        else:
                            # entries of the form: acronym_dict[label]={'acronym': acronym, 'phrase': phrase}
                            for a in abstracts:
                                abstracts[a]=spellout_acronyms_in_abstract(acronym_dict, abstracts[a])


                    print("abstracts={}".format(abstracts))
                    print("keywords={}".format(keywords))

                    d['abstracts']=abstracts
                    d['keywords']=keywords
                    output_filename=args["json"]
                    if Verbose_Flag:
                        print("output_filename={}".format(output_filename))
                    with open(output_filename, 'w', encoding='utf-8') as output_FH:
                        j_as_string = json.dumps(d, ensure_ascii=False)
                        print(j_as_string, file=output_FH)



if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))


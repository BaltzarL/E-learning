#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- mode: python; python-indent-offset: 4 -*-
#
# ./cleanup_pseudo_JSON-from_LaTeX.py --json fordiva.json [--acronyms acronyms.tex]
#
# Purpose: Extract data from the pseudo JSON file that has been produced by my LaTeX template and cleanit up, so that it can be used with my other program (to create claendar entries, MODS file, and insert titles into LADOK).
#
# Outputs a new cleaned up JSON file in a file with the name augmented by "-cleaned"
# Example:
# ./cleanup_pseudo_JSON-from_LaTeX.py --json fordiva.json [--acronyms acronyms.tex]
# 
# Based upon earlier extract_pseudo_JSON-from_PDF.py
#
# 2021-07-29 G. Q. Maguire Jr.

#
import re
import sys

import json
import argparse
import os			# to make OS calls, here to get time zone info
import pprint


def remove_comment_to_EOL(s):
    global Verbose_Flag
    if Verbose_Flag:
        print("remove_comment_to_EOL(s): s={0}".format(s))
    offset=s.find('%')
    if Verbose_Flag:
        print("offset={0}".format(offset))
    while (offset) >= 0:
        if Verbose_Flag:
            print("offset={0}".format(offset))
        if (offset == 0) or (s[offset-1] != '\\'):
            # remove to EOL
            EOL_offset=s.find('\n', offset)
            if EOL_offset > 0:
                if (offset == 0):
                    s=s[EOL_offset+1:]
                else:
                    s=s[0:offset] + '\n' +s[EOL_offset+1:]
        offset=offset+1
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
    # the next has already been done
    #s=remove_comment_to_EOL(s)

    s='<p>'+s+'</p>'
    #s=s.replace('\x0c', '')  # Unsure if this is necessary

    s=s.replace('\u2029', '</p><p>')
    s=s.replace('\u2028', '<BR>')
    s=s.replace('\\\\', '\\')

    s=s.replace('\&', '&amp;')
    s=s.replace('\\,', '\u202F')     # should insert a non-breaking space
    s=s.replace('\\linebreak[4]', ' ')
    s=replace_latex_command(s, '\\textit{', '<i>', '</i>')
    s=replace_latex_command(s, '\\textbf{', '<strong>', '</strong>')
    s=replace_latex_command(s, '\\texttt{', '<tt>', '</tt>')
    s=replace_latex_command(s, '\\textsubscript{', '<sub>', '</sub>')
    s=replace_latex_command(s, '\\textsuperscript{', '<sup>', '</sup>')
    s=replace_latex_symbol(s, '\\ldots', ' ... ')
    s=replace_latex_symbol(s, '\\textregistered', '&reg;')
    s=replace_latex_symbol(s, '\\texttrademark', '&trade;')
    s=replace_latex_symbol(s, '\\textcopyright', '&copy;')

    s=s.replace('\\begin{itemize}<BR>', '</p><p><ul>')
    s=s.replace('\\item', '<li>')
    s=s.replace('\\end{itemize}', '</li></ul></p><p>')
    s=s.replace('<li> ', '<li>')
    s=s.replace(' <li>', '<li>')
    s=s.replace(' <li>', '<li>')
    s=s.replace('\\begin{enumerate}', '</p><p><ol><li>')
    s=s.replace('\\end{enumerate}', '</li></ol></p><p>')


    s=s.replace('<BR></p>', '</p>')
    s=s.replace('<BR></li>', '</li>')
    s=s.replace('<BR><li>', '</li><li>')


    # s=s.replace('\\begin{itemize}</p><p>\\item', '</p><ul><li>')
    # s=s.replace('\\item', '</li><li>')
    # s=s.replace('</p><p>\\end{itemize}</p>', '</li></ul>')
    # s=s.replace('\\end{itemize}', '</li></ul>')
    # s=s.replace('\\begin{enumerate}</p><p>\\item', '</p><ul><li>')
    #s=s.replace('</p><p>\\end{enumerate}</p>', '</li></ul>')
    s=s.replace('\n', ' ')

    # handle defines.tex macros
    s=s.replace('\\eg', 'e.g.')
    s=s.replace('\\Eg', 'E.g.')
    s=s.replace('\\ie', 'i.e.')
    s=s.replace('\\Ie', 'I.e.')
    s=s.replace('\\etc', 'etc.')
    s=s.replace('\\etal', 'et al.')
    s=s.replace('\\first', '(i) ')
    s=s.replace('\\Second', '(ii) ')
    s=s.replace('\\third', '(iii) ')
    s=s.replace('\\fourth', '(iv) ')
    s=s.replace('\\fifth', '(v) ')
    s=s.replace('\\sixth', '(vi) ')
    s=s.replace('\\seventh', '(vii) ')
    s=s.replace('\\eighth', '(viii) ')
    # handle some units
    s=s.replace('{\\meter\\squared}', '\u202Fm<sup>2</sup>')
    s=s.replace('{\\meter\\per\\second}', '\u202Fm\u202Fs<sup>-1</sup>')
    s=s.replace('{\\second}', '\u202Fs')
    s=s.replace('{\\meter}', '\u202Fm')
    s=s.replace('{\\percent}', '\u202F\\%')
    s=replace_latex_command(s, '\\num{', '', '')
    s=replace_latex_command(s, '\\SI{', '', '')
    #
    trailing_empty_paragraph='<p> </p>'
    if s.endswith(trailing_empty_paragraph):
        s=s[:-len(trailing_empty_paragraph)]
    trailing_empty_paragraph='<p></p>'
    if s.endswith(trailing_empty_paragraph):
        s=s[:-len(trailing_empty_paragraph)]


    s=s.replace('<p></p>', '')      # remove empty paragraphs
    s=s.replace('<li></li>', '')    # remove empty list items
    s=s.replace('\\textbackslash ', '\\')
    return s


def check_for_acronyms(a):
    if (a.find('\\gls{') >= 0) or (a.find('\\glspl{') >= 0) or \
       (a.find('\\Gls{') >= 0) or (a.find('\\Glspl{') >= 0) or \
       (a.find('\\acrlong{') >= 0) or (a.find('\\acrshort{') >= 0) or \
       (a.find('\\glsentrylong') >= 0) or (a.find('\\glsentryshort{') >= 0) or (a.find('\\glsentryfull{') >= 0) or \
       (a.find('\\acrfull{') >= 0):
        return True
    return False

def get_acronyms(acronyms_filename):
    acronym_dict=dict()
    #
    newacronym_pattern='newacronym'
    trailing_marker='}'
    start_option_marker='['
    end_option_marker=']'
    #
    with open(acronyms_filename, 'r', encoding='utf-8') as input_FH:
        for line in input_FH:
            line=line.strip()   # remove leading and trailing white space
            comment_offset=line.find('%')
            if comment_offset == 1: #  of a comment line, simply skip the line
                continue
            offset=line.find(newacronym_pattern)
            if offset < 1:
                continue
            offset_s=line.find(start_option_marker)
            offset_e=line.find(end_option_marker)
            if offset_s > 0 and offset_e > 0: 		# remove options to \newacronym[options]{}{}{}
                line=line[0:offset_s]+line[offset_e+1:]
            # process an acronym definition
            parts=line.split('{')
            label=None
            acronym=None
            phrase=None
            for i, value in enumerate(parts):
                if i == 0:
                    continue
                elif i == 1: #  get label
                    label=value.strip()
                    if label.endswith(trailing_marker):
                        label=label[:-1]
                    else:
                        print("Error in parsing for label in line: {}".format(line))
                        continue
                elif i == 2: # get acronym
                    acronym=value.strip()
                    if acronym.endswith(trailing_marker):
                        acronym=acronym[:-1]
                    else:
                        print("Error in parsing for acronym in line: {}".format(line))
                        continue
                elif i == 3: # get phrase
                    phrase=value.strip()
                    if phrase.endswith(trailing_marker):
                        phrase=phrase[:-1]
                    else:
                        print("Error in parsing for phrase in line: {}".format(line))
                        continue
                else:
                    print("Error in parsing in line: {}".format(line))
                    continue
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
    for template in ['\\acrfull{', '\\glsentryfull{']:
        offset=a.find(template)
        while offset >= 0:
            a_prefix=a[:offset]
            end_of_acronym=a.find('}', offset+len(template))
            if end_of_acronym < 0:
                print("could not find end of acronym label")
                break
            label=a[offset+len(template):end_of_acronym]
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
            offset=a.find(template, end_of_acronym)
    #
    # second handle all cases where the long version is to be included
    for template in ['\\acrlong{', '\\glsentrylong{']:
        offset=a.find(template)
        while offset >= 0:
            a_prefix=a[:offset]
            end_of_acronym=a.find('}', offset+len(template))
            if end_of_acronym < 0:
                print("could not find end of acronym label")
                break
            label=a[offset+len(template):end_of_acronym]
            a_postfix=a[end_of_acronym+1:]
            ad=acronym_dict.get(label, None)
            if ad:
                phrase=ad.get('phrase', None)
                if phrase:
                    a=a_prefix+phrase+a_postfix
                else:
                    print("phrase or acronym are missing for label={}".format(label))
            #
            offset=a.find(template, end_of_acronym)
    #
    #
    # third handle all cases where the long version is to be included
    for template in ['\\acrshort{', '\\glsentryshort{']:
        offset=a.find(template)
        while offset >= 0:
            a_prefix=a[:offset]
            end_of_acronym=a.find('}', offset+len(template))
            if end_of_acronym < 0:
                print("could not find end of acronym label")
                break
            label=a[offset+len(template):end_of_acronym]
            a_postfix=a[end_of_acronym+1:]
            ad=acronym_dict.get(label, None)
            if ad:
                acronym=ad.get('acronym', None)
                if acronym:
                    a=a_prefix+acronym+a_postfix
                else:
                    print("phrase or acronym are missing for label={}".format(label))
            #
            offset=a.find(template, end_of_acronym)
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

# ligature. LaTeX commonly does it for ff, fi, fl, ffi, ffl, ...
ligrature_table= {'\ufb00': 'ff', # 'ﬀ'
                  '\ufb03': 'f‌f‌i', # 'ﬃ'
                  '\ufb04': 'ffl', # 'ﬄ'
                  '\ufb01': 'fi', # 'ﬁ'
                  '\ufb02': 'fl', # 'ﬂ'
                  '\ua732': 'AA', # 'Ꜳ'
                  '\ua733': 'aa', # 'ꜳ'
                  '\ua733': 'aa', # 'ꜳ'
                  '\u00c6': 'AE', # 'Æ'
                  '\u00e6': 'ae', # 'æ'
                  '\uab31': 'aə', # 'ꬱ'
                  '\ua734': 'AO', # 'Ꜵ'
                  '\ua735': 'ao', # 'ꜵ'
                  '\ua736': 'AU', # 'Ꜷ'
                  '\ua737': 'au', # 'ꜷ'
                  '\ua738': 'AV', # 'Ꜹ'
                  '\ua739': 'av', # 'ꜹ'
                  '\ua73a': 'AV', # 'Ꜻ'  - note the bar
                  '\ua73b': 'av', # 'ꜻ'  - note the bar
                  '\ua73c': 'AY', # 'Ꜽ'
                  '\ua76a': 'ET', # 'Ꝫ'
                  '\ua76b': 'et', # 'ꝫ'
                  '\uab41': 'əø', # 'ꭁ'
                  '\u01F6': 'Hv', # 'Ƕ'
                  '\u0195': 'hu', # 'ƕ'
                  '\u2114': 'lb', # '℔'
                  '\u1efa': 'IL', # 'Ỻ'
                  '\u0152': 'OE', # 'Œ'
                  '\u0153': 'oe', # 'œ'
                  '\ua74e': 'OO', # 'Ꝏ'
                  '\ua74f': 'oo', # 'ꝏ'
                  '\uab62': 'ɔe', # 'ꭢ'
                  '\u1e9e': 'fs', # 'ẞ'
                  '\u00df': 'fz', # 'ß'
                  '\ufb06': 'st', # 'ﬆ'
                  '\ufb05': 'ſt', # 'ﬅ'  -- long ST
                  '\ua728': 'Tz', # 'Ꜩ'
                  '\ua729': 'tz', # 'ꜩ'
                  '\u1d6b': 'ue', # 'ᵫ'
                  '\uab63': 'uo', # 'ꭣ'
                  #'\u0057': 'UU', # 'W'
                  #'\u0077': 'uu', # 'w'
                  '\ua760': 'VY', # 'Ꝡ'
                  '\ua761': 'vy', # 'ꝡ'
                  # 
                  '\u0238': 'db', # 'ȸ'
                  '\u02a3': 'dz', # 'ʣ'
                  '\u1b66': 'dʐ', # 'ꭦ'
                  '\u02a5': 'dʑ', # 'ʥ'
                  '\u02a4': 'dʒ', # 'ʤ'
                  '\u02a9': 'fŋ', # 'ʩ'
                  '\u02aa': 'ls', # 'ʪ'
                  '\u02ab': 'lz', # 'ʫ'
                  '\u026e': 'lʒ', # 'ɮ'
                  '\u0239': 'qp', # 'ȹ'
                  '\u02a8': 'tɕ', # 'ʨ'
                  '\u02a6': 'ts', # 'ʦ'
                  '\uab67': 'tʂ', # 'ꭧ'
                  '\u02a7': 'tʃ', # 'ʧ'
                  '\uab50': 'ui', # 'ꭐ'
                  '\uab51': 'ui', # 'ꭑ' -- turned ui
                  '\u026f': 'uu', # 'ɯ'
                  # digraphs with single code points
                  '\u01f1': 'DZ', # 'Ǳ'
                  '\u01f2': 'Dz', # 'ǲ'
                  '\u01f3': 'dz', # 'ǳ'
                  '\u01c4': 'DŽ', # 'Ǆ'
                  '\u01c5': 'Dž', # 'ǅ'
                  '\u01c6': 'dž', # 'ǆ'
                  '\u0132': 'IJ', # 'Ĳ'
                  '\u0133': 'ij', # 'ĳ'
                  '\u01c7': 'LJ', # 'Ǉ'
                  '\u01c8': 'Lj', # 'ǈ'
                  '\u01c9': 'lj', # 'ǉ'
                  '\u01ca': 'NJ', # 'Ǌ'
                  '\u01cb': 'Nj', # 'ǋ'
                  '\u01cc': 'nj', # 'ǌ'
                  '\u1d7a': 'th', # 'ᵺ'
                  }

def replace_ligature(s):
    # check for ligratures and replace them with separate characters
    if not s:
        return s
    
    for l in ligrature_table:
        if s.find(l) >= 0:
            print("found ligrature {0} replacing with {1}".format(l, ligrature_table[l]))  
            s=s.replace(l, ligrature_table[l])
    #
    return s


def process_in_quadeuros(s):
    s=remove_comment_to_EOL(s)
    s=s.replace('\n\n','\u2029') # replace two new lines with a unicode paragraph seperator
    s=s.replace('\n',  '\u2028') # replace single new lines with a unicode line seperator
    #s=s.replace('"\u2028,', '",') # replace single new lines with a unicode line seperator
    if s.endswith('\u2028'):
        s=s[:-1]
    # Just leave some characters for now - this part has to be written
    print("s={}".format(s))
    #return '"test string"'
    return s

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

    argp.add_argument('-j', '--json',
                      type=str,
                      default="fordiva.json",
                      help="JSON file for extracted calendar event"
                      )

    argp.add_argument('-a', '--acronyms',
                      type=str,
                      default="acronyms.tex",
                      help="acronyms filename"
                      )

    argp.add_argument('-l', '--ligatures',
                      default=False,
                      action="store_true",
                      help="leave ligatures rahter than replace them"
                      )



    args = vars(argp.parse_args(argv))

    Verbose_Flag=args["verbose"]

    pp = pprint.PrettyPrinter(indent=4, width=1024) # configure prettyprinter

    input_filename=args["json"]
    if Verbose_Flag:
        print("input_filename={}".format(input_filename))

    lines=''
    with open(input_filename, 'r') as in_file:
        for idx, line in enumerate(in_file):
            if Verbose_Flag:
                print(line)
            #remove trailing newlines
            # if line.endswith('\n'):
            #     line=line[:-1]
            if line.find('\\&') >= 0: # remove the \&
                print("line with & ={}".format(line))
                line=line.replace('\\&', '&amp;')

            if line.find('\\b') >= 0: # correct things that might have been treated improperly as a escaped character
                line=line.replace('\\b', '\\\\b')
            if line.find('\\e') >= 0:
                line=line.replace('\\e', '\\\\e')
            if line.find('\\f') >= 0:
                line=line.replace('\\f', '\\\\f')
            if line.find('\\i') >= 0:
                line=line.replace('\\i', '\\\\i')
            if line.find('\\l') >= 0:
                line=line.replace('\\l', '\\\\l')
            if line.find('\\n') >= 0:
                line=line.replace('\\n', '\\\\n')
            if line.find('\\r') >= 0:
                line=line.replace('\\r', '\\\\r')
            if line.find('\\t') >= 0:
                line=line.replace('\\t', '\\\\t')
            if line.find('\\x') >= 0:
                line=line.replace('\\t', '\\\\x')
            if line.find("\\'") >= 0:
                line=line.replace("\\'", "\\\\'")
            if line.find('\\') >= 0:
                line=line.replace('\\', '\\\\')
            if line.find('%^^Ascheol%') >= 0: # remove the special end of line marker
                line=line.replace('%^^Ascheol%', '')
            lines=lines+line

    ## here we need to cleanup the strings between the quad euro markers
    quad__euro_marker='€€€€'
    number_of_quad_euros=lines.count(quad__euro_marker)
    print("number_of_quad_euros={}".format(number_of_quad_euros))
    if (number_of_quad_euros % 2) == 1:
        print("Odd number of markers")
        return

    filtered_lines=list()
    number_of_pairs_of_markers=int(number_of_quad_euros/2)
    for i in range(0, number_of_pairs_of_markers):
        marker_offset=lines.find(quad__euro_marker)
        if marker_offset > 0:
            part=lines[0:marker_offset]
            filtered_lines.append(part)
            next_marker_offset=lines.find(quad__euro_marker, marker_offset+5)
            part_to_filter=lines[marker_offset+5:next_marker_offset]
            processed_text=process_in_quadeuros(part_to_filter)
            filtered_lines.append(processed_text)
            lines=lines[next_marker_offset+4:] #  leave the ","
            
    lines=''.join(filtered_lines)
    print("lines={}".format(lines))

    lines=lines.replace(',\n}', '}')
    lines=lines+'}}'
    print("lines={}".format(lines))
    try:
        if not args['ligatures']:
            lines=replace_ligature(lines)
            print("looking for and replacing ligatures")
            print("lines={}".format(lines))
        d=json.loads(lines)
    except:
        print("error in line (#{0}): {1}".format(idx, line))
        print("{}".format(sys.exc_info()))
        return


    print("end for testing")
    pp.pprint(d)
    
    abstracts=d.get('abstracts', None)
    if abstracts:
        for a in abstracts:
            print("a={0}, abstract={1}".format(a, abstracts[a]))
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

    keywords=d.get('keywords', None)
    if keywords:
        for a in keywords:
            keywords[a]=keywords[a].strip()
            print("a={0}, keywords={1}".format(a, keywords[a]))

    output_filename="{}-cleaned.json".format(input_filename[:-5])
    if Verbose_Flag:
        print("output_filename={}".format(output_filename))
    with open(output_filename, 'w', encoding='utf-8') as output_FH:
        j_as_string = json.dumps(d, ensure_ascii=False)
        print(j_as_string, file=output_FH)

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))


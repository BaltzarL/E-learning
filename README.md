# E-learning
This repository consists of tools for use with KTH's LMS and other systems to facilitate e-learning activities of faculty, students, and staff.

These tools are intended to be examples of how one can use the Canvas Restful API and to
provide some useful functionality (mainly for teachers).

Programs can be called with the option "-v" or "--verbose" you get lots of output - showing in detail the operations of the program.

Additionally, programs can be called with an alternative configuration file using the syntax: --config FILE

for example:  --config config-test.json

See the default-config.json file for an example of the structure of this file. Replace the string xxx by your access token and replace the string yyy.instructure.com with the name of the server where your Canvas LMS is running.

======================================================================
## setup-degree-project-course.py

Purpose: To setup a degree project course.

Input:
```
./setup-degree-project-course.py cycle_number course_id school_acronym
 cycle_number is either 1 or 2 (1st or 2nd cycle)

 "-m" or "--modules" set up the two basic modules (Gatekeeper module 1 and Gatekeeper protected module 1)
 "-p" or "--page" set up the two basic pages for the course
 "-s" or "--survey" set up the survey
 "-S" or "--sections" set up the sections for the examiners and programs
 "-c" or "--columns" set up the custom columns
 "-p" or "--pages" set up the pages
 "-a" or "--assignments" set up the assignments (proposal, alpha and beta drafts, etc.)

 "-A" or "--all" set everything up (sets all of the above options to true)

 with the option "-v" or "--verbose" you get lots of output - showing in detail the operations of the program
 Can also be called with an alternative configuration file:
     ./setup-degree-project-course.py --config config-test.json 1 12683
```

Output: outputs 

Note it is not designed to be run multipe times. If you want to run it again you need to delete the things (modules, assignments, and quiz) that were created.

Example:
```
Set up the modules:
./setup-degree-project-course.py --config config-test.json -m 1 12683

Set up the survey
./setup-degree-project-course.py --config config-test.json -s 1 12683 EECS

Set up sections for the examiners and programs
   ./setup-degree-project-course.py --config config-test.json -S 2 12683 EECS

   ./setup-degree-project-course.py --config config-test.json -S 2 12683 SCI

```

## yyy.py

Purpose: To 

Input:
```
./xxx.py KTHID_of_user
```

Output: outputs 

Note 

Example:
```
./xxx.py u1d13i2c
```

You can xxxx, for example:
```

```




# Editor for Reconciled NfN Transcripts  
A Python based GUI for easy editing of Zooniverse transcriptin reconciled using NfN reconcile.py

This script takes as inputs the reconciled-with-explanations and the flattened 
unreconciled .csv files as produced by Notes from Nature's reconcile.py.

The editing GUI itself is patterned after the NfN Summary html template - except the reconciled result is fully editable using cut, paste, and copy keyboard commands from any field shown in the editor, direct character entry, deletion or replacement in the reconciled text block, or by simply selecting the best version of the actual transcriptions entered by the volunteers.

# Installation
It is assumed that the user will have a working reconcile.py environment.  If that environment supports a version of reconciled.py that can produce the reconciled file with explanations then the entire directory NfN reconcile.py version 0.4.8 is not required.  Simply copy the two files:

````
nfn_editor.py
update driver.py
````

to your label_reconciliations directory or wherever you run reconciled.py from.

Then install the following packages to this environment:

````
selenium>=4.6  
webdriver-manager>=3.8.4  
panoptes_client>=1.5.0  
future==0.18.2
SQLAlchemy~=1.4.41
Pillow==9.3.0
````

If you are starting from scratch and need version 0.4.8 of reconcile.py, build a new environment as follows:

````
•	We require python 3.5 or later
•	git clone https https://github.com/PmasonFF/Reconcile-Editor
•	cd Reconcile-Editor
•	Optional: virtualenv venv -p python3
•	Optional: source venv/bin/activate
•	pip install -r requirements.txt
````

There may be easier ways to build the python environment such as using an IDE like Pycharm.  Alternately simply attempt to run the script and install each package reported as missing, referring to the individual package installation instructions as needed.  It is best the code runs in a virtual environment so future changes to the packages do not lead to incompatibilities (On the other hand there are some advantages to keeping your environment up-to-date and handling the issues if any as they arise.)  



# Description
This script takes as inputs the reconciled-with-explanations and the flattened unreconciled.csv files as produced by Notes from Nature's reconcile.py.

In lieu of the unreconciled Notes from Nature file generated using the -u parameter, this script can use **any** flattened .csv file with columns for subject_id, classification_id, and user_name plus additional columns that has been reconciled using reconcile.py (ie using the -f csv parameter with the reconciled columns defined using the -c parameters.)

For both NfN and .csv files the unreconciled and reconciled with explanations must be match - ie the reconciled file as generated from the unreconciled data.

The script builds a Sqlite database which can then be edited by selecting various problem types as normally presented in the Summary html format from reconcile.py.


# Setup and operation
In order to show the zooniverse subject for comparison to the transcribed data, the script opens a browser (independent of any other open browser on the system). To do this it needs a compatible browser installed on the system and a compatible webdriver installed in the current working directory.  There is a utility script update_drivers.py which will obtain and install up-to-date webdrivers for the supported browser types. **This should be run once before using this script** and again if updates to your browser cause it to throw an error when attempting to open the browser. **At this time Chrome, and Firefox for Mac or Windows, and Edge for Windows are supported.**

The next step is to ensure the reconciled data as produced by reconcile.py **with explanations** and the unreconciled data are in a directory together (not usually the directory with the script).  The path to this directory, the reconciled and unreconciled file names, a identifier for the reviewer, and the browser type to use are passed as parameters to the editor script.  Once the browser drivers are set we are ready to run the editor. The first step is to define the input files using these parameters, along with the browser that will be used to show the original subject. 

# Examples
You may get program help via:
./nfn_editor.py –help

````
NOTE: You may use a file to hold the
command-line arguments like: @/path/to/args.txt.

optional arguments:
  -h, --help            show this help message and exit
  -u USERNAME, --username USERNAME
                        An identifier for the reviewer making the changes. It
                        will be recorded with the modifications made. At this
                        time there is no verification or testing of
                        credentials.
  -d DIRECTORY, --directory DIRECTORY
                        The path and directory where the unreconciled file,
                        the reconciled file are located. The databases will
                        also be built there. example -d
                        C:\py_scripts\Scripts_Reconcile .
  -f FLATTENED, --flattened FLATTENED
                        The source file for the flattened unreconciled
                        classifications
  -r RECONCILED, --reconciled RECONCILED
                        The source file for the reconciled classifications
                        with explanations as produced by reconcile.py
                        --explanations.
  -p PROBLEM_LIST, --problem_list PROBLEM_LIST
                        A optional csv file with a column "subject_id"
                        containing a list of zooniverse subject numbers to
                        edit.
  -b BROWSER, --browser BROWSER
                        Specify the browser to be used to show the subjects.
                        This script supports Chrome, Edge, and Firefox
                        on recent Windows and Mac operating systems. Other
                        browsers can be used with a slight modification.
                        
````

A typical run will look like:
````
./ nfn_editor.py -d <path to working directory> -f unreconciled_nfn.csv -r reconciled_nfn.csv -u Pmason -b firefox
````

# Operation cont’d

On the first run, the script builds or locates a SQL database that is being or will be modified in the current working directory (where the script is being run from).  Using a SQL database provides much faster search and update. Once modified it is easy to convert back to .csv format, or integrate with other data formats such as Darwin Core. 

To select the problems to be corrected, a GUI is presented where the problem types for each reconciled field can be toggled on or off. Currently the problem types are limited to "No match, "One transcript", "Tie matches" (ie no clear majority), and 'Fuzzy" matches. Currently Exact unanimous and Exact or Normalized majority matches are not selectable in the GUI.

However it is also possible to define a problem listing in the parameters that overrides the GUI.  This listing can be any .csv formatted file with a column "subject_id" (note no "s") which holds a list of subjects to edit. It is important all the subjects listed appear in both the reconciled and unreconciled input files and still exist in zooniverse.

The subjects to be edited are retrieved from Zooniverse using the panoptes client, and shown in the browser under the editing GUI.

The editing GUI itself is patterned after the NfN Summary html template - except the reconciled result is fully editable using cut, paste, and copy keyboard commands from any field shown in the editor, direct character entry, deletion or replacement in the reconciled text block, or by simply selecting the best version of the actual transcriptions entered by the volunteers.

There is a button to Restore the reconciled results back to the what they were the last time they were modified and submitted (which may be their original version if no changes have be Submitted).  There is another button to Submit the changes made and move on to the next subject, and finally a button to Submit the changes for the current subject and exit.  The Submit button makes the pending changes permanently in the database. Changes in the database carry a "Modified" flag and a date, time and the id of the reviewer that made the change in place of the reconciled explanation.


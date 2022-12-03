## Demo for Reconcile-Editor

This directory contains various files that can be used to explore and test the reconcile-editor. NOTE these files have not yet been uploaded as of 12-03.

#### Raw data export
There is a sample sample data export as downloaded from zooniverse:

1) digging-up-the-oceans-past-classifications.csv  This is a pure transcription workflow using several combo tasks with multiple short transcription tasks in each. It was generated as a pre-beta test for a project digging up the oceans' past (https://www.zooniverse.org/projects/geosar/digging-up-the-oceans-past) which is part of an effort undertaken within the EMODnet Biology project and the Work Package 2 through which rescuing historical biodiversity data is one of the goals:
It is used with thanks! 
 EMODnet Biology project (https://www.emodnet-biology.eu/) 
 Work Package 2 (https://www.emodnet-biology.eu/WP2_Access_to_marine_biological_data
 World Register of Marine Species (https://www.marinespecies.org/)
 MedOBIS repository (http://ipt.medobis.eu/)
 
 #### Flattened classifications and script
For this data export there is a Python script that was used to flatten the export, and the resulting flattened .csv file.  There are several advantages to flattening the data with a script
- The export can be cleaned to include only valid classifications, cutting off development and previous incompatible workflow versions.
- The column headers can be simplified and ordered while for the reconciliation of the raw export the order is defined by the task numbering and the headers come from the zooniverse task label which can be cumbersome:
- The data can be preprocessed if required. 

In this case there is only some cleanup of older workflow versions, and simple column headers:
  flatten_digging-up-the-oceans-past_class_sorted_raw.csv and the flattening script: Oceans_past_flatten_transcriptions_no_clean.py

#### Parameter .txt files used with reconcile.py
The sample files were reconciled using reconcile.py using the parameter lists found in the file reconcile_parameters.txt included here.  This was done two ways, once a reconciliation of the flattened .csv file, and again a direct reconciliation of the raw export.  In both cases the --explanations parameter was set, and both the reconciled and summary files were requested. For the raw data export the unreconciled file is also required. Note for the flattened files the -f csv format requires the -c column listing for the fields and their type to be flattened.

#### Reconciled and unreconciled files.
This procedure produced two sets of reconciled and unreconciled data. Any one set can be used to demonstrate the editor.  The flattened file gives the cleanest output since it has simple column headers:

The flattened version of Oceans' past:
oceans-past_reconciled.csv
flatten_digging-up-the-oceans-past_class_sorted_raw.csv
oceans-past_summary.html

If you want to see what it looks like reconciled directly from the raw Oceans'export (the normal method for NfN projects)
oceans-past_reconciled_nfn.csv
oceans-past_unreconciled_nfn.csv
oceans-past_summary_nfn.html

## Setup and run the demo
See the Editor readme file to set up the editor for use.  This will consist of setting up a Python environment with the necessary packages, downloading the nfn_editor and update_drivers files to the directory using your Python environment, downloading the set(s) of demo data to a known directory (or with the editor), and a preliminary run of update driver.py for the browser you want to use.

A sample of the parameter list for either of the two sets of data above can be found in editor_parameters.txt.  Run the editor with the command format:
./ nfn_editor.py -d <path to working directory> -f <unreconciled.csv> -r <reconciled.csv> -u <a user name> -b <browser type>
  
Refer to the editor readme for how to use the editor.  As soon as the editor is run it will create the databases it will use and modify.  For this specific demo, the latitude and longitude fields have a number of ties where the selected choice is not the best option. Start by selecting the six lat/long fields for the problem "Tie matches".  You can then work through those subjects with ties matches and select the better choice of the various volunteer's inputs. Once the problems have been corrected you can rerun the script for other problems types but this data is very clean so most selections will show no problems.  You can review the changed subjects by selecting "Modified" for all the fields.  You can also delete the reconciled database that was modified and rerun the whole thing over again at any time - the reconciled file itself is not modified.
  
  




#!/usr/bin/env python

################################
#
# manageRequests.py
#
#  Script to create, modify, and clone McM requests.
#
#  author: David G. Sheffield (Rutgers)
#
################################

import sys
import os.path
import argparse
import csv
import pprint
sys.path.append('/afs/cern.ch/cms/PPD/PdmV/tools/McM/')
from rest import * # Load class to access McM
from requestClass import * # Load class to store request information

def getArguments():
    defaultPWG = 'XXX' # Change this line to your PWG, then -p flag is not needed

    parser = argparse.ArgumentParser(description='Create, modify, and clone McM requests.')

    # Command line flags
    parser.add_argument('file_in')
    parser.add_argument('-c', '--campaign', action='store', dest='campaign', metavar='name', help='Set member_of_campaign.')
    parser.add_argument('-p', '--pwg', action='store', dest='pwg', default=defaultPWG, help='Set PWG. Defaults to %(default)s. Change the variable defaultPWG to your PWG.')
    parser.add_argument('-m', '--modify', action='store_true', dest='doModify', help='Modify existing requests. The CSV file must contain the PrepIds of the requests to be modified.')
    parser.add_argument('--clone', action='store', dest='cloneId', default='', help='Clone an existing request by giving its PrepId')
    parser.add_argument('-d', '--dry', action='store_true', dest='doDryRun', help='Dry run of result. Does not add requests to McM.')
    parser.add_argument('--dev', action='store_true', dest='useDev', help='Use dev/test instance.')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s v0.1')
    
    args_ = parser.parse_args()
    return args_

def checkFile(file_):
    # Check that CSV file exists
    if not os.path.isfile(file_):
        print "Error: File %s does not exist." % file_
        print "Exiting with status 1."
        sys.exit(1)

def checkPWG(pwg_):
    pwg_list = ['B2G','BPH','BTW','EGM','EWK','EXO','FSQ','FWD','HCA','HIG','HIN','JME','L1T','MUO','QCD','SMP','SUS','TAU','TOP','TRK','TSG']
    # Check that PWG is valid
    if pwg_ not in pwg_list:
        print "Error: %s is not a recognized PWG." % pwg_
        if pwg_ == 'XXX':
            print "Change the default value for flag -p to your PWG by modifying the variable defaultPWG on line 23."
        sys.stdout.write("Options are:")
        for iPWG in pwg_list:
            sys.stdout.write(" ")
            sys.stdout.write(iPWG)
        sys.stdout.write("\n")
        print "Exiting with status 2."
        sys.exit(2)

def checkNotCreate(doModify_,cloneId_):
    # Check that script isn't being asked to both modify and clone a request
    doClone = False
    if cloneId_ != "": doClone = True
    if doModify_ and doClone:
        print "Error: cannot both --modify and --clone."
        print "Exiting with status 6."
        sys.exit(6)
    return doModify_ or doClone # Return variable to use in fillFields()

def exitDuplicateField(file_in_,field_):
    print "Error: File %s contains multiple instances of the field %s" % (file_in_,field_)
    print "Exiting with status 3."
    sys.exit(3)

def getFields(csvfile_,file_in_):
    # List of indices for each field in CSV file
    list = [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]
    header = csv.reader(csvfile_).next()
    for ind, field in enumerate(header):
        if field in ['Dataset name','Dataset Name','Dataset','dataset']:
            #ensure no duplicate fields
            if list[0] > -1: exitDuplicateField(file_in_,"Dataset name")
            list[0] = ind
        elif field in ['EOS','eos','Eos','MCDBID','mcdbid']:
            if list[1] > -1: exitDuplicateField(file_in_,"EOS")
            list[1] = ind
        elif field in ['Cross section [pb]','Cross section','Cross section (pb)','Cross Section','Cross Section [pb]','Cross Section (pb)','CS','CS [pb]','CS (pb)','Xsec','Xsec [pb]','Xsec (pb)']:
            if list[2] > -1: exitDuplicateField(file_in_,"Cross section")
            list[2] = ind
        elif field in ['Total events','Total Events','Events','events','total events','Number of Events']:
            if list[3] > -1: exitDuplicateField(file_in_,"Total events")
            list[3] = ind
        elif field in ['Fragment name','Fragment Name','Generator fragment name','Generator Fragment Name','Fragment','fragment']:
            if list[4] > -1: exitDuplicateField(file_in_,"Fragment name")
            list[4] = ind
        elif field in ['Time per event [s]','Time per event','Time per event (s)','Time per Event','Time per Event [s]','Time per Event (s)','Time','Time [s]','Time (s)','time','time [s]','time (s)']:
            if list[5] > -1: exitDuplicateField(file_in_,"Time per event [s]")
            list[5] = ind
        elif field in ['Size per event [kB]','Size per event','Size per event (kB)','Size per Event','Size per Event [kB]','Size per Event (kB)','size','size [kB]','size (kB)']:
            if list[6] > -1: exitDuplicateField(file_in_,"Size per event [kB]")
            list[6] = ind
        elif field in ['Tag','tag','Fragment Tag','Fragment tag','fragment tag','sha','SHA','SHA-1','sha-1']:
            if list[7] > -1: exitDuplicateField(file_in_,"Fragment tag")
            list[7] = ind
        elif field in ['Generator','generator']:
            if list[8] > -1: exitDuplicateField(file_in_,"Generator")
            list[8] = ind
        elif field in ['Filter efficiency','FilterEfficiency','filter efficiency']:
            if list[9] > -1: exitDuplicateField(file_in_,"Filter efficiency")
            list[9] = ind
        elif field in ['Filter efficiency error','Filter Efficiency Error','filter efficiency error']:
            if list[10] > -1: exitDuplicateField(file_in_,"Filter efficiency error")
            list[10] = ind
        elif field in ['Match efficiency','Match Efficiency','match efficiency']:
            if list[11] > -1: exitDuplicateField(file_in_,"Match efficiency")
            list[11] = ind
        elif field in ['Match efficiency error','Match Efficiency Error','match efficiency error']:
            if list[12] > -1: exitDuplicateField(file_in_,"Match efficiency error")
            list[12] = ind
        elif field in ['PWG','pwg']:
            if list[13] > -1: exitDuplicateField(file_in_,"PWG")
            list[13] = ind
        elif field in ['Campaign','campaign','Member of Campaign','Member of campaign','member of campaign']:
            if list[14] > -1: exitDuplicateField(file_in_,"Member of campaign")
            list[14] = ind
        elif field in ['PrepId','PrepID','PREPID','prepid']:
            if list[15] > -1: exitDuplicateField(file_in_,"PrepId")
            list[15] = ind
        elif field in ['Sequences customise','Sequences customize']:
            if list[16] > -1: exitDuplicateField(file_in_,"Sequences customise")
            list[16] = ind
        elif field in ['Process string','Process String']:
            if list[17] > -1: exitDuplicateField(file_in_,"Process string")
            list[17] = ind
        else:
            print "Error: The field %s is not valid." % field
            print "Exiting with status 4."
            sys.exit(4)

    return list

def formatFragment(file_,campaign_):
    if len(file_.split("/")) > 1:
        return file_
    elif campaign_ in ['Summer12']: # 8TeV
        return "Configuration/GenProduction/python/EightTeV/"+file_
    elif campaign_ in ['Fall13','RunIIFall14GS','RunIIWinter15GS']: # 13 TeV
        return "Configuration/GenProduction/python/ThirteenTeV/"+file_
    else:
        print "Error: Cannot determine energy of campaign %s." % campaign_
        print "Exiting with status 5."
        sys.exit(5)

def fillFields(csvfile, fields, campaign, PWG, notCreate_):
    requests = [] # List containing request objects
    num_requests = 0
    for row in csv.reader(csvfile):
        num_requests += 1
        tmpReq = Request()
        if fields[0] > -1: tmpReq.setDataSetName(row[fields[0]])
        if fields[1] > -1:
            tmpReq.setMCDBID(row[fields[1]])
        elif not notCreate_:
            tmpReq.setMCDBID(-1)
        if fields[2] > -1:
            tmpReq.setCS(row[fields[2]])
        elif not notCreate_:
            tmpReq.setCS(1.0)
        if fields[3] > -1: tmpReq.setEvts(row[fields[3]])
        if fields[14] > -1:
            campaign = row[fields[14]]
            tmpReq.setCamp(campaign)
        elif not notCreate_:
            tmpReq.setCamp(campaign)
        if fields[4] > -1: tmpReq.setFrag(formatFragment(row[fields[4]],campaign))
        if fields[5] > -1: tmpReq.setTime(row[fields[5]])
        if fields[6] > -1: tmpReq.setSize(row[fields[6]])
        if fields[7] > -1: tmpReq.setTag(row[fields[7]])
        if fields[8] > -1: tmpReq.setGen(row[fields[8]].split(" ")) # Multiple generators separated by spaces
        if fields[9] > -1:
            tmpReq.setFiltEff(row[fields[9]])
        elif not notCreate_:
            tmpReq.setFiltEff(1.0)
        if fields[10] > -1:
            tmpReq.setFiltEffErr(row[fields[10]])
        elif not notCreate_:
            tmpReq.setFiltEffErr(0.0)
        if fields[11] > -1:
            tmpReq.setMatchEff(row[fields[11]])
        elif not notCreate_:
            tmpReq.setMatchEff(1.0)
        if fields[12] > -1:
            tmpReq.setMatchEffErr(row[fields[12]])
        elif not notCreate_:
            tmpReq.setMatchEffErr(0.0)
        if fields[13] > -1:
            tmpReq.setPWG(row[fields[13]])
        elif not notCreate_:
            tmpReq.setPWG(PWG)
        if fields[15] > -1:
            tmpReq.setPrepId(row[fields[15]])
        if fields[16] > -1:
            tmpReq.setSequencesCustomise(row[fields[16]])
        if fields[17] > -1:
            tmpReq.setProcessString(row[fields[17]])
        requests.append(tmpReq)
    return requests, num_requests

def createRequests(requests, num_requests, doDryRun, useDev):
    # Create new requests based on campaign and PWG
    mcm = restful( dev=useDev ) # Get McM connection

    if not doDryRun:
        print "Adding %d requests to McM." % num_requests
    else:
        print "Dry run. %d requests will not be added to McM." % num_requests 
    for reqFields in requests:
        if not reqFields.useCamp():
            print "A campaign is needed for new requests."
            continue

        # Create new request's dictionary
        new_req = {'pwg':reqFields.getPWG(),'member_of_campaign':reqFields.getCamp(),'mcdb_id':reqFields.getMCDBID()}
        # Fill dictionary with fields
        if reqFields.useDataSetName(): new_req['dataset_name'] = reqFields.getDataSetName()
        if reqFields.useEvts(): new_req['total_events'] = reqFields.getEvts()
        if reqFields.useFrag(): new_req['name_of_fragment'] = reqFields.getFrag()
        if reqFields.useTime(): new_req['time_event'] = reqFields.getTime()
        if reqFields.useSize(): new_req['size_event'] = reqFields.getSize()
        if reqFields.useTag(): new_req['fragment_tag'] = reqFields.getTag()
        if reqFields.useGen(): new_req['generators'] = reqFields.getGen()
        # Sequences might need to be added below with generator parameters
        if reqFields.useSequencesCustomise(): new_req['sequences'][0]['customise'] = reqFields.getSequencesCustomise()
        if reqField.useProcessString(): new_req['process_string'] = reqFields.getProcessString()
        
        if not doDryRun:
            answer = mcm.putA('requests', new_req) # Create request
            if answer['results']:
                # Cannot fill generator parameters while creating a new request
                # Modify newly created request with generator parameters
                mod_req = mcm.getA('requests',answer['prepid']) # Get newly created request
                # Fill generator parameters
                mod_req['generator_parameters'][0]['cross_section'] = reqFields.getCS()
                mod_req['generator_parameters'][0]['filter_efficiency'] = reqFields.getFiltEff()
                mod_req['generator_parameters'][0]['filter_efficiency_error'] = reqFields.getFiltEffErr()
                mod_req['generator_parameters'][0]['match_efficiency'] = reqFields.getMatchEff()
                mod_req['generator_parameters'][0]['match_efficiency_error'] = reqFields.getMatchEffErr()
                update_answer = mcm.updateA('requests',mod_req) # Update request with generator parameters
                if update_answer['results']:
                    print answer['prepid'],"created"
                else:
                    print answer['prepid'],"created but generator parameters not set"
            else:
                if reqFields.useDataSetname():
                    print reqFields.getDataSetName(),"failed to be created"
                else:
                    print "A request has failed to be created"
        else:
            if reqFields.useDataSetName():
                print reqFields.getDataSetName(),"not created"
            else:
                print "request not created"
            pprint.pprint(new_req)

def modifyRequests(requests, num_requests, doDryRun, useDev):
    # Modify existing request based on PrepId
    mcm = restful( dev=useDev ) # Get McM connection

    if not doDryRun:
        print "Modifying %d requests to McM." % num_requests
    else:
        print "Dry run. %d requests will not be modified in McM." % num_requests
    for reqFields in requests:
        if not reqFields.usePrepId():
            print "PrepId is missing."
            continue
        
        # Get request from McM
        mod_req = mcm.getA('requests',reqFields.getPrepId())
        if reqFields.useDataSetName(): mod_req['dataset_name'] = reqFields.getDataSetName()
        if reqFields.useMCDBID(): mod_req['mcdb_id'] = reqFields.getMCDBID()
        if reqFields.useEvts(): mod_req['total_events'] = reqFields.getEvts()
        if reqFields.useFrag(): mod_req['name_of_fragment'] = reqFields.getFrag()
        if reqFields.useTime(): mod_req['time_event'] = reqFields.getTime()
        if reqFields.useSize(): mod_req['size_event'] = reqFields.getSize()
        if reqFields.useTag(): mod_req['fragment_tag'] = reqFields.getTag()
        if reqFields.useGen(): mod_req['generators'] = reqFields.getGen()
        if reqFields.useCS(): mod_req['generator_parameters'][0]['cross_section'] = reqFields.getCS()
        if reqFields.useFiltEff(): mod_req['generator_parameters'][0]['filter_efficiency'] = reqFields.getFiltEff()
        if reqFields.useFiltEffErr(): mod_req['generator_parameters'][0]['filter_efficiency_error'] = reqFields.getFiltEffErr()
        if reqFields.useMatchEff(): mod_req['generator_parameters'][0]['match_efficiency'] = reqFields.getMatchEff()
        if reqFields.useMatchEffErr(): mod_req['generator_parameters'][0]['match_efficiency_error'] = reqFields.getMatchEffErr()
        if reqFields.useSequencesCustomise(): mod_req['sequences'][0]['customise'] = reqFields.getSequencesCustomise()
        if reqField.useProcessString(): mod_req['process_string'] = reqFields.getProcessString()

        if not doDryRun:
            answer = mcm.updateA('requests',mod_req) # Update request
            if answer['results']:
                print reqFields.getPrepId(),"modified"
            else:
                print reqFields.getPrepId(),"failed to be modified"
        else:
            print reqFields.getPrepId(),"not modified"
            pprint.pprint(mod_req)

def cloneRequests(requests, num_requests, doDryRun, useDev, cloneId_):
    # Create new requests be cloning an old one based on PrepId
    mcm = restful( dev=useDev ) # Get McM connection

    if not doDryRun:
        print "Adding %d requests to McM using clone." % num_requests
    else:
        print "Dry run. %d requests will not be added to McM using clone." % num_requests
    for reqFields in requests:
        clone_req = mcm.getA('requests',cloneId_) # Get request to clone
        if reqFields.useDataSetName(): clone_req['dataset_name'] = reqFields.getDataSetName()
        if reqFields.useMCDBID(): clone_req['mcdb_id'] = reqFields.getMCDBID()
        if reqFields.useEvts(): clone_req['total_events'] = reqFields.getEvts()
        if reqFields.useFrag(): clone_req['name_of_fragment'] = reqFields.getFrag()
        if reqFields.useTime(): clone_req['time_event'] = reqFields.getTime()
        if reqFields.useSize(): clone_req['size_event'] = reqFields.getSize()
        if reqFields.useTag(): clone_req['fragment_tag'] = reqFields.getTag()
        if reqFields.useGen(): clone_req['generators'] = reqFields.getGen()
        if reqFields.useCS(): clone_req['generator_parameters'][0]['cross_section'] = reqFields.getCS()
        if reqFields.useFiltEff(): clone_req['generator_parameters'][0]['filter_efficiency'] = reqFields.getFiltEff()
        if reqFields.useFiltEffErr(): clone_req['generator_parameters'][0]['filter_efficiency_error'] = reqFields.getFiltEffErr()
        if reqFields.useMatchEff(): clone_req['generator_parameters'][0]['match_efficiency'] = reqFields.getMatchEff()
        if reqFields.useMatchEffErr(): clone_req['generator_parameters'][0]['match_efficiency_error'] = reqFields.getMatchEffErr()
        if reqFields.useSequencesCustomise(): mod_req['sequences'][0]['customise'] = reqFields.getSequencesCustomise()
        if reqField.useProcessString(): mod_req['process_string'] = reqFields.getProcessString()

        if not doDryRun:
            answer = mcm.clone(cloneId_,clone_req) # Clone request
            if answer['results']:
                print answer['prepid'],"created using clone"
            else:
                if reqFields.useDataSetName():
                    print reqFields.getDataSetName(),"failed to be created using clone"
                else:
                    print "request failed to be created using clone"
        else:
            if reqFields.useDataSetName():
                print reqFields.getDataSetName(),"not created using clone"
            else:
                print "request not created using clone"
            pprint.pprint(clone_req)

def main():
    args = getArguments() # Setup flags and get arguments
    checkPWG(args.pwg) # Make sure PWG is an actual PWG
    # Check that script is not asked to both modify and clone
    # Store variable that is true if script is asked to modify or clone
    notCreate = checkNotCreate(args.doModify,args.cloneId)
    checkFile(args.file_in) # Ensure CSV file exists
    
    if args.useDev:
        print "Using dev/test instance."

    csvfile = open(args.file_in,'r') # Open CSV file
    fields = getFields(csvfile,args.file_in) # Get list of field indices
    # Fill list of request objects with fields from CSV and get number of requests
    requests, num_requests = fillFields(csvfile, fields, args.campaign, args.pwg, notCreate)

    if args.doModify:
        # Modify existing requests
        modifyRequests(requests, num_requests, args.doDryRun, args.useDev)
    elif args.cloneId != "":
        # Create new requests using clone
        cloneRequests(requests, num_requests, args.doDryRun, args.useDev, args.cloneId)
    else:
        # Create new requests
        createRequests(requests, num_requests, args.doDryRun, args.useDev)
    
if __name__ == '__main__':
    main()

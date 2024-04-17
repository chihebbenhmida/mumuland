#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sqlite3 
import os, csv, datetime, glob, sys
import subprocess
import shutil
import re    
import json
from tabulate import tabulate
import errno
import hashlib

def wait_for_excel(myXlsxFile):
    writeable=False
    while writeable==False:
        try :
            f = open(myXlsxFile, 'a')
            writeable=True
            f.close()
        except OSError as err :  
            if err.errno  ==  errno.EBUSY :  
                print("Priere de fermer le fichier Excel : " +os.path.basename(myXlsxFile))  
                print("Attente de 5 sec")
                time.sleep(5)
            else :
                print(err)
     
def os_mv(MyFileName, MyDest, verbose=False):

    if MyFileName == MyDest :
        return 
    if not os.path.isfile(MyFileName) :
        print(MyFileName, ' not found !')
        
    if os.path.isdir(MyDest) :
        MyNewFile = MyDest+'/'+os.path.basename(MyFileName)
    else :
        MyNewFile = MyDest
        
    if os.path.isfile(MyNewFile) :
        os.remove(MyNewFile)
        
    os.rename(MyFileName, MyNewFile)

    if verbose : 
        print('moved ', MyFileName,' -> ',  MyDest)

def os_cp(src_path, dest_path , verbose=False):
    if not os.path.exists(src_path ) :
        print(src_path+" Not found !")
        exit(0)

    if verbose :
        src_type='file' if os.path.isfile(src_path) else 'dir'
        if os.path.exists(dest_path ) :
            dest_type='file' if os.path.isfile(dest_path) else 'dir'
        else :
            dest_type='not_exists'
        print("\ncopy :["+src_type+"] "+src_path+" -> ["+dest_type+"] "+dest_path+"")

    ### Copie reelle
    if os.path.isfile(src_path ):
        shutil.copy(src_path, dest_path)
    else :

        shutil.copytree(src_path, dest_path+'/'+os.path.basename(src_path), dirs_exist_ok=True)

    if verbose :
        if os.path.isfile(src_path ) :
            fileout=dest_path if os.path.isfile(dest_path ) else dest_path+"/"+os.path.basename(src_path)
        else :
            fileout=""
        print(subprocess.check_output(['ls', '-ldh', src_path]).decode('utf-8').strip())
        if fileout != "" :
            print(subprocess.check_output(['ls', '-ldh', fileout]).decode('utf-8').strip())
        else :
            print(subprocess.check_output(['ls', '-ldh', dest_path+'/'+os.path.basename(src_path)]).decode('utf-8').strip())
   
    return
    
def os_rm(src_path, verbose=False) :
    
    # if not os.path.exists (src_path ) :
        # print (src_path+" Not found !")
        # exit (0)
        
    if verbose :
        src_type='file' if os.path.isfile (src_path) else 'dir'
        print ("\nremove "+src_type+": "+src_path)
    
    try :
        if os.path.isfile(src_path) :
            os.remove(src_path)
            
        if os.path.isdir(src_path ) :
            shutil.rmtree(src_path)
            
    except OSError as err :  
        # print(err) 
        # print(err.filename2) 
        if err.errno  ==  errno.EBUSY :
            # print(dir(err))  
            print(err) 

            print(err.args)
            print(err.errno)
            print(err.filename)
            print(err.filename2)
            print(err.strerror)
 
            print("Attente de 5 sec")
            time.sleep(5)
            exit(0)

def os_mkdir(MyDirName, verbose = False):
    if not os.path.isdir(MyDirName):
        if verbose :
            print("os_mkdir : "+MyDirName)
        os.makedirs(MyDirName)        
        
def os_find(myPath, pattern, verbose=False) :
    # myDir="c:/Data/Travail/01_Projets/202203_TEST_SIM"
    # print(os_find(myDir, "*key*")) 
    retList=[]
    if not os.path.isdir(myPath) :
        print(myPath+" is not  dir")
    else :   
        files = glob.glob(myPath+'/**/'+pattern, recursive=True)
        for a in files :
            if os.path.isfile(a) :
                if verbose :
                    print(a.replace(myPath,"."))
                retList.append(a)
    return retList

def os_sgrep_match( mySTR, myRegexp) :
    # pattern = re.compile(myRegexp)
    return bool (re.match(myRegexp, mySTR))

def os_fgrep_match(myFile, myRegexp) :
    with open(myFile, 'r') as f :
        file_lines = f.readlines()
    lines=[]
    for line in file_lines :
        print(list(line))
        print(line)
        if bool (re.match(myRegexp, line)) :
            lines.append(line)
    
    return lines
    
def os_select_line(myFile, myString) :
    with open(myFile, 'r') as f :
        file_lines = f.readlines()
    lines=[]
    for line in file_lines :
        if myString in line :
            # print(line)
            lines.append(line)
    
    return lines
    
def os_touchEmpty(MyFileName):
    open (MyFileName, 'w').close()

def os_touch(MyFileName) :    
    if not os.path.isfile(MyFileName):
        open (MyFileName, 'w').close()        
    with open (MyFileName, 'a') :
        os.utime (MyFileName, None) 

def os_cat(myFile) :
    with open(myFile, "r") as f :
        return f.readlines()

def os_smd5( strData) :
    strHash = hashlib.md5(strData .encode('utf-8')).hexdigest().upper()
    return strHash
    
def os_fmd5( myFile) :
    with open(myFile, "r") as f :
        lines = f.readlines()
        strFileData = ""
        for line in lines :
            strFileData = strFileData + line 

    return os_smd5( strFileData)
            
def os_head(myFile, nbLines):
    with open(myFile, "r") as f :
        Lines = f.readlines()
    for i in range(0,nbLines) :
        print(Lines[i], end="")

def os_see(myFile ):    
    with open(myFile, "r") as f :
        Lines = f.readlines()

    head = [ Lines[i].rstrip("\n").split(';') for i in range(0,5) ]
    center = [[ '...' for i in range(0, len(head[0]))]]
    tail = [ Lines[i].rstrip("\n").split(';') for i in range(len(Lines) - 5, len(Lines)) ]
    
    NL = head + center + tail
    
    tabSTR = tabulate(NL, headers="firstrow", tablefmt="simple", floatfmt=".3f")
    print(tabSTR)

def os_tail(myFile, nbLines):
    with open(myFile, "r") as f :
        Lines = f.readlines()
        
    for i in range(len(Lines) - nbLines, len(Lines)) :
        print(Lines[i], end="")
            
def os_sed(myFile, strA, strB):

    with open(myFile, "r") as f :
        Lines = f.readlines() 
    with open(myFile, "w") as f :
        for line in Lines :
            f.write(line.replace(strA,strB))   
        
def os_fileAppend(MyFileName, MyString) :
    with open(MyFileName, 'a', newline='\n') as d_file:
        d_file.write(MyString)
        d_file.write('\n')

def deprect_dir_copy(mySrcDir, myDestDir) :
    shutil.copytree(mySrcDir, os.path.join(myDestDir, os.path.basename(mySrcDir)), dirs_exist_ok=True )

def deprect_FileRemove(MyFileName):
    # open (MyFileName, 'w').close()
    if os.path.isfile(MyFileName):
        os.remove(MyFileName)
        
def deprect_FileCopy(src, dst) :

    # print(src)
    # print(dst)
    # if os.path.isfile(dst)  :
        # os.remove(dst)
        
    # if os.path.isdir(dst) :
        # shutil.rmtree(dst)
        
    # if os.path.isdir(src) :
        # shutil.copytree(src, dst)
    # else :
    # shutil.copy(src, dst)
    if os.path.isdir(dst) :
        shutil.copy(src, dst)
 
 
def deprec_create_dir_verbose(myDir) :
    if not os.path.isdir(myDir) :
        print("Creating dir : "+myDir)
        os.makedirs(myDir)



    
def yearmon_diff (begin_yearmon, end_yearmon, diff_mon ) :
    # Accepte deux modes de lancement :
    #diff moths ('202201', '202206', 0) calcul du diff nb mon nb_mon) calcul du mois final
    #diff moths ('202201'
    # print()
    if begin_yearmon == '' :
        return

    s_begin_yearmon= int (begin_yearmon [0:4])* 12+ int (begin_yearmon [4:6]) - 1
    

    if end_yearmon == '' : ## priorite 1 calcul end_yearmon
        s_end_yearmon=int(s_begin_yearmon + diff_mon)
        end_yearmon=f'{s_end_yearmon // 12:04d}'+f'{1+ (s_end_yearmon % 12):02d}'

    elif diff_mon == 0 :
        s_end_yearmon = int(end_yearmon [0:4])* 12+ int (end_yearmon [4:6]) - 1
        diff_mon = s_end_yearmon - s_begin_yearmon
    
    # if diff_mon > 1000 :
        # diff_mon = None 
    return begin_yearmon, end_yearmon, diff_mon 



def dict_to_csv_List(myDictList, delimiter = ';' , header=True) :

    # print(myDictList)
    # print(list(myDictList[0].keys()))
    
    myList = []  
    row_length = len(myDictList[0])
    
    myStr  = ''   
    if header  :
        myStr=''
        for idx, element in enumerate(myDictList[0]):
            if idx == 0 :
                myStr = myStr + str(element)
            else :
                myStr = myStr + delimiter + str(element)
        myList.append(myStr)
        # print('myStr='+myStr)
    
    
    for row in myDictList:
        myStr=''
        for idx, element in enumerate(row.values()):
            if idx == 0 :
                myStr = myStr + str(element)
            else :
                myStr = myStr + delimiter + str(element)
        
        myList.append(myStr)
        # print('myStr='+myStr)     
            
    # print(myList)
    return myList
    


def dict_to_csv_string(myDictList, delimiter = ';' , header=True) :

    myStr = ''     
    if len(myDictList) == 0 :
        return myStr
        
    row_length = len(myDictList[0])
    
    if header  :
        for idx, element in enumerate(myDictList[0]):
            if idx != row_length - 1 :
                myStr = myStr + str(element)+delimiter 
            else :
                myStr = myStr + str(element) + '\n' 
    
    for row in myDictList:
        for idx, element in enumerate(row.values()):
            # print(row)
            if idx != row_length - 1 :
                myStr = myStr + str(element)+delimiter 
            else :
                myStr = myStr + str(element) + '\n'  
    return myStr



def list_to_csv_string(myList, delimiter = ';') :
    # print('list_to_csv_string deb')
    # print('mylist')
    # print(myList)
    myStr = ''
    for row in myList:
        for idx, element in enumerate(row) :
            if idx == 0 :
                myStr = myStr + str(element)
            else :
                myStr = myStr + delimiter + str(element)
        myStr = myStr + '\n' 
    # print('myStr')
    # print(myStr)
    # print('list_to_csv_string Fin')
    return myStr

from inspect import currentframe, getframeinfo
def printCodeContext():
    # print("filename  : "+inspect.stack()[1][1])
    # print("lineno    : "+str(inspect.stack()[1][2]))
    # print("funcname  : "+inspect.stack()[1][3])
    
    ## Courant
    print("Error context :")
    for i in range(1,len(inspect.stack())) : 
        print("%s:[%d] %s:%s:%s " % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), i,  str(inspect.stack()[i][1]) ,  str(inspect.stack()[i][2]),  str(inspect.stack()[i][3]) ))
    

    
import inspect, datetime, time
myself           = lambda: inspect.stack()[1][3]
calling_function = lambda: inspect.stack()[2][3]
all_chronos={'progam_start':time.perf_counter()}
count_calls={}
def prf_count_function_calls(dump=False ) :    
    calling_func_name=calling_function()
    if calling_func_name in count_calls.keys() :
        count_calls[calling_func_name] = count_calls[calling_func_name] + 1
    else :
        count_calls[calling_func_name]=1
        count_calls[calling_func_name+"_duree"]=0
    if dump :
        print(count_calls)
        
def log_text(Top="", myText="") :
    strNow=datetime.datetime.now().strftime("%Y/%m/%d-%H:%M:%S")
      
    calling_func_name=calling_function()
    
    if Top.lower() in  ['start', 'debut'] :
        all_chronos["py_tag_"+calling_func_name]=time.perf_counter()       
        print(strNow+";"+calling_func_name+";Debut")
   
    if Top.lower() in  ['stop', 'fin']  :
        ms = (time.perf_counter()-all_chronos["py_tag_"+calling_func_name])
        print(strNow+";"+calling_func_name+";Fin;"+"elapsed " + time.strftime('%M:%S', time.gmtime(ms))+" min:ss \n")        
        # count_calls[calling_func_name+"_duree"]=count_calls[calling_func_name+"_duree"]+ms
        
    if myText != "" :
        print(strNow+";"+myText)
        
 
 
def split_file(in_file, nb_lines) :
    # usage 
    # inFile="path/file.txt"
    # split_file(inFile,  1500)
    
    if not os.path.isfile(in_file) :
        print("File not found : "+in_file)
        exit(0)
    print('Splitting '+os.path.basename(in_file)+" into "+str(nb_lines)+"-line batchs")
    
    file_name, file_extension = os.path.splitext(in_file)
    
    prefix = os.path.basename(file_name)
    suffix = file_extension
    
    os.chdir(os.path.dirname(in_file))
    out_dir = prefix     
    if os.path.isdir(out_dir) :
        shutil.rmtree(out_dir)
    os.mkdir(out_dir)
    
    with open(in_file,'r') as f_in :
        Lines= f_in.readlines()
    if len(Lines) == 0 :
        # print("Empy filenothkng to split : " + os.path.basename(in_file))
        return
        
    prec        = str(len(str((len(Lines) // nb_lines)+1)))
    myFormat    = '0'+prec+'d'
    file_index  = 0
    lHeader     = Lines[0]
    f_out       = None
    for idx, line in enumerate(Lines) :
        if idx % nb_lines == 0 : 
            if idx != 0 :
                f_out.close()
            file_index = file_index + 1
            outfile = out_dir+"/"+prefix +'_' +format(file_index, myFormat) + suffix
            f_out = open(outfile, 'w')
            if idx != 0 :
                f_out.write(lHeader)    
        f_out.write(line)
    f_out.close()




def transpose_list(myRows, hSortAsc=True, vSortAsc=True, verbose=False) :

    # log_text('Debut')
    myList=[]
    if len(myRows ) == 0 :
        return myList
    
    if len(myRows[0]) != 3 :
        print("Taille de tableau non conforme, doit etre 3")
        exit(0)
        
    id1_name=list(myRows[0].keys())[0]
    id2_name=list(myRows[0].keys())[1]
    id3_name=list(myRows[0].keys())[2]

    id1_list = sorted(list(set([d[id1_name] for d in myRows])), reverse=not vSortAsc)
    id2_list = sorted(list(set([d[id2_name] for d in myRows])), reverse=not hSortAsc)
    
    
    # empty_dict={}
    # empty_dict[id1_name] = 0
    # for element in id2_list : 
        # empty_dict[element] = 0      
    # myList=[]
    # for val in id1_list :    
        # mydict = empty_dict.copy() 
        # mydict[id1_name]=val 
        # for row in myRows : 
            # if row[id1_name] == val : 
                # mydict[row[id2_name]]=row[id3_name]
        # myList.append(mydict)

    empty_dict_1={}
    for element in id2_list : 
        empty_dict_1[element] = 0    
    aList={}
    for myID in  id1_list :
        aList[myID] = empty_dict_1.copy()
    for row in myRows :
        aList[row[id1_name]][row[id2_name]] = row[id3_name] 
    empty_dict_2={}
    empty_dict_2[id1_name] = 0
    for element in id2_list : 
        empty_dict_2[element] = 0 
    
    for val in id1_list :        
        new_dict = empty_dict_2.copy()
        new_dict[id1_name] = val
        for elem in id2_list :
            new_dict[elem] = aList[val][elem]
        myList.append(new_dict)
    
    if verbose : 
        print(tabulate(myList, headers='keys', tablefmt='csv', floatfmt=".3f"))
    # log_text('Fin')    
    return myList


def most_frequent(List):
    if len(List) != 0 :
        return max(set(List), key = List.count)
    else:
        return None


def divide_to_chunks(myList, chk_size):
    for index in range(0, len(myList), chk_size):
        yield myList[index:index + chk_size]



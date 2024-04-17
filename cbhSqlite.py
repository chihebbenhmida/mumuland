#!/usr/bin/python3.8
import os, csv
import sqlite3
from   tabulate import tabulate
import hashlib


import inspect, datetime, time
sqlite3_myself           = lambda: inspect.stack()[1][3]
sqlite3_calling_function = lambda: inspect.stack()[2][3]
sqlite3_all_chronos={'progam_start':time.perf_counter()}
def sqlite3_log_text(Top="", myText="") :
    strNow=datetime.datetime.now().strftime("%Y/%m/%d-%H:%M:%S")
   
    if Top.lower() in  ['start', 'debut'] :
        sqlite3_all_chronos["py_tag_"+sqlite3_calling_function()]=time.perf_counter()       
        print(strNow+";"+sqlite3_calling_function()+";Debut")
   
    if Top.lower() in  ['stop', 'fin']  :
        ms = (time.perf_counter()-sqlite3_all_chronos["py_tag_"+sqlite3_calling_function()])
        print(strNow+";"+sqlite3_calling_function()+";Fin;"+"elapsed " + time.strftime('%M:%S', time.gmtime(ms))+" min:ss ")
        print()        
    if myText != "" :
        print(strNow+";"+myText)
        
def sqlite3_checkContentChanged(myDbFile, myKey, myExtQuery) :
    ref_db="/tmp/checkContentChanged/ChkChange.sqlite"
    tmpFile="/tmp/checkContentChanged/out.csv"
    
    sqlite3_read2csvFile(myDbFile, myExtQuery, tmpFile, verbose=False)
    strKEYS=""
    with open(tmpFile,'r') as f :
        for a in f.readlines() :
            strKEYS=strKEYS + a
    strHASH = hashlib.md5(strKEYS.encode('utf-8')).hexdigest().upper()
    lQuery="""select * from key_hash
    where   key1 = '"""+myDbFile+"""'
    and     key2 = '"""+myKey+"""' """
    rows = sqlite3_read2dictList(ref_db, lQuery, verbose=False)

    changed=False
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')  
    if len(rows) == 0 :
        changed = True               
        lQuery="""insert into key_hash (key1,key2,hash_value, update_date) values
        ('"""+myDbFile+"""', '"""+myKey+"""', '"""+strHASH+"""'  , '"""+now+"""')  """
        rows = sqlite3_updateData(ref_db, lQuery, verbose=False)
    else :
        if strHASH !=  rows[0]['hash_value'] : 
            changed = True                    
            lQuery="""update key_hash
            set hash_value = '"""+strHASH+"""' ,
            update_date = '"""+now+"""'
            where   key1 = '"""+myDbFile+"""'
            and     key2 = '"""+myKey+"""' """
            rows = sqlite3_updateData(ref_db, lQuery, verbose=False)
            
        else :
            changed = False
    return changed
    
def sqlite3_dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0].lower()] = row[idx]
    return d

def sqlite3_CreateConnexion(my_db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param my_db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn             = sqlite3.connect(my_db_file)
        conn.row_factory = sqlite3_dict_factory
    except Error as e:
        print(e)
    return conn

def sqlite3_updateObject(myDbFile, MyQuery, verbose=False) :
    if verbose :
        print("\n"+MyQuery)
     
    connexion = sqlite3_CreateConnexion(myDbFile) 
    cur = connexion.cursor()  
    
    try :
        cur.execute(MyQuery)
    
    except sqlite3.OperationalError as e :
        print()
        print("Erreur sqlite : probleme d execution sqlite3_updateObject")
        print(MyQuery)
        print(e)
        exit(0)    
        
    connexion.close()
    if verbose :
        print("Update Object Done")
        
 
def sqlite3_TableExists( myDbFile, myTable, verbose=False ) :    
    lQuery="""SELECT name FROM sqlite_master WHERE type='table' AND name='"""+myTable+"""' """
    return ( len( sqlite3_read2dictList(myDbFile, lQuery, verbose) ) != 0 ) 
        
def sqlite3_createTableFromcsvFile( myDbFile, MycsvFile, myTable, verbose=False ) :
        
    lQuery="""SELECT name FROM sqlite_master WHERE type='table' AND name='"""+myTable+"""' """
    rows = sqlite3_read2dictList(myDbFile, lQuery, verbose)
    
    if sqlite3_TableExists(myDbFile, myTable) :
        # Table existe pas besoin de la creer
        if verbose :
            print("Table existante pas besoin de creer") 
        return 
    
    with open(MycsvFile, 'r') as f :
        Lines = f.readlines() 
    
    if len(Lines) == 0 :
        return 

    print("Creation de la table : " + myTable ) 
    line = "'"+Lines[0].strip().replace(";","','")+"'"

    lQuery="Create Table if not exists "+myTable+" ( "     
    
    myDataSample=[]
    with open(MycsvFile, newline='') as csvfile:   
        reader = csv.DictReader(csvfile, delimiter=';')
        for idx, row in enumerate(reader) :
            if idx < 1000 :
                myDataSample.append(row)    
    
    for key in myDataSample[0].keys():
        myType="TEXT"
        for elem in myDataSample :
        
            if len(elem[key] ) != 0 :
                if elem[key].isdigit():
                   myType = "INT"
                elif elem[key].replace('.','',1).isdigit() and elem[key].count('.') < 2:
                   myType = "REAL"
                   
        lQuery=lQuery+ "'"+key.lower()+"'  "+myType + ", "
    
    lQuery=lQuery+   ");"  
    lQuery=lQuery.replace(", )"," )")
    # lQuery = lQuery.lower()
    
    sqlite3_updateObject(myDbFile, lQuery, verbose)
    


def sqlite3_loadcsvFile2Table( myDbFile, MycsvFile, myTable, verbose=False ) :

    with open (MycsvFile,'r') as f :
        MyList=f.readlines()    
        sqlite3_loadcsvList2Table( myDbFile, MyList, myTable, verbose )

    
def sqlite3_loadcsvList2Table( myDbFile, MyList, myTable, verbose=False, ignore=False ) :
    # verbose = True

    if verbose :
        print()
        
    if len(MyList) == 0 :
        ## Litse vide
        return 

    # Si la ligne 0 a plus de 90% de lettres : c'est un header
    alpha, string =0, MyList[0].lower().replace(';','').strip('\n')
    for i in string:
        if (i.isalpha()):
            alpha+=1
    if  alpha/len(string) > 0.90 :
        # print("Header found : " + MyList[0].lower())
        skipHeader = True
    else :
        skipHeader = False
    # exit(0)
    # header_keywords = [ 'iccid', 'bacth' , 'sncode', 'tmcode' , 'co_id', 'msisdn']
    # skipHeader = False
    # for val in header_keywords :
        # skipHeader = skipHeader or val in MyList[0].lower()
    
    if skipHeader and len(MyList) == 1 :
        ## Juste une ligne d en tetes
        return 
        
    connexion = sqlite3_CreateConnexion(myDbFile)    
    cur = connexion.cursor()
        
    for idx, line in enumerate(MyList) :
        if not ( skipHeader and  idx == 0 ) :
            if ignore :
                MyQuery="insert or ignore into "+myTable+" values ( '"+line.strip().replace(";","', '")+"') ;"
            else :
                MyQuery="insert  into "+myTable+" values ( '"+line.strip().replace(";","', '")+"') ;"
            if verbose :
                print("\n"+MyQuery)
            
            

            try :
                cur.execute(MyQuery)
            except sqlite3.OperationalError as e :
                print()
                print("Erreur sqlite : probleme d execution sqlite3_loadcsvList2Table")
                print(MyQuery)
                print(e)
                exit(0)
            # print(cur.rowcount)
            
    cur.execute("""commit  ;""")

    connexion.close()
    
    # print(str(idx+1-headerOffset)+" lignes chargees  dans " +myTable)
    
    if verbose :
        print("Commit Done")

def sqlite3_read2csvFile(myDbFile, MyQuery, MyFile, MyMode='w', verbose=False ) : 
    if verbose :
        print("\n"+MyQuery)
        
    rows = sqlite3_read2dictList(myDbFile, MyQuery,  verbose)

    if not os.path.isfile(MyFile):
        open (MyFile, 'w').close()
        
    if len(rows) == 0 or not os.path.isfile(MyFile):
        ## careate empty file
        with open (MyFile, 'a') :
            os.utime (MyFile, None)
            
    else : 
        with open(MyFile, MyMode ) as csvfile:
        
            fieldnames = rows[0].keys()
            myDialect=csv.unix_dialect
            myDialect.quoting=csv.QUOTE_NONE
            myDialect.delimiter=';'
            myDialect.lineterinator='\n'
            # myDialect.escapechar="'"
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, 
                dialect = myDialect )
            writer.writeheader()
            for row in rows :  
                writer.writerow(row)
                
            if verbose :
                print("Ecriture dans le ficheir : "+MyFile)

def sqlite3_read2display(myDbFile,  MyQuery, myMode='tsv',  verbose=False ) :

    rows = sqlite3_read2dictList(myDbFile, MyQuery,  verbose)
    
    if myMode == 'csv' :        
        print(*rows[0].keys(), sep=";")
        for row in rows :
            print(*row.values(), sep=";")
            
    elif myMode == 'ssv' :
        print(*rows[0].keys(), sep=",")
        for row in rows :
            print(*row.values(), sep=",")
    
    else :
        print(tabulate(rows, headers="keys", tablefmt=myMode, floatfmt=".3f"))
    
    return rows
    
    
     
def sqlite3_read2dictList(myDbFile, MyQuery, verbose=False ) :
    if verbose :
        print("\n"+MyQuery)
        
    connexion = sqlite3_CreateConnexion(myDbFile)    
    cur = connexion.cursor()

    
    try :
        cur.execute(MyQuery)
    
    except sqlite3.OperationalError as e :
        print()
        print("Erreur sqlite : probleme d execution sqlite3_read2dictList")
        print(MyQuery)
        print(e)
        exit(0)
        
    rows = cur.fetchall()    
    connexion.close()
    return rows

       
def sqlite3_updateData(myDbFile, MyQuery, verbose=False ) :

    if verbose :
        sqlite3_log_text("Debut")
        print(MyQuery)
        
    connexion = sqlite3_CreateConnexion(myDbFile)    
    cur = connexion.cursor()
    
    try :
        cur.execute(MyQuery)
        nbRows = cur.rowcount    
        cur.execute('commit  ;')
        
    except sqlite3.OperationalError as e :
        print()
        print("Erreur sqlite : probleme d execution sqlite3_updateData")
        print(MyQuery)
        print(e)
        exit(0)
            
   
    connexion.close()

    if verbose :
        print("Commit Done")
        if nbRows != 0 : 
            print("Lignes affectees :"+str(nbRows) + " , lors de l appel de "+sqlite3_myself())   
        sqlite3_log_text("Fin") 
       
    return nbRows

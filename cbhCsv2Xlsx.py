#!/usr/bin/env python
# -*- coding: utf-8 -*-

#!/usr/bin/python3
import getopt, sys, os,  time
# from openpyxl.styles import Color, PatternFill, Font, Border
# from openpyxl.styles.borders import Border, Side
# from openpyxl import Workbook
from tabulate import tabulate
import xlsxwriter
import errno

from cbhComm     import *



def get_value(value) :
    number_format   = ''    
    int_val         = None
    try :
        int_val = int(value)
        number_format = '#0'  
        value = int_val   
    except ValueError as e :
        pass         
    if int_val is None : 
        float_val       = None
        try :
            float_val = float(value.replace(',','.'))
            number_format = '# ### ##0.000' 
            value = float_val       
        except ValueError as e :
            pass       
    return value, number_format
 
def getLinesAnalysis( mySplitLines , myAltColorIndex) :

    ## Type de ligne
    format_list     = []
    for i, line in enumerate(mySplitLines) :
        fmt={'index':0, 'nbCol':0, 'vide':True, 'prevNbCol':-1, 'colType':'',
        'idxValue':'', 'idxPrevValue':'', 'idxCol':''}        
        fmt['index'] = i
        fmt['nbCol'] = int(len(line))
        if i > 0 :
            fmt['prevNbCol']  = format_list[i-1]['nbCol'] 
        fmt['vide']  = (len(line[0]) == 0)
        if fmt['nbCol'] > 1 :
            if fmt['prevNbCol'] <= 1 :
                fmt['colType']='Header'
            else :                
                fmt['colType']='Data'  
        if fmt['nbCol'] == 1 :
            if fmt['vide'] :
                fmt['colType']='Vide'
            else  :
                fmt['colType']='Rem'
                
        if myAltColorIndex != -1 and fmt['colType'] == 'Data' :                
            fmt['idxValue']     = line[myAltColorIndex-1]
            fmt['idxPrevValue'] = format_list[i-1]['idxValue']
            if fmt['idxValue'] != '' and fmt['idxPrevValue'] == '' :
                fmt['idxCol'] = 1           
            if fmt['idxValue'] == fmt['idxPrevValue']  :
                fmt['idxCol'] = format_list[i-1]['idxCol']
            else :
                if format_list[i-1]['idxCol'] == 1 :
                    fmt['idxCol'] = 2 
                else :
                    fmt['idxCol'] = 1                      
        format_list.append(fmt)
        
    # print(format_list)
    # print(tabulate(format_list, headers='keys', tablefmt='csv', floatfmt=".3f"))
    
    return format_list
 
 
def applyFormatToWorksheet(worksheet, mySplitLines, format_list, workbook_formats, config) :

    for i, line in enumerate(mySplitLines) :
        # print(line)
        # print(format_list[i])
        # for j, item in enumerate(line) :
            # value, number_format = get_value(item)
            # if number_format == '#0' : 
                # worksheet.write(i, j,     value, int_format)
            # if number_format == '# ### ##0.000' : 
                # worksheet.write(i, j,     value, float_format)
        
        if format_list[i]['colType'] == 'Rem' :
            worksheet.write(i, 0,     line[0] )
            
        if format_list[i]['colType'] == 'Header' :
            for j, item in enumerate(line ) : 
                value, number_format = get_value(item)
                worksheet.write(i, j,     value, workbook_formats['header_format_blue'])
                
        if format_list[i]['colType'] == 'Data' :
            for j, item in enumerate(line ) : 
                value, number_format = get_value(item)
                # value = item
                if format_list[i]['idxCol'] == 2 :
                    worksheet.write(i, j,     value, workbook_formats['data_format_alt_blue'])
                else : 
                    worksheet.write(i, j,     value, workbook_formats['data_format_basic'])                
            # hlinkList=[]
            for j in config['hlinkList'] :
                value, number_format = get_value(line[j-1])
                worksheet.write(i, j-1,     value, workbook_formats['data_format_hlink']) 

def add_csvFile_to_ExcelWB( csvFile, workbook, workbook_formats, config ) :
    
    splitLines=[]
    with open(csvFile, "r") as f :
        Lines = f.readlines()
        for line in Lines :
            splitLines.append(line.strip().split(';'))
            
    ## Type de ligne
    format_list = getLinesAnalysis( splitLines , config['altColorIndex'])
    
    sheetname = os.path.basename(csvFile).replace( '.csv', '')
    if os_sgrep_match( sheetname, "^[0-9]{1,}_") :
        sheetname = sheetname[3:]
    # print(sheetname)        
    # exit(0)
    worksheet = workbook.add_worksheet(sheetname)
    applyFormatToWorksheet(worksheet, splitLines, format_list, workbook_formats , config)
    
    if config['auto_fit'] :
        worksheet.autofit()   
        
    if config['freezeCell'] != [] :  
        worksheet.freeze_panes(freezeCell[0],freezeCell[1])
 
def csvPath_to_xlsx(myInPath, myAutoFit=True, myAltColorIndex=-1, hlinkList=[], freezeCell=[]) :

    if not os.path.exists(myInPath) : 
        print("Path not found : "+myInPath)
        exit(0)
    
    config={'auto_fit' : myAutoFit, 'altColorIndex': myAltColorIndex, 'hlinkList': hlinkList,  'freezeCell' : freezeCell}
    # print(config)

    if os.path.isfile(myInPath) :
        myOutFile = myInPath.replace('.csv', '.xlsx')
        csvFiles = [ myInPath ]
    
    if os.path.isdir(myInPath) :    
        myOutFile = myInPath+"/"+os.path.basename(myInPath)+".xlsx"
        csvFiles = os_find(myInPath, "*.csv", verbose=False)
        
    workbook = xlsxwriter.Workbook(myOutFile)    
    ## WorkBook Formats
    workbook_formats={
    'int_format' : workbook.add_format({'num_format': '#0'}),
    'float_format' : workbook.add_format({'num_format': '# ### ##0.000'}),
    'data_format_basic' : workbook.add_format({'border':1}),
    'data_format_alt_blue'  : workbook.add_format({'border':1,'bg_color':'#DCE6F1'}),
    'data_format_hlink' : workbook.add_format({'border':1,'underline':True,'font_color':  '#0000FF'}),
    'header_format_blue' : workbook.add_format({'bold': True, 'bg_color':  '#9BC2E6', 'border':1 } ),
    'header_format_olive_green' : workbook.add_format({'bold': True, 'bg_color':  '#64a331', 'border':1}),
    }
    # print(workbook_formats)
    
    for wk in workbook_formats :
        # workbook_formats[wk].set_font_name("Calibri")
        # workbook_formats[wk].set_font_size(11)
        workbook_formats[wk].set_align('top')
        
    # exit(0)
    
    for csvFile in csvFiles: 
        print("csvxsxl:"+csvFile)
        add_csvFile_to_ExcelWB( csvFile, workbook, workbook_formats, config )
    
    print("Ficheir xlsx produit :" + myOutFile)        
    
    wait_for_excel(myOutFile)
    workbook.close()   

def usage():
    print("help help")
    
def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "d:f:s:hv", ["help", "output="])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(err)  # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
    verbose = False
    inputfile = None
    sheetname = None
    colorise_hl=False
    for o, a in opts:
        if o == "-v":
            verbose = True
        elif o in ("-h", "--help"):
            usage()
            sys.exit(0)
        elif o in ("-c", "--colorise-HL"):
            colorise_hl = True
        elif o in ("-f", "--inputfile"):
            inputfile = a
        elif o in ("-s", "--sheetname"):
            sheetname = a
            
        else:
            assert False, "unhandled option"
    # ...
    if sheetname is None or sheetname == '' :    
        sheetname = os.path.basename(os.path.splitext(inputfile)[0]) 
        
    csvReport_to_xlsx(inputfile, inputfile.replace('.csv','.xlsx'), sheetname, colorise_hl, codisindex)
    
if __name__ == "__main__":
    main()



from termcolor import colored
import sys
import os
from stat import *
import time
from threading import Thread
from HTMLParser import HTMLParser
from lxml import etree
import lxml.html
from lxml import html
import requests
from sets import Set
import re
import codecs
from django.utils.encoding import smart_str, smart_unicode
import difflib
from bs4 import BeautifulSoup
import urllib2
import xlsxwriter



def datasetGenerator():
    #-------------DatasetGenerator-------------------#
    #----------Step : 1	Taking User Input----------------#
    print(colored("\n\n\n DATASET GENERATOR	:	START \n\n\n",'yellow', attrs=['bold']))
    print(colored("\n\nSelect The Algorithm to run	: \n",'magenta', attrs=['bold']))
    print(colored( "-----------------------------------------------------------------\n",'cyan', attrs=['bold']))
    print(colored("BoilerPipe	: 1\n",'red', attrs=['bold']))
    print(colored("VIPS	: 2\n",'red', attrs=['bold']))
    print(colored("Block O Matic	: 3\n",'red', attrs=['bold']))
    print(colored("Gomory Hu Based	: 4\n",'red', attrs=['bold']))
    print(colored("To Quit	: 7\n",'red', attrs=['bold']))
    algo_type=input('\nEnter algorithm type	: ')
    print (colored("\nType Of Algorithm Entered	: "+str(algo_type),'green', attrs=['bold'])) 
    print(colored("\n\nSelect The dataset to evaluate algorithm	: \n",'magenta', attrs=['bold']))
    print (colored("-----------------------------------------------------------------\n",'cyan', attrs=['bold']))
    print(colored("Random Dataset	: 1\n",'red', attrs=['bold']))
    print(colored("Popular Dataset	: 2\n",'red', attrs=['bold']))
    dataset_type=input('\nEnter dataset type	: ')
    print (colored("\nType Of Dataset Entered	: "+ str(dataset_type),'green', attrs=['bold'])) 
    current_directory=os.getcwd()
    if algo_type==1 or algo_type==2 or algo_type==3 or algo_type==4 :
      #----------Step : 2	Getting dataset specific mapping.txt----------------#
      if dataset_type==1 :
	dataset_location=current_directory+"/dataset-random/"
      elif dataset_type==2 :
	dataset_location=current_directory+"/dataset-popular/"
      print (colored("\nGetting dataset location . . . .  ",'green', attrs=['bold'])) 
      with open(dataset_location+'mapping.txt', 'r') as f:
	lineArr=f.read().split(',')
      for i in range(0,len(lineArr)) :
	lineArr[i]=str(lineArr[i]).replace('\n','')
      lineArr.remove(lineArr[len(lineArr)-1])
      print (colored("\nPreprocessing mapping.txt . . . . ",'green', attrs=['bold'])) 
      
      for eachLine in lineArr :
	l=eachLine.split(':')
	
	webURL=str(l[0]+":"+l[1]).replace('"','')
	webURL=webURL[:len(webURL)-2]
	
	absoluteURL=l[-1].replace('"','').replace(' ','')
	
	URLDict[webURL]=absoluteURL
	GroundTruthDict[webURL]=absoluteURL.replace("index.html","index.blocks.html")
      print (colored("\nPopulating URLDict and GroundTruthDict . def evaluator() :. . .  ",'green', attrs=['bold'])) 
      print(colored("\n\n\n DATASET GENERATOR	:	END \n\n\n",'yellow', attrs=['bold']))
    return URLDict , GroundTruthDict , algo_type , dataset_type

def evaluator(GeneratedBlocksSet , GroundTruthBlocksSet ) :
      Retrieved_blocks_Algo=len(GeneratedBlocksSet[k])
      print (colored("No of retrieved blocks by algorithm ------> \t"+str(Retrieved_blocks_Algo)+"\n",'green', attrs=['bold']))
      Relevant_blocks_GT=len(GroundTruthBlocksSet[k])
      print (colored("No of relevant blocks by ground truth ------> \t"+str(Relevant_blocks_GT)+"\n",'green', attrs=['bold']))
      print (colored("Calculating HITS : Exact Match Metric . . . . \n",'green', attrs=['bold']))
      Hit_exact_match_metric=len(GeneratedBlocksSet[k].intersection(GroundTruthBlocksSet[k]))
      print (colored("No of correctly segmented blocks by algorithm (HITS Exact) ------> \t"+str(Hit_exact_match_metric)+"\n",'green', attrs=['bold']))
      
      print (colored("Calculating HITS : Fuzzy Match Metric . . . . \n",'green', attrs=['bold']))
      Hit_fuzzy_match_metric=0
      for xx in GeneratedBlocksSet[k] :
	for yy in GroundTruthBlocksSet[k] :
	  per=difflib.SequenceMatcher(None,xx,yy).ratio()
	  if per >=0.8 :
	    Hit_fuzzy_match_metric=Hit_fuzzy_match_metric+1
      print (colored("No of correctly segmented blocks by algorithm (HITS Fuzzy) ------> \t"+str(Hit_fuzzy_match_metric)+"\n",'green', attrs=['bold']))
      print(colored("Calculating statistics . . . . \n",'yellow', attrs=['bold']))
      recall_exact = float(Hit_exact_match_metric) / float(Relevant_blocks_GT)
      recall_fuzzy = float(Hit_fuzzy_match_metric) / float(Relevant_blocks_GT)
      if Retrieved_blocks_Algo!=0 :
	precision_exact = float(Hit_exact_match_metric) / float(Retrieved_blocks_Algo)
	fscore_exact = 2 * (float(precision_exact * recall_exact) / float(precision_exact + recall_exact))
	precision_fuzzy = float(Hit_fuzzy_match_metric) / float(Retrieved_blocks_Algo)
	fscore_fuzzy = 2 * (float(precision_fuzzy * recall_fuzzy) / float(precision_fuzzy + recall_fuzzy))
      else :
	precision_exact=0
	fscore_exact=0
	precision_fuzzy=0
	fscore_fuzzy=0   
      
      print (colored("Precision Exact ------> \t"+str(precision_exact)+"\n",'green', attrs=['bold']))
      print (colored("Recall Exact ------> \t"+str(recall_exact)+"\n",'green', attrs=['bold']))
      print (colored("F-Score Exact ------> \t"+str(fscore_exact)+"\n",'green', attrs=['bold']))
      print (colored("Precision Fuzzy ------> \t"+str(precision_fuzzy)+"\n",'green', attrs=['bold']))
      print (colored("Recall Fuzzy ------> \t"+str(recall_fuzzy)+"\n",'green', attrs=['bold']))
      print (colored("F-Score Fuzzy ------> \t"+str(fscore_fuzzy)+"\n",'green', attrs=['bold']))
      return Hit_exact_match_metric,Hit_fuzzy_match_metric,precision_exact,precision_fuzzy,recall_exact,recall_fuzzy,Relevant_blocks_GT,Retrieved_blocks_Algo,fscore_exact,fscore_fuzzy
  
def output(row,worksheet,algo_name,avg_Retrieved_blocks_Algo,avg_Relevant_blocks_GT,avg_Hit_exact_match_metric,avg_precision_exact,avg_recall_exact,avg_fscore_exact,avg_Hit_fuzzy_match_metric,avg_precision_fuzzy,avg_recall_fuzzy,avg_fscore_fuzzy) :
  col=0
  worksheet.write_string  (row, col,     algo_name              )
  worksheet.write_number(row, col + 1,avg_Retrieved_blocks_Algo)
  worksheet.write_number(row, col + 2,avg_Relevant_blocks_GT)
  worksheet.write_number(row, col + 3,avg_Hit_exact_match_metric)
  worksheet.write_number(row, col + 4,avg_precision_exact)
  worksheet.write_number(row, col + 5,avg_recall_exact)
  worksheet.write_number(row, col + 6,avg_fscore_exact)
  worksheet.write_number(row, col + 7,avg_Hit_fuzzy_match_metric)
  worksheet.write_number(row, col + 8,avg_precision_fuzzy)
  worksheet.write_number(row, col + 9,avg_recall_fuzzy)
  worksheet.write_number(row, col + 10,avg_fscore_fuzzy)
  
  
 
if __name__ == '__main__':
  current_directory=os.getcwd()
  srcPath=current_directory
  sum_Retrieved_blocks_Algo=0
  sum_Relevant_blocks_GT=0
  sum_Hit_exact_match_metric=0
  sum_Hit_fuzzy_match_metric=0
  sum_precision_exact=0
  sum_recall_exact=0
  sum_fscore_exact=0
  sum_precision_fuzzy=0
  sum_recall_fuzzy=0
  sum_fscore_fuzzy=0

  avg_Retrieved_blocks_Algo=0
  avg_Relevant_blocks_GT=0
  avg_Hit_exact_match_metric=0
  avg_Hit_fuzzy_match_metric=0
  avg_precision_exact=0
  avg_recall_exact=0
  avg_fscore_exact=0
  avg_precision_fuzzy=0
  avg_recall_fuzzy=0
  avg_fscore_fuzzy=0
  
  
  
  
  row = 0
  
  # Create a workbook and add a worksheet.
  workbook = xlsxwriter.Workbook(current_directory+'/Output/StatisticalResults.xlsx')
  worksheet = workbook.add_worksheet()

  # Add a bold format to use to highlight cells.
  bold = workbook.add_format({'bold': 1})
  # Adjust the column width.
  worksheet.set_column(0, 10, 20)

  # Write some data headers.
  worksheet.write('A1', 'Algorithm', bold)
  worksheet.write('B1', 'Retrieved Blocks', bold)
  worksheet.write('C1', 'Relevant Blocks', bold)
  worksheet.write('D1', 'HIT Exact', bold)
  worksheet.write('E1', 'Precision Exact', bold)
  worksheet.write('F1', 'Recall Exact', bold)
  worksheet.write('G1', 'F-Score Exact', bold)
  worksheet.write('H1', 'HIT Fuzzy', bold)
  worksheet.write('I1', 'Precision Fuzzy', bold)
  worksheet.write('J1', 'Recall Fuzzy', bold)
  worksheet.write('K1', 'F-Score Fuzzy', bold)
  while True :
    URLDict={}
    GroundTruthDict={}
    
    GroundTruthBlocksSet={}
    GeneratedBlocksSet={}
    textBlockSet1=Set()
    textBlockSet2=Set()
    URLDict , GroundTruthDict , algo_type , dataset_type = datasetGenerator()
    #-------------------------------------------AlgorithmDriver------------------------------------------#
    print(colored("\n\n\n Test Framework	:	START \n\n\n",'yellow', attrs=['bold']))
    #-------------------------------------------AlgorithmDriver : BlockFusion------------------------------------------#
    if algo_type==1 : 
      i=0
      for k, v in URLDict.iteritems():
	print "---------------------------------ITERATION START		:	"+str(i)+"---------------------------------------------"
	print
	#------------------Execute BlockFusion jar file-----------------#
	print (colored("Executing BlockFusion python file . . . . \n",'green', attrs=['bold']))
	GeneratedBlocksSet[k]=BlockFusion.segmentPage(str(v))
	print(colored("\n\n\n BLOCK MAPPER	:	START \n\n\n",'yellow', attrs=['bold']))
	#-----------------Parse The Output : GeneratedBlocks Extraction-----------------------------------------#
	
	print (colored("Parsing the output . . . . \n",'green', attrs=['bold']))
	print (colored("Generating text serialized version of Generated and GroundTruth Blocks . . . . \n",'green', attrs=['bold']))
	
        #-----------------Parse The GroundTruth : GroundTruthBlocks Extraction-----------------------------------------#
	html_block=lxml.html.parse(str(GroundTruthDict[k]))
	for node in html_block.iter() :
	  block=node.xpath('//*[@data-block]')
	for r in block :
	  textBlock=r.text_content()
	  s=re.sub(r"\W", "", textBlock)
	  textBlockSet2.add(s)
	GroundTruthBlocksSet[k]=textBlockSet2
	print(colored("\n\n\n BLOCK MAPPER	:	END \n\n\n",'yellow', attrs=['bold']))
	#-------------------------------------------Evaluator------------------------------------------#
	print(colored("\n\n\n Evaluator	:	START \n\n\n",'yellow', attrs=['bold']))
	Hit_exact_match_metric,Hit_fuzzy_match_metric,precision_exact,precision_fuzzy,recall_exact,recall_fuzzy,Relevant_blocks_GT,Retrieved_blocks_Algo,fscore_exact,fscore_fuzzy=evaluator(GeneratedBlocksSet , GroundTruthBlocksSet)
	print(colored("Calculating averages . . . . \n",'yellow', attrs=['bold']))
	sum_Hit_exact_match_metric=sum_Hit_exact_match_metric+Hit_exact_match_metric
	sum_Hit_fuzzy_match_metric=sum_Hit_fuzzy_match_metric+Hit_fuzzy_match_metric
	sum_precision_exact=sum_precision_exact+precision_exact
	sum_precision_fuzzy=sum_precision_fuzzy+precision_fuzzy
	sum_recall_exact=sum_recall_exact+recall_exact
	sum_recall_fuzzy=sum_recall_fuzzy+recall_fuzzy
	sum_Relevant_blocks_GT=sum_Relevant_blocks_GT+Relevant_blocks_GT
	sum_Retrieved_blocks_Algo=sum_Retrieved_blocks_Algo+Retrieved_blocks_Algo
	sum_fscore_exact=sum_fscore_exact+fscore_exact
	sum_fscore_fuzzy=sum_fscore_fuzzy+fscore_fuzzy
	time.sleep(4)
	print "---------------------------------ITERATION END		:	"+str(i)+"---------------------------------------------"
	print
	print
	i=i+1
      avg_Hit_exact_match_metric=float(sum_Hit_exact_match_metric) / len(URLDict)
      avg_Hit_fuzzy_match_metric=float(sum_Hit_fuzzy_match_metric) / len(URLDict)
      avg_precision_exact=float(sum_precision_exact) / len(URLDict)
      avg_precision_fuzzy=float(sum_precision_fuzzy) / len(URLDict)
      avg_recall_exact=float(sum_recall_exact) / len(URLDict)
      avg_recall_fuzzy=float(sum_recall_fuzzy) / len(URLDict)
      avg_Relevant_blocks_GT=float(sum_Relevant_blocks_GT) / len(URLDict)
      avg_Retrieved_blocks_Algo=float(sum_Retrieved_blocks_Algo) / len(URLDict)
      avg_fscore_exact= float(sum_fscore_exact) / len(URLDict)
      avg_fscore_fuzzy= float(sum_fscore_fuzzy) / len(URLDict)
      
      print (colored("Avg Retrieved Blocks ------> \t"+str(avg_Retrieved_blocks_Algo)+"\n",'green', attrs=['bold']))
      print (colored("Avg Relevant Blocks ------> \t"+str(avg_Relevant_blocks_GT)+"\n",'green', attrs=['bold']))
      print (colored("Avg HIT Exact ------> \t"+str(avg_Hit_exact_match_metric)+"\n",'green', attrs=['bold']))
      print (colored("Avg Precision Exact ------> \t"+str(avg_precision_exact)+"\n",'green', attrs=['bold']))
      print (colored("Avg Recall Exact ------> \t"+str(avg_recall_exact)+"\n",'green', attrs=['bold']))
      print (colored("Avg F-Score Exact ------> \t"+str(avg_fscore_exact)+"\n",'green', attrs=['bold']))
      print (colored("Avg HIT Fuzzy ------> \t"+str(avg_Hit_fuzzy_match_metric)+"\n",'green', attrs=['bold']))
      print (colored("Avg Precision Fuzzy ------> \t"+str(avg_precision_fuzzy)+"\n",'green', attrs=['bold']))
      print (colored("Avg Recall Fuzzy ------> \t"+str(avg_recall_fuzzy)+"\n",'green', attrs=['bold']))
      print (colored("Avg F-Score Fuzzy ------> \t"+str(avg_fscore_fuzzy)+"\n",'green', attrs=['bold']))
      print(colored("\n\n\n Evaluator	:	END \n\n\n",'yellow', attrs=['bold']))
      print(colored("\n\n\n Writing StatisticalResults to Xls File . . . .\n\n\n",'yellow', attrs=['bold']))
      row=row+1
      output(row,worksheet,"BlockFusion",avg_Retrieved_blocks_Algo,avg_Relevant_blocks_GT,avg_Hit_exact_match_metric,avg_precision_exact,avg_recall_exact,avg_fscore_exact,avg_Hit_fuzzy_match_metric,avg_precision_fuzzy,avg_recall_fuzzy,avg_fscore_fuzzy )
    
    #-------------------------------------------AlgorithmDriver : VIPS------------------------------------------#   
    elif algo_type==2:
      i=0
      for k, v in URLDict.iteritems():
	print "---------------------------------ITERATION START		:	"+str(i)+"---------------------------------------------"
	print
	#------------------Execute VIPS jar file-----------------#
	print (colored("Executing VIPS runnable jar file . . . . \n",'green', attrs=['bold']))
	os.system("java -jar VIPS.jar "+str(k))
	print (colored("Copying the output to /Output directory . . . . \n",'green', attrs=['bold']))
	src=current_directory
	for f in os.listdir(src):
	  if f[-3:] == "xml":
	    pathname = os.path.join(src, f)
	    mode = os.stat(pathname)[ST_MODE]
	    destPath=current_directory+"/Output/VIPS/"
	    os.system("mv  "+pathname+"	"+destPath)
			
	print(colored("\n\n\n BLOCK MAPPER	:	START \n\n\n",'yellow', attrs=['bold']))
	#-----------------Parse The Output : GeneratedBlocks Extraction-----------------------------------------#
	
	print (colored("Parsing the output . . . . \n",'green', attrs=['bold']))
	print (colored("Generating text serialized version of Generated and GroundTruth Blocks . . . . \n",'green', attrs=['bold']))
	doc = etree.parse(destPath+"/VIPSResult.xml")
	parser = HTMLParser()
	# Get the Blocks
	for node in doc.getroot():
	  ssrc=''
	  for child in node.getchildren() :
	      if  child.getchildren() :
		for c in child.getchildren() :
		  src= ""
		  if  c.getchildren() :
		    for cc in c.getiterator() :
		      src=smart_str(src)+smart_str(cc.get('SRC'))
		  else :
		    src=smart_str(c.get('SRC'))
		  
		  ssrc=src
		  block=lxml.html.fromstring(ssrc)
		  textBlock=block.text_content()
		  s=re.sub(r"\W", "", textBlock)
		  textBlockSet1.add(s)
		 
	      else :
		ssrc=smart_str(child.get('SRC'))
		block=lxml.html.fromstring(ssrc)
		textBlock=smart_str(block.text_content())
		s=re.sub(r"\W", "", textBlock)
		textBlockSet1.add(s)
		
      #-----------------Parse The GroundTruth : GroundTruthBlocks Extraction-----------------------------------------#
	html_block=lxml.html.parse(str(GroundTruthDict[k]))
	for node in html_block.iter() :
	  block=node.xpath('//*[@data-block]')
	for r in block :
	  textBlock=r.text_content()
	  s=re.sub(r"\W", "", textBlock)
	  textBlockSet2.add(s)
	GroundTruthBlocksSet[k]=textBlockSet2
	GeneratedBlocksSet[k]=textBlockSet1
	print "Printing GeneratedBlocksSet . . . . "
	print(colored("\n\n\n BLOCK MAPPER	:	END \n\n\n",'yellow', attrs=['bold']))
	#-------------------------------------------Evaluator------------------------------------------#
	print(colored("\n\n\n Evaluator	:	START \n\n\n",'yellow', attrs=['bold']))
	Hit_exact_match_metric,Hit_fuzzy_match_metric,precision_exact,precision_fuzzy,recall_exact,recall_fuzzy,Relevant_blocks_GT,Retrieved_blocks_Algo,fscore_exact,fscore_fuzzy=evaluator(GeneratedBlocksSet , GroundTruthBlocksSet)
	print(colored("Calculating averages . . . . \n",'yellow', attrs=['bold']))
	sum_Hit_exact_match_metric=sum_Hit_exact_match_metric+Hit_exact_match_metric
	sum_Hit_fuzzy_match_metric=sum_Hit_fuzzy_match_metric+Hit_fuzzy_match_metric
	sum_precision_exact=sum_precision_exact+precision_exact
	sum_precision_fuzzy=sum_precision_fuzzy+precision_fuzzy
	sum_recall_exact=sum_recall_exact+recall_exact
	sum_recall_fuzzy=sum_recall_fuzzy+recall_fuzzy
	sum_Relevant_blocks_GT=sum_Relevant_blocks_GT+Relevant_blocks_GT
	sum_Retrieved_blocks_Algo=sum_Retrieved_blocks_Algo+Retrieved_blocks_Algo
	sum_fscore_exact=sum_fscore_exact+fscore_exact
	sum_fscore_fuzzy=sum_fscore_fuzzy+fscore_fuzzy
	time.sleep(4)
	print "---------------------------------ITERATION END		:	"+str(i)+"---------------------------------------------"
	print
	print
	i=i+1
      avg_Hit_exact_match_metric=float(sum_Hit_exact_match_metric) / len(URLDict)
      avg_Hit_fuzzy_match_metric=float(sum_Hit_fuzzy_match_metric) / len(URLDict)
      avg_precision_exact=float(sum_precision_exact) / len(URLDict)
      avg_precision_fuzzy=float(sum_precision_fuzzy) / len(URLDict)
      avg_recall_exact=float(sum_recall_exact) / len(URLDict)
      avg_recall_fuzzy=float(sum_recall_fuzzy) / len(URLDict)
      avg_Relevant_blocks_GT=float(sum_Relevant_blocks_GT) / len(URLDict)
      avg_Retrieved_blocks_Algo=float(sum_Retrieved_blocks_Algo) / len(URLDict)
      avg_fscore_exact= float(sum_fscore_exact) / len(URLDict)
      avg_fscore_fuzzy= float(sum_fscore_fuzzy) / len(URLDict)
      
      print (colored("Avg Retrieved Blocks ------> \t"+str(avg_Retrieved_blocks_Algo)+"\n",'green', attrs=['bold']))
      print (colored("Avg Relevant Blocks ------> \t"+str(avg_Relevant_blocks_GT)+"\n",'green', attrs=['bold']))
      print (colored("Avg HIT Exact ------> \t"+str(avg_Hit_exact_match_metric)+"\n",'green', attrs=['bold']))
      print (colored("Avg Precision Exact ------> \t"+str(avg_precision_exact)+"\n",'green', attrs=['bold']))
      print (colored("Avg Recall Exact ------> \t"+str(avg_recall_exact)+"\n",'green', attrs=['bold']))
      print (colored("Avg F-Score Exact ------> \t"+str(avg_fscore_exact)+"\n",'green', attrs=['bold']))
      print (colored("Avg HIT Fuzzy ------> \t"+str(avg_Hit_fuzzy_match_metric)+"\n",'green', attrs=['bold']))
      print (colored("Avg Precision Fuzzy ------> \t"+str(avg_precision_fuzzy)+"\n",'green', attrs=['bold']))
      print (colored("Avg Recall Fuzzy ------> \t"+str(avg_recall_fuzzy)+"\n",'green', attrs=['bold']))
      print (colored("Avg F-Score Fuzzy ------> \t"+str(avg_fscore_fuzzy)+"\n",'green', attrs=['bold']))
      print(colored("\n\n\n Evaluator	:	END \n\n\n",'yellow', attrs=['bold']))
      print(colored("\n\n\n Writing StatisticalResults to Xls File . . . .\n\n\n",'yellow', attrs=['bold']))
      row=row+1
      output(row,worksheet,"VIPS",avg_Retrieved_blocks_Algo,avg_Relevant_blocks_GT,avg_Hit_exact_match_metric,avg_precision_exact,avg_recall_exact,avg_fscore_exact,avg_Hit_fuzzy_match_metric,avg_precision_fuzzy,avg_recall_fuzzy,avg_fscore_fuzzy )
    
  
    #-------------------------------------------AlgorithmDriver : BlockOMatic------------------------------------------#
    elif algo_type==3: 
      i=0
      for k, v in URLDict.iteritems():
	print "---------------------------------ITERATION START		:	"+str(i)+"---------------------------------------------"
	print
	#------------------Execute BlockOMatic jar file-----------------#
	print (colored("Executing BlockOMatic runnable jar file . . . . \n",'green', attrs=['bold']))
	os.system(" java -jar BlockOMatic.jar  -browser firefox -get segmentation -verbose true -url "+str(k))
	print (colored("Copying the output to /Output directory . . . . \n",'green', attrs=['bold']))
	src=current_directory
	for f in os.listdir(src):
	  if f[-3:] == "xml":
	    pathname = os.path.join(src, f)
	    mode = os.stat(pathname)[ST_MODE]
	    destPath=current_directory+"/Output/BLOCKOMATIC/"
	    os.system("mv  "+pathname+"	"+destPath)
			
	print(colored("\n\n\n BLOCK MAPPER	:	START \n\n\n",'yellow', attrs=['bold']))
	#-----------------Parse The Output : GeneratedBlocks Extraction-----------------------------------------#
	
	print (colored("Parsing the output . . . . \n",'green', attrs=['bold']))
	print (colored("Generating text serialized version of Generated and GroundTruth Blocks . . . . \n",'green', attrs=['bold']))
	doc = etree.parse(destPath+"/blocks.xml")
	parser = HTMLParser()
	# Get the Blocks
	for node in doc.getroot():
	  for child in node.getchildren() :
	    for cc in child.getchildren() :
	      src=smart_str(cc.get('ObjectRectText'))
	      s=re.sub(r"\W", "", src)
	      textBlockSet1.add(s)
		
      #-----------------Parse The GroundTruth : GroundTruthBlocks Extraction-----------------------------------------#
	html_block=lxml.html.parse(str(GroundTruthDict[k]))
	for node in html_block.iter() :
	  block=node.xpath('//*[@data-block]')
	for r in block :
	  textBlock=r.text_content()
	  s=re.sub(r"\W", "", textBlock)
	  textBlockSet2.add(s)
	GroundTruthBlocksSet[k]=textBlockSet2
	GeneratedBlocksSet[k]=textBlockSet1
	print(colored("\n\n\n BLOCK MAPPER	:	END \n\n\n",'yellow', attrs=['bold']))
	#-------------------------------------------Evaluator------------------------------------------#
	print(colored("\n\n\n Evaluator	:	START \n\n\n",'yellow', attrs=['bold']))
	Hit_exact_match_metric,Hit_fuzzy_match_metric,precision_exact,precision_fuzzy,recall_exact,recall_fuzzy,Relevant_blocks_GT,Retrieved_blocks_Algo,fscore_exact,fscore_fuzzy=evaluator(GeneratedBlocksSet , GroundTruthBlocksSet)
	print(colored("Calculating averages . . . . \n",'yellow', attrs=['bold']))
	sum_Hit_exact_match_metric=sum_Hit_exact_match_metric+Hit_exact_match_metric
	sum_Hit_fuzzy_match_metric=sum_Hit_fuzzy_match_metric+Hit_fuzzy_match_metric
	sum_precision_exact=sum_precision_exact+precision_exact
	sum_precision_fuzzy=sum_precision_fuzzy+precision_fuzzy
	sum_recall_exact=sum_recall_exact+recall_exact
	sum_recall_fuzzy=sum_recall_fuzzy+recall_fuzzy
	sum_Relevant_blocks_GT=sum_Relevant_blocks_GT+Relevant_blocks_GT
	sum_Retrieved_blocks_Algo=sum_Retrieved_blocks_Algo+Retrieved_blocks_Algo
	sum_fscore_exact=sum_fscore_exact+fscore_exact
	sum_fscore_fuzzy=sum_fscore_fuzzy+fscore_fuzzy
	time.sleep(4)
	print "---------------------------------ITERATION END		:	"+str(i)+"---------------------------------------------"
	print
	print
	i=i+1
      avg_Hit_exact_match_metric=float(sum_Hit_exact_match_metric) / len(URLDict)
      avg_Hit_fuzzy_match_metric=float(sum_Hit_fuzzy_match_metric) / len(URLDict)
      avg_precision_exact=float(sum_precision_exact) / len(URLDict)
      avg_precision_fuzzy=float(sum_precision_fuzzy) / len(URLDict)
      avg_recall_exact=float(sum_recall_exact) / len(URLDict)
      avg_recall_fuzzy=float(sum_recall_fuzzy) / len(URLDict)
      avg_Relevant_blocks_GT=float(sum_Relevant_blocks_GT) / len(URLDict)
      avg_Retrieved_blocks_Algo=float(sum_Retrieved_blocks_Algo) / len(URLDict)
      avg_fscore_exact= float(sum_fscore_exact) / len(URLDict)
      avg_fscore_fuzzy= float(sum_fscore_fuzzy) / len(URLDict)
      
      print (colored("Avg Retrieved Blocks ------> \t"+str(avg_Retrieved_blocks_Algo)+"\n",'green', attrs=['bold']))
      print (colored("Avg Relevant Blocks ------> \t"+str(avg_Relevant_blocks_GT)+"\n",'green', attrs=['bold']))
      print (colored("Avg HIT Exact ------> \t"+str(avg_Hit_exact_match_metric)+"\n",'green', attrs=['bold']))
      print (colored("Avg Precision Exact ------> \t"+str(avg_precision_exact)+"\n",'green', attrs=['bold']))
      print (colored("Avg Recall Exact ------> \t"+str(avg_recall_exact)+"\n",'green', attrs=['bold']))
      print (colored("Avg F-Score Exact ------> \t"+str(avg_fscore_exact)+"\n",'green', attrs=['bold']))
      print (colored("Avg HIT Fuzzy ------> \t"+str(avg_Hit_fuzzy_match_metric)+"\n",'green', attrs=['bold']))
      print (colored("Avg Precision Fuzzy ------> \t"+str(avg_precision_fuzzy)+"\n",'green', attrs=['bold']))
      print (colored("Avg Recall Fuzzy ------> \t"+str(avg_recall_fuzzy)+"\n",'green', attrs=['bold']))
      print (colored("Avg F-Score Fuzzy ------> \t"+str(avg_fscore_fuzzy)+"\n",'green', attrs=['bold']))
      print(colored("\n\n\n Evaluator	:	END \n\n\n",'yellow', attrs=['bold']))
      print(colored("\n\n\n Writing StatisticalResults to Xls File . . . .\n\n\n",'yellow', attrs=['bold']))
      row=row+1
      output(row,worksheet,"BlockOMatic",avg_Retrieved_blocks_Algo,avg_Relevant_blocks_GT,avg_Hit_exact_match_metric,avg_precision_exact,avg_recall_exact,avg_fscore_exact,avg_Hit_fuzzy_match_metric,avg_precision_fuzzy,avg_recall_fuzzy,avg_fscore_fuzzy )
    
  
    #-------------------------------------------AlgorithmDriver : GomoryHu------------------------------------------#    
    elif algo_type==4: 
      i=0
      for k, v in URLDict.iteritems():
	print "---------------------------------ITERATION START		:	"+str(i)+"---------------------------------------------"
	print
	#------------------Execute Gomory Hu Python file-----------------#
	print (colored("Executing Gomory Hu Tree based Algorithm . . . . \n",'green', attrs=['bold']))
	os.system("python ImprovedFinalGomoryWebContentExtraction.py "+str(k))
      
	#------------------Copy the output to /Output/GOMORY folder----------------------------------#
	print (colored("Copying the output to /Output directory . . . . \n",'green', attrs=['bold']))
	destPath=current_directory+"/Output/GOMORY"
	print(colored("\n\n\n ALGORITHM DRIVER	:	END \n\n\n",'yellow', attrs=['bold']))
		
	print(colored("\n\n\n BLOCK MAPPER	:	START \n\n\n",'yellow', attrs=['bold']))
	
	#-----------------Parse The Output : GeneratedBlocks Extraction-----------------------------------------#
	
	print (colored("Parsing the output . . . . \n",'green', attrs=['bold']))
	print (colored("Generating text serialized version of Generated and GroundTruth Blocks . . . . \n",'green', attrs=['bold']))
	doc = etree.parse(destPath+"/segmented_webpage.xml")
	parser = HTMLParser()
	# Get the Blocks
	for node in doc.iter() :
	    block=node.xpath('/SegmentedPage/Cluster')
	
	for b in block :
	      tmp=Set()
	      for bb in b.getchildren() :
		
		textBlockOuterHTML=parser.unescape(bb.get("outerHTML"))
		
		textBlockTagPath=parser.unescape(bb.get("tagPath"))
		
		# Mapping the blocks from xml to html
		url = str(k)
		content = urllib2.urlopen(url).read()
		soup = BeautifulSoup(content)
		elems = soup.select((textBlockTagPath.replace("-"," > ")).lower())
		for e in elems :
		  if e.get_text() == BeautifulSoup(textBlockOuterHTML).get_text() :
		    e['class']='cluster'
		    tmp.add(e)
		
	      elems1=soup.findAll(attrs= { "class" : "cluster" })
	      
	      new_div = soup.new_tag("div")
	      new_div['class']='Cluster'

	      for content in reversed(elems1):
		new_div.insert(0, content.extract())
	      elems1.append(new_div)
	      # Getting the text of the block and removing all whitespaces
	      textBlock = new_div.get_text()
	      s=re.sub(r"\W", "", textBlock)
	      textBlockSet1.add(s)
	      for e in tmp :
		del e['class']
		
	#-----------------Parse The GroundTruth : GroundTruthBlocks Extraction-----------------------------------------#
	html_block=lxml.html.parse(str(GroundTruthDict[k]))
	for node in html_block.iter() :
	  block=node.xpath('//*[@data-block]')
	for r in block :
	  textBlock=r.text_content()
	  s=re.sub(r"\W", "", textBlock)
	  textBlockSet2.add(s)
	GroundTruthBlocksSet[k]=textBlockSet2
	GeneratedBlocksSet[k]=textBlockSet1
	print(colored("\n\n\n BLOCK MAPPER	:	END \n\n\n",'yellow', attrs=['bold']))
	#-------------------------------------------Evaluator------------------------------------------#
	print(colored("\n\n\n Evaluator	:	START \n\n\n",'yellow', attrs=['bold']))
	Hit_exact_match_metric,Hit_fuzzy_match_metric,precision_exact,precision_fuzzy,recall_exact,recall_fuzzy,Relevant_blocks_GT,Retrieved_blocks_Algo,fscore_exact,fscore_fuzzy=evaluator(GeneratedBlocksSet , GroundTruthBlocksSet)
	print(colored("Calculating averages . . . . \n",'yellow', attrs=['bold']))
	sum_Hit_exact_match_metric=sum_Hit_exact_match_metric+Hit_exact_match_metric
	sum_Hit_fuzzy_match_metric=sum_Hit_fuzzy_match_metric+Hit_fuzzy_match_metric
	sum_precision_exact=sum_precision_exact+precision_exact
	sum_precision_fuzzy=sum_precision_fuzzy+precision_fuzzy
	sum_recall_exact=sum_recall_exact+recall_exact
	sum_recall_fuzzy=sum_recall_fuzzy+recall_fuzzy
	sum_Relevant_blocks_GT=sum_Relevant_blocks_GT+Relevant_blocks_GT
	sum_Retrieved_blocks_Algo=sum_Retrieved_blocks_Algo+Retrieved_blocks_Algo
	sum_fscore_exact=sum_fscore_exact+fscore_exact
	sum_fscore_fuzzy=sum_fscore_fuzzy+fscore_fuzzy
	time.sleep(4)
	print "---------------------------------ITERATION END		:	"+str(i)+"---------------------------------------------"
	print
	print
	i=i+1
      avg_Hit_exact_match_metric=float(sum_Hit_exact_match_metric) / len(URLDict)
      avg_Hit_fuzzy_match_metric=float(sum_Hit_fuzzy_match_metric) / len(URLDict)
      avg_precision_exact=float(sum_precision_exact) / len(URLDict)
      avg_precision_fuzzy=float(sum_precision_fuzzy) / len(URLDict)
      avg_recall_exact=float(sum_recall_exact) / len(URLDict)
      avg_recall_fuzzy=float(sum_recall_fuzzy) / len(URLDict)
      avg_Relevant_blocks_GT=float(sum_Relevant_blocks_GT) / len(URLDict)
      avg_Retrieved_blocks_Algo=float(sum_Retrieved_blocks_Algo) / len(URLDict)
      avg_fscore_exact= float(sum_fscore_exact) / len(URLDict)
      avg_fscore_fuzzy= float(sum_fscore_fuzzy) / len(URLDict)
      
      print (colored("Avg Retrieved Blocks ------> \t"+str(avg_Retrieved_blocks_Algo)+"\n",'green', attrs=['bold']))
      print (colored("Avg Relevant Blocks ------> \t"+str(avg_Relevant_blocks_GT)+"\n",'green', attrs=['bold']))
      print (colored("Avg HIT Exact ------> \t"+str(avg_Hit_exact_match_metric)+"\n",'green', attrs=['bold']))
      print (colored("Avg Precision Exact ------> \t"+str(avg_precision_exact)+"\n",'green', attrs=['bold']))
      print (colored("Avg Recall Exact ------> \t"+str(avg_recall_exact)+"\n",'green', attrs=['bold']))
      print (colored("Avg F-Score Exact ------> \t"+str(avg_fscore_exact)+"\n",'green', attrs=['bold']))
      print (colored("Avg HIT Fuzzy ------> \t"+str(avg_Hit_fuzzy_match_metric)+"\n",'green', attrs=['bold']))
      print (colored("Avg Precision Fuzzy ------> \t"+str(avg_precision_fuzzy)+"\n",'green', attrs=['bold']))
      print (colored("Avg Recall Fuzzy ------> \t"+str(avg_recall_fuzzy)+"\n",'green', attrs=['bold']))
      print (colored("Avg F-Score Fuzzy ------> \t"+str(avg_fscore_fuzzy)+"\n",'green', attrs=['bold']))
      print(colored("\n\n\n Evaluator	:	END \n\n\n",'yellow', attrs=['bold']))
      print(colored("\n\n\n Writing StatisticalResults to Xls File . . . .\n\n\n",'yellow', attrs=['bold']))
      row=row+1
      output(row,worksheet,"GomoryHu",avg_Retrieved_blocks_Algo,avg_Relevant_blocks_GT,avg_Hit_exact_match_metric,avg_precision_exact,avg_recall_exact,avg_fscore_exact,avg_Hit_fuzzy_match_metric,avg_precision_fuzzy,avg_recall_fuzzy,avg_fscore_fuzzy )
    
    elif algo_type==7:
      print(colored("\n\n\n Test Framework	:	END \n\n\n",'yellow', attrs=['bold']))
      workbook.close()
      sys.exit()
    else :
      print "Wrong Choice"
      continue
      
      
    print(colored("\n\n\n Test Framework	:	END \n\n\n",'yellow', attrs=['bold']))
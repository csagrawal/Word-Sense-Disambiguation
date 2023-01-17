#!/usr/bin/env python
# coding: utf-8

import re
import string
import sys
import math

def cross_validation(line,word_sense_count,total_count,sense1,sense2,output_file_name):
    
    sen1=sense1
    sen2=sense2

    output_file = open(output_file_name,"a")
    
    avg_accuracy=0
    if(total_count % 5 ==0):
        partition_size = total_count//5
    else:
        partition_size = (total_count//5)+1

    #dividing data into training and testing set
    for i in range(5):  #no. of folds
        fold_no = i+1
        
        start_index = i*partition_size*7
        end_index = i*partition_size*7 + partition_size*7
        training_data=[]
        testing_data=[]

        for j in range(len(line)):

            if(j in range(start_index,end_index)):
                testing_data.append(line[j]) 
            else:
                training_data.append(line[j])
                
        word_sense_count,sense1_count, sense2_count,v1_size,v2_size = train_wsd(training_data,word_sense_count,sen1,sen2)
        accuracy,output_file = test_wsd(testing_data,word_sense_count,sense1,sense2,sense1_count,sense2_count,v1_size,v2_size,output_file,fold_no) 
        avg_accuracy += accuracy
        print("Fold",i+1,"accuracy is = ",accuracy,"%")
    output_file.close()
    avg_accuracy = (avg_accuracy/5)
    print("Average accuracy is = ",avg_accuracy,"%")


def test_wsd(testing_data,word_sense_count,sense1 , sense2 , sense1_count, sense2_count,v1_size,v2_size,output_file,fold_no):
     
    output_file.write("Fold "+str(fold_no)+"\n")

    # probability_as_sense1
    count=0
    correct_count=0
    print_string2 = ""
    
    probability_as_sense1, probability_as_sense2=0,0

    test_data = testing_data
    for i in range(len(test_data)):
        line[i]=line[i].lower()   

        if(i < (len(line)-1)):
            line[i+1]=line[i+1].lower()
        
        if("instance id" in line[i]):
            print_data = (re.split('instance id="|" ',line[i]))
            print_string1 = print_data[1]
            
        if('senseid="' in line[i]):
            input_line = (re.split('senseid="|%|"/>',line[i]))
            sense = input_line[2]
            print_string2 = input_line[1]

        if(print_string2):
            print_string = print_string1 + " " + print_string2 + "%"  

        if('<context>' in line[i]):
            words = list(line[i+1].split())
            for each_word in words:

                #removing symbols at start and end of word
                while((len(each_word) > 0) and (each_word[-1] in symbols)):
                    each_word=each_word[:-1]
                while((len(each_word) > 0) and (each_word[0] in symbols)):
                    each_word=each_word[1:]
                
                if('head>' in each_word):
                    input_head = (re.split('head>|</head',each_word))
                    each_word = input_head[1]              
                                                   
                count_of_word1 = word_sense_count[sense1][each_word] if(each_word in word_sense_count[sense1]) else 0
                if(probability_as_sense1==0):
                    probability_as_sense1 = math.log(((count_of_word1 + 1)/(sense1_count + v1_size)),2)
                else:
                    probability_as_sense1 += math.log(((count_of_word1 + 1)/(sense1_count + v1_size)),2)                

                count_of_word2 = word_sense_count[sense2][each_word] if(each_word in word_sense_count[sense2]) else 0  
                
                if(probability_as_sense2==0):
                    probability_as_sense2 = math.log(((count_of_word2 + 1)/(sense2_count + v2_size)),2)
                else:
                    probability_as_sense2 += math.log(((count_of_word2 + 1)/(sense2_count + v2_size)),2)                


            test_sense = sense1 if(probability_as_sense1 > probability_as_sense2) else sense2
            print_string_final = print_string + test_sense
            if(test_sense == sense):
                correct_count+=1
                count+=1
            else: 
                count+=1
            output_file.write(print_string_final+"\n")

    accuracy = (correct_count/count) * 100
    return(accuracy,output_file)

def train_wsd(training_data,word_sense_count,sense1,sense2):
    
    line = training_data
    first, count, sense1_count , sense2_count = 0 , 0 , 0 , 0

    for i in range(len(line)):    
        line[i]=line[i].lower()   

        if(i < (len(line)-1)):
            line[i+1]=line[i+1].lower()

        #sense
        if('senseid="' in line[i]):
            input_line = (re.split('senseid="|%|"/>',line[i]))
            sense = input_line[2]

        #word and sence dictionary
        if('<context>' in line[i]):
            words = list(line[i+1].split())
            for each_word in words:

                #removing symbols at start and end of word
                while((len(each_word) > 0) and (each_word[-1] in symbols)):
                    each_word=each_word[:-1]
                while((len(each_word) > 0) and (each_word[0] in symbols)):
                    each_word=each_word[1:]

                if(sense == sense1):
                    if((each_word) not in word_sense_count[sense1]):
                        if('head>' not in each_word):
                            word_sense_count[sense1][each_word]=1                        
                        else:
                            input_head = (re.split('head>|</head',each_word))
                            each_word = input_head[1]
                            sense1_count+=1
                            if(each_word not in word_sense_count[sense1]):
                                word_sense_count[sense1][each_word]=1 
                                continue
                            word_sense_count[sense1][each_word]+=1          
                    else:
                        word_sense_count[sense1][each_word]+=1   
                else:
                    if((each_word) not in word_sense_count[sense2]):
                        if('head>' not in each_word):
                            word_sense_count[sense2][each_word]=1                        
                        else:
                            input_head = (re.split('head>|</head',each_word))
                            each_word = input_head[1]
                            sense2_count+=1
                            if(each_word not in word_sense_count[sense2]):
                                word_sense_count[sense2][each_word]=1
                                continue
                            word_sense_count[sense2][each_word]+=1   
                    else:
                        word_sense_count[sense2][each_word]+=1   

        #count of senses                
        v1_size = len(word_sense_count[sense1])
        v2_size = len(word_sense_count[sense2])   
    return(word_sense_count,sense1_count, sense2_count,v1_size,v2_size)

if __name__ == "__main__":
    arguments = sys.argv  
    input_file = str(arguments[1])
    
    output_file_name = input_file+ ".out"
    
    file = open(input_file,"r")
    line = file.readlines()
    symbols=string.punctuation
    
    sense1 , sense2 = "" , ""
    
    first=0
    for i in range(len(line)):
        if('instance id' in line[i]):
            first+=1 
            print_data = (re.split('instance id="|" ',line[i]))
        if (not sense1) or (not sense2):
            if('senseid="' in line[i]):
                input_line = (re.split('senseid="|%|"/>',line[i]))
                sense = input_line[2]
                if(first==1):
                    sense1 = input_line[2]
                if(sense != sense1):
                    sense2 = sense
          
    total_count=first                    
    word_sense_count = { sense1 : {} , sense2 : {} }
    
    #data dividing into folds for cross validation
    cross_validation(line,word_sense_count,total_count,sense1,sense2,output_file_name)




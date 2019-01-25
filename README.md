# GmailClient
Standalone Application connecting to Gmail and taking actions on messages.  
Video demo of running application - https://youtu.be/KdyDwCuL5sc

**crawler.py**  
Standaloe script which establishes a connection with Gmail using Oauth.  
Parses messages in gmail and stores in Database  
On subsequent runs, it fetches last stored messages time, and filters only new mail details, and stores the same  

**database.sql**  
Email_details: Master table consisting of email,message ids and internal time   
Message_details: Table containing message details, including From address,To Address, Subject, LabelId, TimeStamp  
Label_details : Mapping table of label id and label name  

**rules.json**  
Json file consiting of rules with a structure including Predicates, Criterias and sets of Actions  

**action.py**  
Standalone script displaying set of rules parsed from Rules.json file  
Script expects rule number to be chosen by the user  
Performs actions as described in rule and changes the state of Gmail messages in real time  

**ENHANCEMENTS TO BE MADE**
The assignment is completed to meet the requirements. However following enhancements could be made  
Rules and actions are predefined - This could be taken from user as command line arguments  
Converting the standalone script into a GUI application using PyQT  
Unit and functional test cases  

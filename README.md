# GmailClient
Standalone Application connecting to Gmail and taking actions on messages.

**crawler.py**
Standaloe script which establishes a connection with Gmail using Oauth.  
Parses message based on timestamp and stores in Database  

**database.sql**
Email_details: Master table consisting of email and message ids  
Message_details: Table containing message details, including From address,To Address, Subject, LabelId, TimeStamp  
Label_details : Mapping table of label id and label name  

**rules.json**
Json file consiting of rules with a structure convering Predicates, Criterias and sets of Actions  

**action.py**
Standalone script displaying set of rules parsed from Rules.json file  
Script expects rule number to be chosen by the user  
Performs actions as described in rule and changes the state of Gmail messages in real time  

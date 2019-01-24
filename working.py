from __future__ import print_function
from apiclient import discovery, errors
from httplib2 import Http
from oauth2client import file, client, tools
import base64
import email
import json
import mysql.connector
import re
import datetime

SCOPES = 'https://www.googleapis.com/auth/gmail.modify'

class GmailClient(object):
    
    def __init__(self):
        """
            Initialize GmailClient variables
        """
        self.service=self.get_gmail_service()
        self.user_id='me'
    
    def get_gmail_service(self):
        """"
        :Summary: 1. Establish connection with Gmail using oauth
                  2. Authenticate using browser token
                  3. Store credentials locally for further connections
                  4. Return service 
        
        """
        store = file.Storage('token.json')
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
            credentials = tools.run_flow(flow, store)
        service = discovery.build('gmail', 'v1', http=credentials.authorize(Http()))
        return service

    def fetch_label_messages(self,label_ids=[]):
        """
        Fetches all Messages of labels  
        :Args:
        label_ids: Only return Messages with labelIds applied.
        :Returns:
        List of Messages 
        """
        try:
            response = self.service.users().messages().list(userId=self.user_id,
                                                       labelIds=label_ids).execute()
        
            messages = []
            if 'messages' in response:
              messages.extend(response['messages'])
        
            while 'nextPageToken' in response:
              page_token = response['nextPageToken']
              response = self.service.users().messages().list(userId=self.user_id,
                                                         labelIds=label_ids,
                                                         pageToken=page_token).execute()
              messages.extend(response['messages'])
        
            return messages
        except Exception as error:
            print('Error encountered: %s' % error)

    def fetch_email(self,messages):
        """
        :summary: Makes request to google service to fetch metadata
        :args: messages - list of dicts containing message ids
        :returns: List of email addresses
        """
        email_addresses=[]
        message_details=[]
        for each_message in messages:
            id=each_message.get('id')
            response=self.service.users().messages().get(userId='me', 
                                                   id = id,
                                                   format='metadata', 
                                                   metadataHeaders=["To", "From", "Subject"]).execute()
            label_ids=response['labelIds']
            date=datetime.datetime.fromtimestamp(int(response['internalDate'])/1000)
            headers=response['payload']['headers']
            message_detail=self.parse_message(headers)
            email_id=message_detail.get('from_address')
            for label in label_ids:    
                message_details.append((id,
                                        message_detail['from_address'],
                                        message_detail['to_address'],
                                        message_detail['subject'],
                                        label,
                                        date))
            email_addresses.append((id,email_id))
        print("Email addresses fetched:%s"%email_addresses)
        self.create_tables()
        self.add_email_details(email_addresses)
        self.add_message_details(message_details)
    
    def add_email_details(self,email_addresses):
        """
            sql queries
        """
        mydb = mysql.connector.connect(
                  host="192.168.56.102",
                  user="root",
                  passwd="Global!23",
                  database="tenmiles"
                )
        mycursor = mydb.cursor()
        query="INSERT INTO email_details (id,email_address) values (%s,%s)"
        mycursor.executemany(query,email_addresses)             
        mydb.commit()      
        
    def add_message_details(self,message_details):
        """
            sql queries
        """
        print("Inserting message details to db with %s "%message_details)
        mydb = mysql.connector.connect(
                  host="192.168.56.102",
                  user="root",
                  passwd="Global!23",
                  database="tenmiles"
                )
        mycursor = mydb.cursor()
        query="INSERT INTO message_details (message_id,from_address,to_address,subject,label_id,message_date) values (%s,%s,%s,%s,%s,%s)"
        mycursor.executemany(query,message_details)             
        mydb.commit()      
    
    def parse_message(self,headers):
        """
        :summary: Parses from,to,subject from headers
        :args: Headers- Header parameters of a particular message
        :returns: message detail dictionary
        """
        message_detail={}
        for record in headers:
            if record.get('name')=='From':
                message_detail['from_address']=self.parse_email(record.get('value'))
            if record.get('name')=='To':
                message_detail['to_address']=record.get('value')
            if record.get('name')=='Subject':
                message_detail['subject']=record.get('value')
        return message_detail
      
    def parse_email(self,email_address):
        if email_address:
            pattern = re.search('<(.+?)>', email_address)
            email_id=pattern.group(1)
            print(email_id)
            return email_id
            
    def create_tables(self):
        """
        :summary: Establishes connection objects to mysql, and performs queries
        """
        mydb = mysql.connector.connect(
                  host="192.168.56.102",
                  user="root",
                  passwd="Global!23",
                  database="tenmiles"
                )
        mycursor = mydb.cursor()
        mycursor.execute("CREATE TABLE IF NOT EXISTS email_details (id VARCHAR(255) PRIMARY KEY, email_address VARCHAR(255))")
        mycursor.execute("CREATE TABLE IF NOT EXISTS label_details (id int PRIMARY KEY, label_name VARCHAR(255))")
        mycursor.execute("CREATE TABLE IF NOT EXISTS message_details (id int auto_increment PRIMARY KEY,message_id VARCHAR(255), from_address VARCHAR(255),\
                        to_address VARCHAR(255),subject VARCHAR(255),label_id VARCHAR(100),message_date datetime,\
                        FOREIGN KEY(message_id) REFERENCES email_details(id))")
#         mycursor.execute("CREATE TABLE IF NOT EXISTS message_details (id int auto_increment PRIMARY KEY,message_id VARCHAR(255), from_address VARCHAR(255),\
#                         to_address VARCHAR(255),subject VARCHAR(255),label_ids JSON,message_date date,\
#                         FOREIGN KEY(message_id) REFERENCES email_details(id))")
        
        mydb.commit()      
        
    def read_all_labels(self):
        results = self.service.users().labels().list(userId = 'me').execute()
        labels = results.get('labels', [])
        if not labels:
            print('No labels found.')
        else:
            print('Labels:')
            for label in labels:
                print(label['name'])


def main():
    client_obj=GmailClient()
    client_obj.read_all_labels()
    messages = client_obj.fetch_label_messages(label_ids=['INBOX'])
    email_addresses=client_obj.fetch_email(messages)
    import pdb;pdb.set_trace();
    client_obj.create_entries(email_addresses)    





if __name__ == "__main__":
    main()


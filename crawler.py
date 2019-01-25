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
        :summary:
                    1. Fetches the last message datetime record in database
                    2. Applies filter to gmail api to fetch messages after this time
                    3. Iterates and forms message list
        """
        try:
            last_fetched_time=self.last_fetched_message_time()
            if last_fetched_time:
                query="after:"+str(last_fetched_time)
                response = self.service.users().messages().list(userId=self.user_id,q=query,
                                                       labelIds=label_ids).execute()
            else:
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

    def last_fetched_message_time(self):
        """
        :summary: Fetches the last gmail message time
                    
        """
        
        mydb=self.get_mydb()
        mycursor = mydb.cursor()
        query="SELECT max(internal_date) from email_details;"
        mycursor.execute(query)
        result=mycursor.fetchone()
        return result[0]
    
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
            internal_date=int(response['internalDate'])/1000
            date=datetime.datetime.fromtimestamp(internal_date)
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
            email_addresses.append((id,email_id,internal_date))
        self.add_email_details(email_addresses)

        self.add_message_details(message_details)
    
    def add_email_details(self,email_addresses):
        """
        :message_details: List of tuples containing messageid,from address,to address,subject,label id, message date
        :summary:    
                    1. Received database object
                    2. Inserts data into email details table
        """
        mydb=self.get_mydb()
        mycursor = mydb.cursor()
        query="INSERT INTO email_details (id,email_address,internal_date) values (%s,%s,%s)"
        mycursor.executemany(query,email_addresses)             
        mydb.commit()      
        
    def add_message_details(self,message_details):
        """
        :message_details: List of tuples containing messageid,from address,to address,subject,label id, message date
        :summary:    
                    1. Received database object
                    2. Inserts data into message details table
        """
        mydb=self.get_mydb()
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
        """
        :args: email_address: email string enclosed in <> operator
        :summary:
                    1. Received email address and splits based on regex
                    2. Reuturns matching group
        """
        if email_address:
            pattern = re.search('<(.+?)>', email_address)
            if pattern:
                email_id=pattern.group(1)
                print(email_id)
                return email_id
            else:
                print(email_address)
                return str(email_address)
    def create_tables(self):
        """
        :summary: 1. Gets database connection object
                  2. Creates database tables
        """
        mydb=self.get_mydb()
        mycursor = mydb.cursor()
        mycursor.execute("CREATE TABLE IF NOT EXISTS email_details (id VARCHAR(255) PRIMARY KEY, email_address VARCHAR(255),internal_date bigint)")
        mycursor.execute("CREATE TABLE IF NOT EXISTS label_details (id VARCHAR(100) PRIMARY KEY, label_name VARCHAR(255))")
        mycursor.execute("CREATE TABLE IF NOT EXISTS message_details (id int auto_increment PRIMARY KEY,message_id VARCHAR(255), from_address VARCHAR(255),\
                        to_address VARCHAR(255),subject VARCHAR(255),label_id VARCHAR(100),message_date datetime,\
                        FOREIGN KEY(label_id) REFERENCES label_details(id),FOREIGN KEY(message_id) REFERENCES email_details(id))")
        mydb.commit()      
        
    def get_mydb(self):
        """
        :summary:
                 1. Establishes connection to mysql
                 2. Returns db connection object
        """
        
        mydb = mysql.connector.connect(
                  host="192.168.56.102",
                  user="root",
                  passwd="Global!23",
                  database="tenmiles"
                )
        return mydb
    
    def read_all_labels(self):
        """
        :summary:
                    1. Fetch all the labels of user
                    2. Loop through label list and store mapping in database 
        """
        results = self.service.users().labels().list(userId = 'me').execute()
        labels = results.get('labels', [])
        if not labels:
            print('No labels found.')
        else:
            mydb=self.get_mydb()
            mycursor = mydb.cursor()
            for label in labels:
                query="INSERT INTO label_details values ('%s','%s')"%(label['id'],label['name'])
                mycursor.execute(query)
            mydb.commit()

def main():
    """
    :summary: 
        1. Establish connection to Gmail using Oauth
        2. Read all labels and store in database
        3. Read all messages and store in database
        4. If messages are already parsed, fetch new messages based on timestamp
    """
    client_obj=GmailClient()
    client_obj.create_tables()
#     client_obj.read_all_labels()
    messages = client_obj.fetch_label_messages(label_ids=['INBOX'])
    email_addresses=client_obj.fetch_email(messages)


if __name__ == "__main__":
    main()

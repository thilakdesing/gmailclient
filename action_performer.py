from __future__ import print_function
from apiclient import discovery, errors
from httplib2 import Http
from oauth2client import file, client, tools
import base64
import json
import mysql.connector

class ActionPerformer(object):
    """
        Peforms actions on messages based on rules
    """
    def display_rules(self):
        """
        :summary:
                    1.Displays the set of rules and actions by parsing rules.json file
                    2.Expects user to choose rule number from command line
                    3.Calls rule engine to implement rule
        """
    	rules = json.load(open('rules.json'))
    	for rule_number,rule_record in rules.iteritems():
    		criterias=rule_record['criteria']
    		print("")
    		print ("Rule %s matching %s of the following rules -->%s"%(rule_number,rule_record['predicate'],rule_record['action']) )
    		for criteria in criterias:
    			print (rule_number,criteria['name'],criteria['value'][0],criteria['value'][1])
    	
    	done=0
    	while(done==0):
    		rule_input=raw_input("Choose rule number from above rules:")
    		if rule_input not in rules.keys():
    			print ("Invalid input.")
    		else:
    			done=1
    	self.rule_engine(rule_input)

    def rule_engine(self,rule_input):
        """
        :args: rule_input: Rule number chosen by user
        :summary:
                    1.Parses criterias in rules.json for chosen rule number
                    2.Fetches results based on criterias by calling database
                    3.Filters results based on predicates (ANY/ALL)
        """
    	rules = json.load(open('rules.json'))
    	chosen_rule=rules[rule_input]
    	print('Beginning action')
        criterias=chosen_rule['criteria']
        result={}
        for rule in criterias:
            
            if rule['value'][0]=='contains': 
                query="SELECT message_id from message_details where "+rule['name']+" like '%"+rule['value'][1]+"%';"
    	    elif rule['value'][0]=='equals':
                query="SELECT message_id from message_details where "+rule['name']+"='"+rule['value'][1]+"';"
            elif rule['value'][0]=='greaterthanequals':
                query="SELECT message_id from message_details where "+rule['name']+">='"+rule['value'][1]+"';"
            elif rule['value'][0]=='lessthanequals':
                query="SELECT message_id from message_details where "+rule['name']+"<='"+rule['value'][1]+"';"
            result[rule['name']]=self.execute_query(query)
        
        master_result=[]
        for field,field_result in result.iteritems():
            for entry in field_result:
                master_result.append(entry)
        if chosen_rule['predicate']=='ANY':
            final_list= master_result
        if chosen_rule['predicate']=='ALL':
            result_list=result.values()
            common_result=set(result_list[0]).intersection(*result_list)
            final_list=common_result
        print(final_list)        
        modify_body=chosen_rule['modify_body']
        modify_body['ids']=list(final_list)
        self.perform_action(modify_body)
        
    def perform_action(self,modify_body):
        """
        :args: modify_body: dictionary containing labels to be modified
        :summary:
                    1. Connects to google service
                    2. Executes modification on selected messages
        """
        SCOPES = 'https://www.googleapis.com/auth/gmail.modify'
        store = file.Storage('token.json')
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
            credentials = tools.run_flow(flow, store)
        service = discovery.build('gmail', 'v1', http=credentials.authorize(Http()))
        
        message = service.users().messages().batchModify(userId='me',
                                                body=modify_body).execute()
            
    
    def execute_query(self,query):
        """
        :args: query: Query to be executed
        :summary:
                 1. Establishes connection to mysql
                 2. Creates cursor and implements query
                 3. Modifies result set to convenient format
        """
        mydb = mysql.connector.connect(
                  host="192.168.56.102",
                  user="root",
                  passwd="Global!23",
                  database="tenmiles"
                )
        mycursor = mydb.cursor()
        mycursor.execute(query)
        result=mycursor.fetchall()
        final_result=[]
        for x in result:
            final_result.append(x[0])
        return final_result      
               
def main():
	act_obj=ActionPerformer()
	act_obj.display_rules()


if __name__ == '__main__':
    main()


1. alertuser.zip
	- contains code for "notifyuser" lambda function
	- notifies the  user if user is not drinking enough water
2. hydrationtracker.zip
	- contains code for "hydrationtracker" lambda function
	- receives messages from IoT device and persists the processed data into Mysql database created in RDS
3. resetwater.zip
	- contains code for "resetwater" lambda function
	- called everyday at 12AM. Resets the amount of water consumed by user to '0' every day.

Using .zip files:
Each .zip file contains source code for lambda functions used in hydration tracker project. 
Uploading the .zip file to aws
	- create a lambda function 
	- Under the function code pane, select "Upload a .zip file" from code entry type dropdown menu
	- Select Python 2.7 from Runtime dropdown menu
	- type main.main in Handler
	- Save the code

Execution role:
I am choosing existing role "accumulateweight"
In I AM console, I have allowed "accumulateweight" role to access, AWS RDS, AWS IOT, AWS SNS etc.

Leave the other settings as it is. 
Save the lambda function.






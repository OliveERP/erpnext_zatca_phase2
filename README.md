## Erpnext Zatca

Integration of ERPNExt with ZATCA system, which covers:
1. Cryptographically signing the invoice.
2. Reporting the invoice.
3. Clearing the invoice digitally.
4. Generating QRCODE.

##	Technical FAQs:

-	What JAVA version should I install before using the SDK?
 The prerequisite is using the Java SDK (JAR) versions >=11 and <15.

-	What should the user do when faced with a JAVA error?
When faced with a JAVA error, the user needs to install JAVA (versions >=11 and <15) before running and using the SDK.

Install/Update for Linux
1.	Install [jq] from https://stedolan.github.io/jq/
2.	Download the sdk.zip file
3.	Run command sh ~/.bash_profile
4.	If error, then create a file .bash_profile in root or home directory.
5.	Unzip the sdk.zip file
6.	Now, open a command line/terminal and point to the root folder of the sdk.
7.	Replace the word “source” with “.” On lines 31 and 32 of install.sh
8.	Run command install.sh 
9.	Run sh ~/.bash_profile
10.	Run command cd $FATOORA_HOME
11.	Run command chmod +x fatoora
12.	Now, you can start using the fatoora cli. Please run fatoora -help to get all supported commands



#### License

MIT

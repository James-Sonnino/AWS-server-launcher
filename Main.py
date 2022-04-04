from googleapiclient.errors import HttpError
import gmail
import subprocess  # For executing a shell command
import time
import requests
import urllib3
import sys

#disable unverified https request warning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

to = "demo@anydemo.awsapps.com"
regions = ["NA", "APAC", "EMEA"]
servers = {"1": "Demo-HQ-EMEA", "2": "Demo-V1-EMEA", "3": "Demo-V2-EMEA-1", "4": "Demo-V2-EMEA-2", "5": "Demo-V2-APAC-1", "6": "Demo-V2-APAC-2", "7": "Demo-V2-NA-1", "8": "Demo-V2-NA-2", "9": "Demo-Prox-EMEA", "10": "Demo-Prox-NA", "11": "Demo-ABX-EMEA", "12": "Demo-ABX-NA"}

def check_services(host):
    """
    Returns True if all services are up, returns False otherwise
    """
    url = "https://" + host + "/bt/api"
    #login and get a token
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    response = requests.request("POST", url + "/login", headers=headers, json= {"username": "AnyVisionAdmin","password": "AVpa$$word!","isEulaConfirmed": "true"}, verify=False)
    token = response.json()["token"]

    #check services health
    headers = {
        "Authorization": f"bearer {token}",
        "Accept": "application/json"
    }
    response = requests.request("GET", url + "/health", headers=headers, verify=False).json()
    for service in response:
        if response[service][0]["status"] != "passing":
            return False
    return True
            


def is_up(host):
    """
    Returns True if host (str) responds to a ping request.
    Remember that a host may not respond to a ping (ICMP) request even if the host name is valid.
    """
    # Building the command. Ex: "ping -c 1 google.com"
    command = ['ping', '-n', '1', host]

    return subprocess.call(command, stdout=subprocess.DEVNULL) == 0    



def validated(x,n1,n2):
    """
    INPUT VALIDATION
    returns a validated value that is a number 
    in range of n1<=x<=n2
    """
    done = False
    while (not done):
        try:
            y = int(x)
            if y >= n1 and y <= n2:
                done = True
            else:
                x = input(f"Please enter only numbers between {n1} and {n2}:\n")
        except:
            x = input("Please enter only integers:\n")
    return x

def list_is_valid(l, n1, n2):
    """
    INPUT VALIDATION
    returns True if all elements of list L are numbers
    between n1 and n2
    """
    for i in l:
        try:
            x = int(i)
            if x < n1 or x > n2:
                return False
        except:
            return False
    return True



def print_greeting():
    print("""
    
    
    Hi, and welcome to the...
     ___        ______                                   _                        _                
    / \ \      / / ___|   ___  ___ _ ____   _____ _ __  | | __ _ _   _ _ __   ___| |__   ___ _ __  
   / _ \ \ /\ / /\___ \  / __|/ _ \ '__\ \ / / _ \ '__| | |/ _` | | | | '_ \ / __| '_ \ / _ \ '__| 
  / ___ \ V  V /  ___) | \__ \  __/ |   \ V /  __/ |    | | (_| | |_| | | | | (__| | | |  __/ |    
 /_/   \_\_/\_/  |____/  |___/\___|_|    \_/ \___|_|    |_|\__,_|\__,_|_| |_|\___|_| |_|\___|_|    
                                                                                                   
    """)

def main_menu():
    choice = input("""
    Hi! What would you like to do?
    
    1) launch AWS server/s
    2) exit
    
    Please enter 1 or 2:
    """)
    return validated(choice, 1, 2)

def launch_menu():
    choices = input("""
Which server/s would you like to launch? Please enter a single number, or a space seperated list of numbers between 1 and 12. (Ex: 3 5 12)

1) BT V1 HQ EMEA
2) BT V1 Site EMEA
3) Demo V2 EMEA 1
4) Demo V2 EMEA 2
5) Demo V2 APAC 1
6) Demo V2 APAC 2
7) Demo V2 NA 1
8) Demo V2 NA 2
9) Demo Prox EMEA
10) Demo Prox NA
11) Demo ABX EMEA
12) Demo ABX NA
\n\n
""").split()
    
    #validate the input
    while (not list_is_valid(choices, 1, 12)):
        choices = input("Please enter a single number, or a space seperated list of numbers between 1 and 12. (Ex: 3 5 12)\n").split()
    duration = input("For how long do you want the server/s to be up? (You can choose from 1 to 24 hours)\n")
    duration = validated(duration, 1, 24)

    #send email for each chosen server
    for i in choices:
        #set product
        product = servers[i]
        #set region
        for j in regions:
            if j in product:
                region = j        
        body = f"Product: {product}\nRegion: {region}\nDuration: {duration}"
        subject = "Sent using AWS Server Launcher"
        try:
            # Call the Gmail API
            message = gmail.create_message(None, "demo@anydemo.awsapps.com", subject, body)
            gmail.send_message(gmail.get_service(), "me", message)
        except HttpError as error:
            #TODO: Handle errors from gmail API.
            print(f'An error occurred: {error}')        

    #this loop checks if the host and Web UI are up 
    for i in choices:
        hostname = servers[i].lower()
        counter = 0
        ping_available = False

        print()
        print("WARNING! You must be connected to the VPN in order to check if the server is up!")
        print(f"Checking if {servers[i]} is up. Please wait...")
        
        #check ping
        while True:
            if is_up(hostname + ".tls.ai"):
                ping_available = True
                break
            else:
                sys.stdout.write(".")
                sys.stdout.flush()
            counter += 1
            if counter == 10:
                print()
                print("Failed to start the instance. Insufficient capacity on Amazon Web Services.")
                break
            
        print()
        
        if ping_available:
            if "v1" in hostname:
                print(f"{servers[i]} is up. You can now connect using the V1 dashboard.\n\n")
            else:
            #check services
                counter = 0
                while True:
                    if counter == 10:
                        print(f"{servers[i]}'s services are not coming up. Please open a ticket to the Support Team at https://oosto.com/support/")
                        break
                    try:
                        if check_services(hostname + ".tls.ai"):
                            print(f"{servers[i]} is up and all services are running!!")
                            print(f"Link to web UI for {servers[i]}: https://{hostname}.tls.ai/\n\n")
                            break
                        else:
                            counter += 1
                            print("Waiting for all services to start...")
                            for i in range(60):
                                time.sleep(1)
                                sys.stdout.write(".")
                                sys.stdout.flush()
                            print()
                    except:
                        counter += 1
                        print("Waiting for all services to start...")
                        for i in range(60):
                            time.sleep(1)
                            sys.stdout.write(".")
                            sys.stdout.flush()
                        print()

    input("Press any key to go back to the main menu: ")

def main():
    while True:  
        print_greeting()
        main_menu_choice = main_menu()
        if main_menu_choice == "2":
            print("Thank you for using the AWS server launcher. See you next time!")
            break
        else:
            launch_menu()

main()
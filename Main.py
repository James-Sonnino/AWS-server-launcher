from googleapiclient.errors import HttpError
import gmail
import subprocess  # For executing a shell command
import time


to = "demo@anydemo.awsapps.com"
regions = ["NA", "APAC", "EMEA"]
servers = {"1": "Demo-HQ-EMEA", "2": "Demo-V1-EMEA", "3": "Demo-V2-EMEA-1", "4": "Demo-V2-EMEA-2", "5": "Demo-V2-APAC-1", "6": "Demo-V2-APAC-2", "7": "Demo-V2-NA-1", "8": "Demo-V2-NA-2", "9": "Demo-Prox-EMEA", "10": "Demo-Prox-NA", "11": "Demo-ABX-EMEA", "12": "Demo-ABX-NA"}



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
                x = input("Please enter only numbers between {0} and {1}:\n".format(n1, n2))
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

    #check if hosts are up and serve Web  UI link
    for i in choices:
        print("\nChecking if {} is up. Please wait...".format(servers[i]))
        counter = 0
        while True:
            if is_up(servers[i].lower() + ".tls.ai"):
                print("{} is up!!".format(servers[i]))
                print("Link to web UI for {0}: https://{1}.tls.ai/\n\n".format(servers[i], servers[i].lower()))
                break
            else:
                print("...")
            counter += 1
            time.sleep(2)

            if counter == 10:
                print("Failed to start the instance. Insufficient capacity on Amazon Web Services.")
                break

    input("Press any key to go back to the main menu: ")
    
#####################################

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


















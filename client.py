import requests
from datetime import datetime

server_url = 'http://127.0.0.1:5000'
username = None  # store logged-in username

# ---------- LOGIN ----------
def login():
    global username
    while True:
        u = input("Enter username: ")
        p = input("Enter password: ")
        response = requests.post(f'{server_url}/login', json={"username": u, "password": p})
        data = response.json()
        if response.status_code == 200:
            print(data["message"])
            username = u
            break
        else:
            print(data["message"], "- Try again.")

# ---------- CREATE EVENT ----------
from datetime import datetime

def create_event():
    while True:
        # Validate event name
        event_name = input("Enter event name: ").strip()
        if not event_name:
            print("Event name cannot be empty. Try again.")
            continue

        # Validate date format
        event_date = input("Enter event date (YYYY-MM-DD): ").strip()
        try:
            datetime.strptime(event_date, "%Y-%m-%d")
        except ValueError:
            print("Invalid date format. Use YYYY-MM-DD. Try again.")
            continue

        # Confirm creation
        confirm = input(f"Are you sure you want to create event '{event_name}' on {event_date}? (Y/N): ").strip().upper()
        if confirm != "Y":
            print("Event creation cancelled.\n")
            return
        break

    # Send request to server
    response = requests.post(f'{server_url}/events', json={"name": event_name, "date": event_date})
    data = response.json()

    # Display clean output
    if response.status_code == 201:
        event = data['event']
        print("\nEvent Created Successfully!\n")
        print(f"Event Name : {event['name']}")
        print(f"Event Date : {event['date']}")
        print(f"Event ID   : {event['id']}\n")
    else:
        print(data.get("message", "Failed to create event"))

# ---------- LIST EVENTS ----------
def list_events():
    response = requests.get(f'{server_url}/events')
    events = response.json()
    if events:
        print(" Events:")
        for event in events:
            print(f"- [{event['id']}] {event['name']} on {event['date']} ({event['registrations_count']} registered students)")
    else:
        print("No events found.")

# ---------- REGISTER STUDENT ----------
def register_student():
    list_events()  # show events first

    # Validate event ID input
    while True:
        event_id_input = input("Enter event ID to register for: ").strip()
        if not event_id_input.isdigit():
            print("Invalid input. Enter a valid number.")
            continue
        event_id = int(event_id_input)
        break

    # Validate student name input
    while True:
        student_name = input("Enter student name: ").strip()
        if not student_name:
            print("Student name cannot be empty. Try again.")
            continue
        break

    # Send registration request
    response = requests.post(f'{server_url}/events/{event_id}/register', json={"name": student_name})
    data = response.json()

    # Display output
    if response.status_code == 200:
        event = data['event']
        print("\nStudent Registration Successful!\n")
        print(f"Student Name : {student_name}")
        print(f"Event Name   : {event['name']}")
        print(f"Event ID     : {event['id']}\n")
    else:
        print(data["message"])


# ---------- VIEW REGISTERED STUDENTS ----------
def view_registrations():
    list_events()
    while True:
        event_id_input = input("Enter the ID of the event to view registered students: ").strip()
        if not event_id_input.isdigit():
            print(" Invalid input. Enter a valid number.")
            continue
        event_id = int(event_id_input)
        break

    response = requests.get(f'{server_url}/events/{event_id}/registrations')
    data = response.json()
    if 'students' in data:
        print(f"\n Students registered for '{data['event_name']}':")
        if data['students']:
            for student in data['students']:
                print(f"- {student}")
        else:
            print("No students registered yet.")
    else:
        print(data['message'])

# ---------- MAIN MENU ----------
def menu():
    print("Welcome! Please log in first.")
    login()  # prompt login immediately

    while True:
        print("\n--- MENU ---")
        print("1. Create Event")
        print("2. List Events")
        print("3. Register Student")
        print("4. View Registered Students")
        print("5. Exit")
        choice = input("Choose: ").strip()

        if choice == "1":
            create_event()
        elif choice == "2":
            list_events()
        elif choice == "3":
            register_student()
        elif choice == "4":
            view_registrations()
        elif choice == "5":
            print("END!")
            break
        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    menu()

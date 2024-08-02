import pickle
import sys
from pathlib import Path
from collections import UserDict
from datetime import datetime, timedelta

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    def __init__(self, value):
        super().__init__(value)
    
class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Телефон не містить 10 чисел")
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value):
        try:
            birthday_date = datetime.strptime(value, "%d.%m.%Y")
            super().__init__(birthday_date)
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

    def __str__(self):
        return self.value.strftime("%d.%m.%Y")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if p.value != phone]

    def edit_phone(self, old_phone, new_phone):
        for phone in self.phones:
            if phone.value == old_phone:
                phone.value = new_phone
                break

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p.value
        return None
    
    def add_birthday(self, date):
        self.birthday = Birthday(date)

    def __str__(self):
        phones = '; '.join(p.value for p in self.phones)
        return f"Contact name: {self.name.value}, phones: {phones}, birthday: {self.birthday}"

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

def save_data(book, filename="book.txt"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="book.txt"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()  

class InvalidCommand(Exception):
    pass

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Give me name and phone please."
        except KeyError:
            return "Give me name and phone please."
        except IndexError:
            return "Give me name and phone please."
        except Exception as e:
            return f"Error: {e}"
    return inner

@input_error
def add_contact(args, contacts):
    name, phone, *_ = args
    record = contacts.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        contacts.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def change_contact(args, contacts):
    name, old_phone, new_phone = args
    record = contacts.find(name)
    if record is None:
        return f"name {name} not found"
    record.edit_phone(old_phone, new_phone)
    return "Contact updated."

@input_error
def show_phone(args, contacts):
    name, = args
    record = contacts.find(name)
    if record is None:
        return f"name {name} not found"
    return f"{record}"

@input_error
def show_all(contacts):
    res = [f"{key} {value}" for key, value in contacts.items()]
    return "\n".join(res)

@input_error
def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, args

@input_error
def add_birthday(args, contacts):
    name, birthday, *_ = args
    record = contacts.find(name)
    if record is None:
        return f"name {name} not found"
    record.add_birthday(birthday)
    return "Birthday added."

@input_error
def show_birthday(args, contacts):
    name, = args
    record = contacts.find(name)
    if record is None or record.birthday is None:
        return f"No birthday for {name}"
    return f"{name} birthday is {record.birthday}"

@input_error
def birthdays(args, contacts):
    today = datetime.today()
    next_week = today + timedelta(days=7)
    upcoming_birthdays = []
    for record in contacts.values():
        if record.birthday:
            birthday_this_year = record.birthday.value.replace(year=today.year)
            if today <= birthday_this_year <= next_week:
                upcoming_birthdays.append(f"{record.name.value}: {record.birthday}")
    return "\n".join(upcoming_birthdays)

def main():
    contacts = load_data()

    print("Welcome to the assistant bot! \n \
    - add [ім'я] [новий номер телефону] \n \
    - change [ім'я] [старий номер телефону] [новий номер телефону] \n \
    - phone [ім'я] \n \
    - all \n \
    - add-birthday [ім'я] [дата] \n \
    - show-birthday [ім'я] \n \
    - birthdays [кількість днів] \n \
    - close or exit")

    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)
        if command in ["close", "exit"]:
            save_data(contacts)
            print("Good bye!")
            break      
        elif command == "hello":
            print("How can I help you?")      
        elif command == "add":
            print(add_contact(args, contacts))           
        elif command == "change":
            print(change_contact(args, contacts))       
        elif command == "phone":
            print(show_phone(args, contacts))         
        elif command == "all":
            print(show_all(contacts))
        elif command == "add-birthday":
            print(add_birthday(args, contacts))
        elif command == "show-birthday":
            print(show_birthday(args, contacts))
        elif command == "birthdays":
            print(birthdays(args, contacts))           
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()
import sqlite3
from bs4 import BeautifulSoup
import requests

# Function to create a connection to SQLite database
def create_connection():
    conn = None
    try:
        conn = sqlite3.connect('TF2_weapons.db')  # Database will be created if it doesn't exist
        print("Connection to SQLite DB successful")
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
    return conn

# Function to create the weapons table
def create_table(conn):
    try:
        cursor = conn.cursor()
        # Drop the existing table if it exists
        cursor.execute('DROP TABLE IF EXISTS weapons')
        
        # Create the table with the new schema
        sql_create_table = '''
        CREATE TABLE IF NOT EXISTS weapons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            class TEXT NOT NULL,
            slot TEXT NOT NULL
        );
        '''
        cursor.execute(sql_create_table)
        print("Table created successfully")
    except sqlite3.Error as e:
        print(f"Error creating table: {e}")

# Function to insert weapon data into the table
def insert_weapon(conn, weapon):
    try:
        sql_insert_weapon = '''
        INSERT INTO weapons (name, class, slot)
        VALUES (?, ?, ?);
        '''
        cursor = conn.cursor()
        cursor.execute(sql_insert_weapon, weapon)
        conn.commit()
        #print(f"Weapon {weapon} inserted successfully")
    except sqlite3.Error as e:
        print(f"Error inserting ability: {e}")    

# Function to scrape weapon data from the given URL
def scrape_data(conn, url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    current_class = None
    current_slot = None

    # Loop over each element in the page
    for header in soup.find_all(['h2', 'h3', 'table']):
        if header.name == 'h2':
            # Extract the class name from the 'id' of the <h2> tag
            class_header = header.find('span', {'class': 'mw-headline'})
            if class_header:
                current_class = class_header.get('id')

        elif header.name == 'h3':
            # Extract the slot name from the 'id' of the <h3> tag
            slot_header = header.find('span', {'class': 'mw-headline'})
            if slot_header:
                current_slot = slot_header.get('id')

        elif header.name == 'table' and current_class and current_slot:
            # Check if the current class is Spy and the current slot is PDA or PDA2
            if current_class == "Spy" and "PDA" in current_slot:
                # Skip the first row only for Spy's PDA and PDA2
                for row in header.find_all('tr')[1:]:  # Skip first row
                    weapon_cell = row.find('th')
                    if weapon_cell:
                        weapon_link = weapon_cell.find('a', title=True)
                        if weapon_link:
                            weapon_name = weapon_link['title']
                            weapon_name = weapon_name.replace("_", " ")
                            weapon_name = weapon_name.strip()
                            current_class = current_class.replace("_", " ")
                            current_class = current_class.strip()
                            current_slot = current_slot.replace("_", " ")
                            current_slot = current_slot.strip()
                            temp_string = current_slot
                            while temp_string.isalpha() == False:
                                temp_string = current_slot[0:len(temp_string)-1]
                            current_slot = temp_string
                            # Insert weapon data into the database
                            insert_weapon(conn, (weapon_name, current_class, current_slot))
            else:
                # For other classes and slots, skip the first two rows
                for row in header.find_all('tr')[2:]:  # Skip first two rows
                    hasAlreadyInsertedPDAs = False
                    if "PDA" in current_slot and current_class == "Engineer" and hasAlreadyInsertedPDAs == False:
                        insert_weapon(conn, ("Construction PDA", current_class, "PDA"))
                        insert_weapon(conn, ("Destruction PDA", current_class, "PDA"))
                        hasAlreadyInsertedPDAs = True
                        continue
                    weapon_cell = row.find('th')
                    if weapon_cell:
                        weapon_link = weapon_cell.find('a', title=True)
                        if weapon_link:
                            weapon_name = weapon_link['title']
                            weapon_name = weapon_name.replace("_", " ")
                            weapon_name = weapon_name.strip()
                            current_class = current_class.replace("_", " ")
                            current_class = current_class.strip()
                            current_slot = current_slot.replace("_", " ")
                            current_slot = current_slot.strip()
                            temp_string = current_slot
                            while temp_string.isalpha() == False:
                                temp_string = current_slot[0:len(temp_string)-1]
                            current_slot = temp_string
                            # Insert weapon data into the database
                            insert_weapon(conn, (weapon_name, current_class, current_slot))

                        
def remove_duplicates(conn):
    try:
        cursor = conn.cursor()

        # SQL query to remove duplicates
        sql_remove_duplicates = '''
        WITH cte AS (
            SELECT id, ROW_NUMBER() OVER (PARTITION BY name, class, slot ORDER BY id) AS rn
            FROM weapons
        )
        DELETE FROM weapons
        WHERE id IN (
            SELECT id FROM cte WHERE rn > 1
        );
        '''

        cursor.execute(sql_remove_duplicates)
        conn.commit()
        print("Duplicates removed successfully")

    except sqlite3.Error as e:
        print(f"Error removing duplicates: {e}")

# Function to print the weapons table
def print_table(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name, class, slot FROM weapons ORDER BY class")

        rows = cursor.fetchall()
        previous_class = None

        for row in rows:
            weapon_name, weapon_class, weapon_slot = row

            # Check if the class has changed, print a new line if it has
            if weapon_class != previous_class:
                if previous_class is not None:
                    print()  # Print a new line when the class changes
                print(f"Class: {weapon_class}")

            # Print the weapon details
            print(f"  Slot: {weapon_slot}, Weapon: {weapon_name}")
            
            # Update the previous_class for the next iteration
            previous_class = weapon_class

    except sqlite3.Error as e:
        print(f"Error reading from table: {e}")
        
def update_duplicate_weapons(conn):
    # Get all weapons from the database
    weapons = conn.execute("SELECT id, name, class, slot FROM weapons").fetchall()
    
    # Create a dictionary to track weapon counts
    weapon_count = {}

    for weapon in weapons:
        weapon_name = weapon[1] # Index 1 corresponds to 'name'
        weapon_class = weapon[2] # Index 2 corresponds to 'class'
        weapon_slot = weapon[3]

        # Create a key for the weapon name
        if weapon_name not in weapon_count:
            weapon_count[weapon_name] = []

        # Append the class to the list of classes for this weapon
        weapon_count[weapon_name].append(weapon_class)

    # Update weapon names for duplicates
    for weapon_name, classes in weapon_count.items():
        strBuilder = ""
        if len(classes) > 1:  # Only modify if there are duplicates
            
            for weapon_class in classes:
                strBuilder += weapon_class + ", "
                
            strBuilder = strBuilder[0:len(strBuilder)-2]
            weapon = (weapon_name, strBuilder, weapon_slot)
            
            conn.execute("DELETE FROM weapons WHERE name = ?", [weapon_name])                    
            insert_weapon(conn, weapon)
            
            #print(weapon_name, strBuilder)
            
            '''
            for weapon_class in classes:
                # Format the new name with the class
                new_weapon_name = f"{weapon_name} ({weapon_class})"
                
                # Update the database for each weapon with this class
                conn.execute("UPDATE weapons SET name = ? WHERE name = ? AND class = ?", (new_weapon_name, weapon_name, weapon_class))
                
            '''

    conn.commit()  # Commit the changes to the database


# Main workflow
def main():
    # Create a database connection
    conn = create_connection()    
    
    if conn is not None:
        # Create the table
        create_table(conn)

        # Scrape the data
        scrape_data(conn, 'https://wiki.teamfortress.com/wiki/Weapons')
        
        remove_duplicates(conn)
        
        update_duplicate_weapons(conn)
        
        print_table(conn)

        # Close the connection
        conn.close()
    else:
        print("Error making connection")

if __name__ == '__main__':
    main()

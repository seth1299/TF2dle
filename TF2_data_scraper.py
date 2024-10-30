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
            slot TEXT NOT NULL,
            ammo TEXT NOT NULL
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
        INSERT INTO weapons (name, class, slot, ammo)
        VALUES (?, ?, ?, ?);
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
    ammo = None
    loaded_ammo = None
    carried_ammo = None

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
                            ammo = "N/A"
                                
                            # Insert weapon data into the database
                            insert_weapon(conn, (weapon_name, current_class, current_slot, ammo))
            else:
                # For other classes and slots, skip the first two rows
                for row in header.find_all('tr')[2:]:  # Skip first two rows
                    hasAlreadyInsertedPDAs = False
                    if "PDA" in current_slot and current_class == "Engineer" and hasAlreadyInsertedPDAs == False:
                        insert_weapon(conn, ("Construction PDA", current_class, "PDA", "N/A"))
                        insert_weapon(conn, ("Destruction PDA", current_class, "PDA", "N/A"))
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
                            # Find all <td> elements after the weapon name
                            td_elements = row.find_all('td')
                            
                            if current_slot == "Melee":
                                ammo = "N/A"
                            elif (current_class == "Heavy" and current_slot == "Primary") or (weapon_name == "Widowmaker" or weapon_name == "Short Circuit"):
                                ammo = 200
                            elif (current_class == "Pyro" and current_slot != "Melee"):
                                if weapon_name == "Flare Gun" or weapon_name == "Detonator" or weapon_name == "Scorch Shot":
                                    ammo = "1, 16"
                                elif weapon_name != "Dragon's Fury" and current_slot == "Primary":
                                    ammo = "200, N/A"
                                elif weapon_name == "Dragon's Fury":
                                    ammo = "40, N/A"
                                elif weapon_name == "Thermal Thruster":
                                    ammo = "2, N/A"
                                elif weapon_name == "Gas Passer" or weapon_name == "Manmelter":
                                    ammo = "1, ∞"
                            elif weapon_name == "Ali Baba's Wee Booties" or weapon_name == "Bootlegger" or weapon_name == "Giger Counter" or weapon_name == "Sandvich" or weapon_name == "Robo-Sandvich" or weapon_name == "Dalokohs Bar" or weapon_name == "Fishcake" or weapon_name == "Razorback":
                                ammo = "N/A"
                            elif weapon_name == "Crusader's Crossbow":
                                ammo = "1, 38"
                            elif current_class == "Sniper" and current_slot != "Melee":
                                if weapon_name == "Huntsman" or weapon_name == "Fortified Compound":
                                    ammo = "1, 12"
                                elif weapon_name == "Jarate" or weapon_name == "Self-Aware Beauty Mark" or weapon_name == "Razorback":
                                    ammo = "1, ∞"
                                elif weapon_name == "SMG":
                                    ammo = "25, 75"
                                elif weapon_name == "Cleaner's Carbine":
                                    ammo = "20, 75"
                                elif current_slot == "Primary":
                                    ammo = "1, 25"
                                else:
                                    ammo = "N/A"
                            elif weapon_name != "Widowmaker" and weapon_name != "Short Circuit" and current_slot != "Melee" and len(td_elements) >= 2:  # Ensure there are at least two <td> elements                                                                
                                if 'rowspan' in td_elements[0].attrs:
                                    # Reuse the existing loaded_ammo and carried_ammo
                                    ammo = f"{loaded_ammo}, {carried_ammo}"
                                else:
                                    # Extract and store the new ammo values
                                    loaded_ammo = td_elements[1].get_text(strip=True)
                                    carried_ammo = td_elements[2].get_text(strip=True)
                                    ammo = f"{loaded_ammo}, {carried_ammo}"

                                if "N/A" in ammo:
                                    ammo = "N/A"

                                # Debug print statements (can be removed in production)
                                #print(f"Weapon: {weapon_name}, Ammo: {ammo}")
                            else:
                                ammo = f"{loaded_ammo}, {carried_ammo}"
                            # Insert weapon data into the database
                            insert_weapon(conn, (weapon_name, current_class, current_slot, ammo))

                        
def remove_duplicates(conn):
    try:
        cursor = conn.cursor()

        # SQL query to remove duplicates
        sql_remove_duplicates = '''
        WITH cte AS (
            SELECT id, ROW_NUMBER() OVER (PARTITION BY name, class, slot, ammo ORDER BY id) AS rn
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
        cursor.execute("SELECT name, class, slot, ammo FROM weapons")

        rows = cursor.fetchall()
        previous_class = None
        previous_slot = None

        for row in rows:
            weapon_name, weapon_class, weapon_slot, weapon_ammo = row

            # Check if the class has changed, print a new line if it has
            if weapon_class != previous_class:
                if previous_class is not None:
                    print()  # Print a new line when the class changes
                print(f"Class: {weapon_class}")
                
            if previous_slot != weapon_slot and previous_slot != None:
                print()
                print(f"Slot: {weapon_slot}")
                print()
            elif previous_slot == None and previous_slot != weapon_slot:
                print(f"Slot: {weapon_slot}")
                print()

            # Print the weapon details
            print(f"- {weapon_name}, Ammo: {weapon_ammo}")
            
            # Update the previous_class for the next iteration
            previous_class = weapon_class
            previous_slot = weapon_slot

    except sqlite3.Error as e:
        print(f"Error reading from table: {e}")
        
def update_duplicate_weapons(conn):
    # Get all weapons from the database
    weapons = conn.execute("SELECT id, name, class, slot, ammo FROM weapons").fetchall()
    
    # Create a dictionary to track weapon counts with slots and ammo
    weapon_count = {}

    for weapon in weapons:
        weapon_name = weapon[1]  # Index 1 corresponds to 'name'
        weapon_class = weapon[2]  # Index 2 corresponds to 'class'
        weapon_slot = weapon[3]   # Index 3 corresponds to 'slot'
        weapon_ammo = weapon[4]   # Index 4 corresponds to 'ammo'

        # Create a key for the weapon name
        if weapon_name not in weapon_count:
            weapon_count[weapon_name] = []

        # Append the class, slot, and ammo as a tuple to the list of classes for this weapon
        weapon_count[weapon_name].append((weapon_class, weapon_slot, weapon_ammo))

    # Update weapon names for duplicates
    for weapon_name, class_slot_list in weapon_count.items():
        if len(class_slot_list) > 1:  # Only modify if there are duplicates
            # Build the combined class string
            combined_classes = ", ".join([cls_slot[0] for cls_slot in class_slot_list])
            
            # Use the slot and ammo from the first occurrence
            weapon_slot = class_slot_list[0][1]
            weapon_ammo = class_slot_list[0][2]

            # Delete all records with the same name
            conn.execute("DELETE FROM weapons WHERE name = ?", [weapon_name])

            # Insert the single record with combined classes, correct slot, and ammo
            if weapon_name not in ["Shotgun", "B.A.S.E. Jumper"]:
                conn.execute(
                    "INSERT INTO weapons (name, class, slot, ammo) VALUES (?, ?, ?, ?)",
                    (weapon_name, combined_classes, weapon_slot, weapon_ammo)
                )
            else:
                # Special handling for Shotgun and B.A.S.E. Jumper
                conn.execute(
                    "INSERT INTO weapons (name, class, slot, ammo) VALUES (?, ?, ?, ?)",
                    (weapon_name, combined_classes, "Primary, Secondary", weapon_ammo)
                )

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

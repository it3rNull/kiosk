import csv
import sqlite3

def export_table_to_csv(table_name, csv_file):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Fetch all rows from the table
    cursor.execute(f"select * from {table_name}")
    rows = cursor.fetchall()
    
    # Get the column names
    column_names = [description[0] for description in cursor.description]
    
    # Write data to the CSV file
    with open(csv_file, 'w', newline='') as file:
        writer = csv.writer(file)
        
        # Write the column headers
        writer.writerow(column_names)
        
        # Write the data rows
        writer.writerows(rows)
    
    cursor.close()
    conn.close()

# Usage example
export_table_to_csv('payments', 'output.csv')
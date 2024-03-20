import streamlit as st
import psycopg2

# Establish database connection
conn = psycopg2.connect(
    dbname="chat_history",
    user="postgres",
    password="0900",
    host="localhost",
    port="5432"
)

cursor = conn.cursor()

def delete_row(mobile_number):
    try:
        cursor.execute("SELECT * FROM d3 WHERE mobile_number = %s", (mobile_number,))
        row = cursor.fetchone()
        if row is None:
            st.error(f"Mobile number {mobile_number} does not exist.")
        else:
            cursor.execute("DELETE FROM d3 WHERE mobile_number = %s", (mobile_number,))
            conn.commit()
            st.success(f"Movie_Ticket is cancelled successfully.")
    except Exception as e:
        st.error(f"Error deleting data: {e}")

def main():
    mobile_number = st.text_input("Enter Mobile Number:")
    if st.button("Cancel_Ticket"):
        delete_row(mobile_number)

if __name__ == "__main__":
    main()

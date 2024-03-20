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

def calculate_price(num_tickets):
    ticket_prices = {1: 200, 2: 400, 3: 600, 4: 800, 5: 1000}
    return ticket_prices.get(num_tickets, 0)

def main():
    mobile_number = st.text_input("Enter Mobile Number:")

    # Check if mobile number exists when the user enters it
    if mobile_number:
        cursor.execute("SELECT * FROM d3 WHERE mobile_number = %s", (mobile_number,))
        row = cursor.fetchone()
        if row is None:
            st.error(f"Mobile number {mobile_number} does not exist.")
        else:
            st.success(f"Mobile number {mobile_number} exists.")
            language_options = ['English', 'Kannada', 'Hindi']
            language = st.selectbox("Select language", language_options)

            movie_experience_options = ['2D movie', '3D movie']
            movie_experience = st.selectbox("Select movie experience", movie_experience_options)

            movie_category_options = ['Action', 'Comedy', 'Drama', 'Thriller']
            movie_category = st.selectbox("Select movie category", movie_category_options)

            movie_selection_options = []
            if movie_category == 'Action':
                movie_selection_options = ['Avengers Endgame', 'The Dark Knight', 'Inception', 'John Wick 4']
            elif movie_category == 'Comedy':
                movie_selection_options = ['Dumb and Dumber', 'The Hangover', 'Johnny English Reborn', 'We are the Millers']
            elif movie_category == 'Drama':
                movie_selection_options = ['The Shawshank Redemption', 'Forrest Gump', 'The Godfather', 'Titanic']
            elif movie_category == 'Thriller':
                movie_selection_options = ['Interstellar', 'The Matrix', 'Jurassic Park', 'Avatar The Way of Water']

            movie_selection = st.selectbox("Select movie", movie_selection_options)

            showtime_selection_options = ['4:00 PM', '6:30 PM', '8:00 PM', '10:15 PM']
            showtime_selection = st.selectbox("Select showtime", showtime_selection_options)

            theatre_selection_options = ['Aero Theatre', 'Vista Theatre', 'Regal Cinemas', 'Universal Cinemas']
            theatre_selection = st.selectbox("Select theatre", theatre_selection_options)

            seating_position_options = ['Standard', 'VIP', 'Balcony']
            seating_position = st.selectbox("Select seating position", seating_position_options)

            num_tickets_existing = row[8]  

            num_tickets_options = [1, 2, 3, 4, 5]
            num_tickets = st.selectbox("Select number of tickets", num_tickets_options, index=num_tickets_options.index(num_tickets_existing))

            # Calculate the new price and the difference
            new_price = calculate_price(num_tickets)
            original_price = row[9]  
            price_difference = new_price - original_price

            st.success(f"Total Price: {new_price}")
            if price_difference > 0:
                 st.info(f"pay the remaining amount: {price_difference}")
            elif price_difference < 0:
                st.info(f"Your amount {abs(price_difference)} will be refunded")

     

            if st.button("Update"):
                # Update record with all the fields
                sql = """UPDATE d3 
                         SET language = %s, movie_experience = %s, 
                             movie_category = %s, movie_selection = %s, 
                             showtime_selection = %s, theatre_selection = %s, 
                             seating_position = %s, num_tickets = %s, price = %s
                         WHERE mobile_number = %s"""
                val = (language, movie_experience, movie_category, movie_selection,
                       showtime_selection, theatre_selection, seating_position,
                       num_tickets, new_price, mobile_number)
                cursor.execute(sql, val)
                conn.commit()

                st.success("Record Updated Successfully!!!")

if __name__ == "__main__":
    main()

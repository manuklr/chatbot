import streamlit as st
from streamlit_chat import message
import nltk
import random
import json
import pickle
import numpy as np
from keras.models import load_model
from nltk.stem import WordNetLemmatizer
import psycopg2




st.set_page_config(
    page_title="MovieBooking_Bot",
    page_icon="🤖",
    
)

# Function to clean up sentences
def clean_up_sentences(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words

# Function to create a bag of words
def bag_of_words(sentence, words, ignore_letters):
    sentence_words = clean_up_sentences(sentence)
    bag = [0] * len(words)
    for w in sentence_words:
        for i, word in enumerate(words):
            if word == w:
                bag[i] = 1
    return np.array(bag)

# Function to predict the class (intent)
def predict_class(sentence, model, words, classes, ignore_letters):
    bow = bag_of_words(sentence, words, ignore_letters)
    res = model.predict(np.array([bow]))[0]
    ERROR_THRESHOLD = 0.7  # Adjusted threshold to 0.7
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({'intent': classes[r[0]], 'probability': str(r[1])})
    return return_list


import re




# Function to get a response based on the detected intent, with fuzzy matching
import random
from fuzzywuzzy import process

def get_response(user_input,intents_list, intents_json, session_state):
    if intents_list:
        tag = intents_list[0]['intent']
        list_of_intents = intents_json['intents']
        matched_intent = None

        # Perform fuzzy matching to find the closest intent match
        intent_names = [intent['tag'] for intent in list_of_intents]
        closest_match = process.extractOne(tag, intent_names)

        # Check if the closest match exceeds a certain threshold
        if closest_match[1] >= 80:  # Adjust the threshold as needed
            closest_intent_name = closest_match[0]
            for intent in list_of_intents:
                if intent['tag'] == closest_intent_name:
                    matched_intent = intent
                    break

        if matched_intent:
            response = random.choice(matched_intent['responses'])
            # Remove words after ":"
            result = response.split(":")[0].strip()
            return result


    # If no matching intent found, use session state tag for response
    if session_state.tag == 'Greeting':
        response = "Please choose the 'Language' from the options above."
    elif session_state.tag == 'Movie language choice':
        response = "Please choose the 'Movie_Experience' from the options above."
    elif session_state.tag == 'Movie Experience Choice':
        response = "Please choose the 'Movie_Category' from the options above."
    elif session_state.tag in ['Action Movie Category Choice', 'Comedy Movie Category Choice', 'Drama Movie Category Choice', 'Science Fiction Movie Category Choice']:
        response = "Please choose the 'Movie_Name' from the options above."
    elif session_state.tag == 'Movie Selection':
        response = "Please choose the 'Showtime' from the options above."
    elif session_state.tag == 'Showtime Selection':
        response = "Please choose the 'Theatre' from the options above."
    elif session_state.tag == 'Theatre Selection':
        response = "Please choose the 'Seating_Position' from the options above."
    elif session_state.tag == 'Seating Position Selection':
        response = "Please choose the 'Number_Of_Tickets' from the options above."
    else:
        response = "Sorry I didn't understand the given input, please try again"
    return response




# Function to get response options based on the detected intent
def get_response_options(intents_list, intents_json):
    result = ""

    if intents_list:
        tag = intents_list[0]['intent']
        list_of_intents = intents_json['intents']
        for i in list_of_intents:
            if i['tag'] == tag and 'responses' in i and i['responses']:
                options_split = i['responses'][0].split("\nOptions")
                if len(options_split) > 1:
                    result = options_split[1].strip().replace("Options", "")
                    # Remove "Response Options for Interaction" line
                    result = result.replace("Response Options for Interaction", "")
                break

    return result


import streamlit as st


def fetch_data():
    print("Fetching data from the database........")

    try:
        print("Fetching data...")
        # Fetch data from the database by joining d3 and d4 tables
        cursor.execute('''
            SELECT d3.*, d4.price
            FROM d3
            JOIN d4 ON d3.num_tickets = d4.no_of_tickets
            ORDER BY d3.id DESC
            LIMIT 1
        ''')
        fetched_data = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]

        if fetched_data:
            # Store fetched data in a dictionary
            fetched_data_dict = {}
            for i in range(len(column_names)):
                value = fetched_data[0][i]
                # Handle string representation of None
                if value == 'None':
                    value = None
                # Handle string representation of numerical values
                elif isinstance(value, str) and value.replace('.', '', 1).isdigit():
                    value = float(value)
                fetched_data_dict[column_names[i]] = value

            # Insert the price into d3 table
            if 'price' in fetched_data_dict:
                cursor.execute('''
                    UPDATE d3
                    SET price = %s
                    WHERE id = %s
                ''', (fetched_data_dict['price'], fetched_data_dict['id']))
                conn.commit()

            return fetched_data_dict  # Return the fetched data
        else:
            st.warning("No data found.")
            return None

    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None


# Loading the model and data
lemmatizer = WordNetLemmatizer()
intents = json.loads(open("intense.json").read())
words = pickle.load(open('words.pkl', 'rb'))
classes = pickle.load(open('classes.pkl', 'rb'))
model = load_model('chatbotmodel.h5')
ignore_letters = ["?", "!", ".", ","]


conn = psycopg2.connect(
    dbname="chat_history",
    user="postgres",
    password="0900",
    host="localhost",
    port="5432"
)

cursor = conn.cursor()



# Ensure table creation is only done if it doesn't exist     
cursor.execute('''
    CREATE TABLE if NOT EXISTS d3 (
        id SERIAL PRIMARY KEY,       
        language VARCHAR,
        movie_experience VARCHAR,
        movie_category VARCHAR,
        movie_selection VARCHAR,
        showtime_selection VARCHAR,
        theatre_selection VARCHAR,
        seating_position VARCHAR,
        num_tickets INTEGER,
        price INTEGER,
        mobile_number BIGINT                 
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS d4 (
        no_of_tickets INTEGER PRIMARY KEY,
        price INTEGER
    )
''')


conn.commit()


import psycopg2
from psycopg2 import IntegrityError

def insert_data(language, movie_experience, movie_category, movie_selection, showtime_selection, theatre_selection, seating_position, num_tickets, mobile_number, conn, cursor):
    try:
        # Check if mobile number already exists in the database
        cursor.execute("""
            SELECT id FROM d3 WHERE mobile_number = %s
        """, (mobile_number,))
        existing_record = cursor.fetchone()

        if existing_record:
            st.error("Mobile number already exist.")
            # Handle the case where the mobile number already exists
            return
        else:
            # Insert new record into the database
            cursor.execute("""
                INSERT INTO d3 (language, movie_experience, movie_category, movie_selection, showtime_selection, theatre_selection, seating_position, num_tickets, mobile_number)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (language, movie_experience, movie_category, movie_selection, showtime_selection, theatre_selection, seating_position, num_tickets, mobile_number))
            conn.commit()
            #st.write(f"Mobile Number saved: {mobile_number}")
            st.success("enter submit for the details")
    except IntegrityError as e:
        conn.rollback()
        print(f"Error inserting data: {e}")




# Inside the main function

def main():
    session_state = st.session_state

    if 'tag' not in session_state:
        session_state.tag = None

    if 'chat_history' not in session_state:
        session_state.chat_history = []

    if 'response_options' not in session_state:
        session_state.response_options = []

    if 'language' not in session_state:
        session_state.language = None

    if 'movie_experience' not in session_state:
        session_state.movie_experience = None

    if 'movie_category' not in session_state:
        session_state.movie_category = None

    if 'movie_selection' not in session_state:
        session_state.movie_selection = None

    if 'showtime_selection' not in session_state:
        session_state.showtime_selection = None

    if 'theatre_selection' not in session_state:
        session_state.theatre_selection = None

    if 'seating_position' not in session_state:
        session_state.seating_position = None

    if 'num_tickets' not in session_state:
        session_state.num_tickets = None

    if 'mobile_number' not in session_state:
        session_state.mobile_number = None    

    # Flag to track if data is already inserted
    data_inserted = False

    # Check if data is already inserted
    if all([session_state.language, session_state.movie_experience, session_state.movie_category, session_state.movie_selection, session_state.showtime_selection, session_state.theatre_selection, session_state.seating_position, session_state.num_tickets, session_state.mobile_number]):
         data_inserted = True

    for i, chat in enumerate(session_state.chat_history):
        if chat["User"]:
            message(chat["User"], is_user=True, key=f"user_{i}")  # Assign unique key for user messages
        if chat["Bot"]:
            message(chat["Bot"], key=f"bot_{i}")

        if i < len(session_state.response_options):
            response_options = session_state.response_options[i]
            if response_options:
                options_table = [{"Option": option} for option in response_options.split("\n")]

                st.markdown(
                    f'<style>table {{ width: 30%; border-collapse: collapse; }} th, td {{ border: 50px solid black; padding: 8px; }} </style>',
                    unsafe_allow_html=True
                )

                table_html = '<table><tr><th>Option</th></tr>'
                for option in options_table:
                    table_html += f"<tr><td>{option['Option']}</td></tr>"
                table_html += "</table>"

                # Display the HTML table
                st.markdown(table_html, unsafe_allow_html=True)

    user_input = st.chat_input("User")

    # Process user input and ask questions when the button is clicked
    
    if user_input is not None:
        
        if user_input.lower() == 'exit':
           session_state.chat_history = []
           session_state.response_options = [] 
           st.success("Goodbye!")

        elif user_input.lower() =='proceed':
            st.success("enter your mobile number")
        
        elif  user_input.isdigit() and len(user_input) > 1:

            mobile_number_input = user_input
            if re.match(r'^[1-9]\d{9}$', mobile_number_input):
                session_state.mobile_number=mobile_number_input
                insert_data(session_state.language, session_state.movie_experience, session_state.movie_category, session_state.movie_selection, session_state.showtime_selection, session_state.theatre_selection, session_state.seating_position, session_state.num_tickets,session_state.mobile_number, conn, cursor)
            else:
                st.success("Invalid mobile number.")
        
    
               
        elif user_input.lower() == "cancel":
          
        # Remove the last inserted record from the database
           try:
            cursor.execute('''
                DELETE FROM d3
                WHERE id = (
                    SELECT id
                    FROM d3
                    ORDER BY id DESC
                    LIMIT 1
                )
            ''')
            conn.commit()
            st.success("your booking is cancelled.")
            session_state.chat_history = [] 
            empty_container = st.empty()
           except Exception as e:
            st.error(f"Error cancelling last inserted record: {e}")
            
           session_state.chat_history = [] 
           empty_container = st.empty()
         

        else:
            ints = predict_class(user_input, model, words, classes, ignore_letters)
            response = get_response(user_input,ints, intents, session_state)
            response_options = get_response_options(ints, intents)

            # Append user input and bot response to chat history
            session_state.chat_history.append({"User": user_input, "Bot": response})

            # Store response_options in session state
            session_state.response_options.append(response_options)

            # Process intents and insert data into the database only if not already inserted
            if not data_inserted:
                for intent in ints:
                    session_state.tag = intent['intent']
                    tag = intent['intent']

                    # Assign values to variables based on the tag
                    if tag == 'Movie language choice':
                        session_state.language = user_input
                    elif tag == 'Movie Experience Choice':
                        session_state.movie_experience = user_input
                    elif tag in ['Action Movie Category Choice', 'Comedy Movie Category Choice', 'Drama Movie Category Choice', 'Science Fiction Movie Category Choice']:
                        session_state.movie_category = user_input
                    elif tag == 'Movie Selection':
                        session_state.movie_selection = user_input
                    elif tag == 'Showtime Selection':
                        session_state.showtime_selection = user_input
                    elif tag == 'Theatre Selection':
                        session_state.theatre_selection = user_input
                    elif tag == 'Seating Position Selection':
                        session_state.seating_position = user_input
                        print(session_state.seating_position)
                    elif tag == 'Number of Tickets Selection':
                        session_state.num_tickets = int(user_input)
                     
                
                if all([session_state.language, session_state.movie_experience, session_state.movie_category, session_state.movie_selection, session_state.showtime_selection, session_state.theatre_selection, session_state.seating_position, session_state.num_tickets,session_state.mobile_number]):
                    print( session_state.language, session_state.movie_experience, session_state.movie_category, session_state.movie_selection, session_state.showtime_selection, session_state.theatre_selection, session_state.seating_position, session_state.num_tickets,session_state.mobile_number)
                    insert_data(tag, user_input, session_state.language, session_state.movie_experience, session_state.movie_category, session_state.movie_selection, session_state.showtime_selection, session_state.theatre_selection, session_state.seating_position, session_state.num_tickets,session_state.mobile_number, conn, cursor)

                    # Set data_inserted flag to True after insertion
                    data_inserted = True
            
            for intent in ints:
                    
                    tag = intent['intent']
                    if tag == 'details':

                      print("hello")
                      fetched_data = fetch_data()
                      print(fetched_data)
                      if fetched_data:   
                            data_response = "\n".join([f"{key}: {value}" for key, value in fetched_data.items()])
                    # Append the concatenated data to the chat history
                            session_state.chat_history.append({"User": "", "Bot": data_response})

            # Fetch data from the database
            

            # Clear input field and update elements
            st.text_input("", key="input_key")
            st.experimental_rerun()

if __name__ == '__main__':
    main()

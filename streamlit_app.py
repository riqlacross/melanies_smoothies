# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests

# Write directly to the app
st.title("Customize Your Smoothie! 🥤")
st.write("""
    Choose the fruits you want in your Smoothie!
""")

name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your smoothie will be: ", name_on_order)

# Snowflake connection setup
cnx = st.experimental_connection("snowflake")  # Use experimental_connection if st.connection is not available
session = cnx.session()

# Retrieve fruit options from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME')).collect()

# Display fruit options for selection
ingredients_list = st.multiselect("Choose up to 5 ingredients:", [row['FRUIT_NAME'] for row in my_dataframe])

# Check the number of selected ingredients
if len(ingredients_list) > 5:
    st.error('You can select a maximum of 5 ingredients.')
    ingredients_list = ingredients_list[:5]  # Keep only the first 5 selections if more than 5 are chosen

if ingredients_list:
    ingredients_string = ' '.join(ingredients_list)

    st.write(ingredients_string)

    my_insert_stmt = f"""
    INSERT INTO smoothies.public.orders(ingredients, name_on_order)
    VALUES ('{ingredients_string}', '{name_on_order}')
    """

    time_to_insert = st.button('Submit Order')
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f"{name_on_order}'s Smoothie is ordered!", icon="✅")

    # New section to display Fruityvice nutrition information for selected fruits
    st.write("### Fruityvice Nutrition Information for Selected Fruits")

    fruityvice_data = []
    for fruit in ingredients_list:
        response = requests.get(f"https://fruityvice.com/api/fruit/{fruit.lower()}")
        if response.status_code == 200:
            fruityvice_data.append(response.json())
        else:
            st.error(f"Failed to fetch data for {fruit}: {response.status_code}")

    if fruityvice_data:
        st.json(fruityvice_data)  # Display the JSON response for all selected fruits

        # Display the data as a dataframe
        import pandas as pd
        fv_df = pd.json_normalize(fruityvice_data)
        st.dataframe(data=fv_df, use_container_width=True)

from flask import Flask, render_template, request, jsonify
from PIL import Image
from pathlib import Path
from io import BytesIO
import cv2
import google.generativeai as genai
import pandas as pd
import os
import csv
import re
import googletrans
from googletrans import *
import json
import time
import matplotlib.pyplot as plt
import plotly.express as px

API_KEY = "AIzaSyAzTaIfYcArKhZ4Hh31CM5Tgi1UGb-bMOE"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-pro-vision')


safety_settings = [
    {
        "category": "HARM_CATEGORY_DANGEROUS",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE",
    },
]


app = Flask(__name__)

@app.route('/',  methods = ['GET','POST'])
def hello():
    start_time = time.time()
    total_rows = populate_data()
    csv_file_path = "data/new_entries.csv"
    # Read the CSV file
    names = []
    images = []
    prices = []
    count = 0
    with open(csv_file_path, 'r', encoding='utf-8') as file:
        csv_reader = csv.reader(file, delimiter=";")
        next(csv_reader)
        for row in csv_reader:
            if any(row):
                names.append(row[1])
                image_url = './static/Catalog Digitization/ONDC Test Data _ Images/Product Images/' + row[5]
                images.append(image_url)
                prices.append(row[4])
                count += 1

    
    end_time = time.time()
    elapsed_time = end_time - start_time
    throughput = total_rows / elapsed_time  # Rows processed per second
    
     # Create or append to a file to store throughput history
    throughput_history_file = 'static/throughput_history.csv'
    throughput_df = pd.DataFrame({'Timestamp': [time.strftime("%Y-%m-%d %H:%M:%S")], 'Throughput': [throughput]})
    
    if not os.path.exists(throughput_history_file):
        throughput_df.to_csv(throughput_history_file, sep=';', index=False)
    else:
        throughput_df.to_csv(throughput_history_file, sep=';', index=False, mode='a', header=False)

    # Generate an interactive line chart using Plotly
    history_df = pd.read_csv(throughput_history_file, sep=';')
    fig = px.line(history_df, x='Timestamp', y='Throughput', title='Throughput History')
    
    # Update x-axis layout for better readability
    fig.update_xaxes(tickangle=45, tickmode='linear')

    # Save the chart to a file (optional)
    fig.write_image('static/throughput_chart.png')
    return render_template('index.html', names = names, images = images, prices = prices, count = count, throughput=throughput)


def fetch_number_from_string(input_string):
    # Use regex to find the first number in the string
    match = re.search(r'\d+', input_string)
    
    if match:
        # Extract the matched number
        number = int(match.group())
        return number
    else:
        return None

@app.route('/product-form',  methods = ['GET','POST'])
def productForm():
    if request.method == 'POST':
        image_file = request.files['image']
        image_file_location = "static/upload.png" 
        image_file.save(image_file_location)
        with Image.open(image_file_location) as img:
            img.save(image_file_location)
    
    model = genai.GenerativeModel('gemini-pro-vision')
    image_path = image_file_location
    image = {
    'mime_type': 'image/png',
    'data': Path(image_path).read_bytes()
    }
    
    df = pd.read_csv('static/Catalog Digitization/final_merged.csv', sep=';')

    prompt = f"Find the SKU id from this dataframe {df}. response should contain the SKU id only."
    response = model.generate_content([image, prompt], safety_settings=safety_settings)
    response = fetch_number_from_string(response.text)
    result = response

    product_name = df[df['id'] == result]['name'].values[0] if result in df['id'].values else None
    product_category=  df[df['id'] == result]['category'].values[0] if result in df['id'].values else None
    product_sub =  df[df['id'] == result]['subcategory'].values[0] if result in df['id'].values else None
    product_image_path =  df[df['id'] == result]['image'].values[0] if result in df['id'].values else None
    product_price =  df[df['id'] == result]['price'].values[0] if result in df['id'].values else None
    product_qty =  df[df['id'] == result]['Qty'].values[0] if result in df['id'].values else None

    #add to new_entries
    file_path = 'data/new_entries.csv'
    df_existing = pd.read_csv(file_path, sep=';')

    if result not in df_existing['id'].values:
    # Create a new row with the specified values
        new_row = pd.DataFrame({
            'id': [result],
            'name': [product_name],
            'category': [product_category],
            'subcategory': [product_sub],
            'price': [product_price],
            'image': [product_image_path],
            'Qty' : [product_qty]
        })

        # Append the new row to the existing DataFrame
        df_existing = df_existing._append(new_row, ignore_index=True)

        # Save the updated DataFrame back to the CSV file with a custom separator ;
        df_existing.to_csv(file_path, sep=';', index=False)
        # Generate the URL for the CSV file
        csv_url = 'static/new_entries.csv'
    
    return render_template('product.html',product_qty = product_qty, product_name = product_name, sku_id = int(result), product_category = product_category,  product_price = product_price, product_sub = product_sub, product_image = 'static/upload.png')

def populate_data():
    df = pd.read_csv('static/Catalog Digitization/final_merged.csv', sep=';')

    new_entries = pd.DataFrame(columns=['id', 'name', 'category', 'subcategory', 'price', 'image', 'Qty'])

    total_rows = len(df)

    for _, row in df.iterrows():
        product_id = row['id']
        product_name = row['name']
        product_category = row['category']
        product_sub = row['subcategory']
        product_image_path = row['image']
        product_price = row['price']
        product_qty = row['Qty']

        new_row = pd.DataFrame({
            'id': [product_id],
            'name': [product_name],
            'category': [product_category],
            'subcategory': [product_sub],
            'price': [product_price],
            'image': [product_image_path],
            'Qty': [product_qty]
        })

        new_entries = pd.concat([new_entries, new_row], ignore_index=True)

    # Save the updated DataFrame back to the CSV file with a custom separator ;
    new_entries.to_csv('data/new_entries.csv', sep=';', index=False)
    return total_rows


@app.route('/view-form',  methods = ['GET','POST'])
def viewForm():
    if request.method == 'POST':
        image_url = request.form.get('image')
        image = image_url.replace('./static/Catalog Digitization/ONDC Test Data _ Images/Product Images/', '')
        #add to new_entries
        file_path = 'data/new_entries.csv'
        df = pd.read_csv(file_path, sep=';')
        product_id = df[df['image'] == image]['id'].values[0]
        product_category=  df[df['image'] == image]['category'].values[0]
        product_sub = df[df['image'] == image]['subcategory'].values[0]
        product_name = df[df['image'] == image]['name'].values[0]
        product_price =  df[df['image'] == image]['price'].values[0]
        product_qty =  df[df['image'] == image]['Qty'].values[0]
        
      
    return render_template('product.html', product_qty = product_qty, product_image = image_url, product_name = product_name, sku_id = product_id, product_category = product_category,  product_price = product_price, product_sub = product_sub )

@app.route('/process-audio', methods = ['GET','POST'])
def processAudio():
    #if request.method == 'POST':
    #audio_file = request.files['audio']
        #audio_file.save("static/" + audio_file.filename)
        #text = r.recognize_google(audio,language="en-US")
        #response = model.generate_content(text)
    return render_template('product.html')

@app.route("/chatbot", methods=['POST', 'GET'])
def chatbot():
    return render_template("chat.html")


if __name__ == '__main__':
    app.run(debug=True, port=5000)

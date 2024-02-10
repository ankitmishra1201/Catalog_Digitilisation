from flask import Flask, render_template, request, jsonify
from PIL import Image
from pathlib import Path
from io import BytesIO
import pytesseract
import cv2
import google.generativeai as genai
import pandas as pd
import os
import csv
import re
import googletrans
from googletrans import *
import json

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
                image_url = './static/Catalog Digitization/ONDC Test Data _ Images/Product Images/' + row[2]
                images.append(image_url)
                prices.append(row[5])
                count += 1

    return render_template('index.html', names = names, images = images, prices = prices, count = count)


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
            'image': [product_image_path]
        })

        # Append the new row to the existing DataFrame
        df_existing = df_existing._append(new_row, ignore_index=True)

        # Save the updated DataFrame back to the CSV file with a custom separator ;
        df_existing.to_csv(file_path, sep=';', index=False)
        # Generate the URL for the CSV file
        csv_url = 'static/new_entries.csv'
    
    return render_template('product.html',product_name = product_name, sku_id = int(result), product_category = product_category,  product_price = product_price, product_sub = product_sub, product_image = 'static/upload.png')


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
      
    return render_template('product.html', product_image = image_url, product_name = product_name, sku_id = product_id, product_category = product_category,  product_price = product_price, product_sub = product_sub )

@app.route('/process-audio', methods = ['GET','POST'])
def processAudio():
    if request.method == 'POST':
        audio_file = request.files['audio']
        #audio_file.save("static/" + audio_file.filename)
        #text = r.recognize_google(audio,language="en-US")
        #response = model.generate_content(text)
    return render_template('product.html', processed_audio = audio_file)


if __name__ == '__main__':
    app.run(debug=True)

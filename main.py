from transformers import AutoModelForCausalLM, AutoTokenizer
import pandas as pd
import google.generativeai as genai
import dotenv
import sqlite3
from transformers import pipeline
import re 
import speech_recognition as sr

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def sql_query(query: str):
    return pd.read_sql_query(query, connection).to_dict(orient='records')
    
ds = pd.ExcelFile('ds.xlsx')
refined_sheet = pd.read_excel(ds,'Refined')
connection = sqlite3.connect('mydatabase.db')
refined_sheet.to_sql('mytable', connection, if_exists='replace')


recognizer = sr.Recognizer()


audio_file = "pass the audio file" 
with sr.AudioFile(audio_file) as source:
    print("Listening...")
    audio = recognizer.record(source)
    
try:

    print("Converting speech to text...")
    
    text = recognizer.recognize_sphinx(audio)
    print("You said: " + text)

except sr.UnknownValueError:
    print("Sphinx could not understand the audio")

except sr.RequestError as e:
    print(f"Sphinx error; {e}")
    
    
system_prompt = """
You are an expert SQL analyst. When appropriate, generate SQL queries based on the user question and the database schema.
When you generate a query, use the 'sql_query' function to execute the query on the database and get the results.
Then, use the results to answer the user's question.

database_schema: [
    {
        table: 'mytable',
        columns: [
            {
                name: 'index',
                type: 'INTEGER'
            },
            {
                name: 'Delivery Id',
                type: 'TEXT'
            },
            {
                name: 'Origin_Location',
                type: 'TEXT'
            },
            {
                name: 'Destination_Location',
                type: 'TEXT'
            },
            {
                name: 'region',
                type: 'TEXT'
            },
            {
                name: 'created_at',
                type: 'TIMESTAMP'
            },
            {
                name: 'actual_delivery_time',
                type: 'TIMESTAMP'
            },
            {
                name: 'On time Delivery',
                type: 'REAL'
            },
            {
                name: 'Customer_rating',
                type: 'REAL'
            },
            {
                name: 'condition_text',
                type: 'TEXT'
            },
            {
                name: 'Fixed Costs',
                type: 'REAL'
            },
            {
                name: 'Maintenance',
                type: 'REAL'
            },
            {
                name: 'Difference',
                type: 'REAL'
            },
            {
                name: 'Area',
                type: 'TEXT'
            },
            {
                name: 'Delivery_Time',
                type: 'REAL'
            }
        ]
    }
]
""".strip()


api_key="pass your gemini api key"


genai.configure(api_key=api_key)

sql_gemini = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=system_prompt,
    tools=[sql_query]
  )

chat = sql_gemini.start_chat(enable_automatic_function_calling=True)


response = chat.send_message(text)

def generate_invoice_pdf(response.text, filename="invoice.pdf"):
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    c.setFont("Helvetica", 16)
    c.drawString(100, height - 100, "Invoice")
    c.setFont("Helvetica", 12)
    y_position = height - 120  
    for line in invoice_text.split("\n"):
        c.drawString(100, y_position, line)
        y_position -= 14  
    c.save()


generate_invoice_pdf(invoice_text)




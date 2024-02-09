//import { GoogleGenerativeAI } from "@google/generative-ai"; 
// const API_KEY = "AIzaSyAh0hRIKFl75-pgz7WwJbkqYYc-nvagt1U"; // Paste your API key here 
// const genAI = new GoogleGenerativeAI(API_KEY); 
// const model = genAI.getGenerativeModel({ model: "gemini-pro" }); 

const { GoogleGenerativeAI } = require('@google-ai/generativelanguage');

const client = new GoogleGenerativeAI({
  apiKey: 'AIzaSyAh0hRIKFl75-pgz7WwJbkqYYc-nvagt1U',
});

module.exports.client=client


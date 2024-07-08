# E-commerce Chat-bot Documentation

## Setting Up the Environment and Dependencies

### Prerequisites
Before setting up the environment, ensure you have the following installed:
- Python 3.7 or higher
- pip (Python package installer)

### Step-by-Step Guide
1. **Clone the Repository**  
   Clone the repository to your local machine:  
   `git clone git@github.com:Frostylake/chatbot.git`

2. **Create a Virtual Environment**  
   It is recommended to create a virtual environment to manage your project dependencies:  
   `python -m venv venv`

3. **Activate the Virtual Environment**
   - On Windows:  
     `venv\Scripts\activate`
   - On macOS and Linux:  
     `source venv/bin/activate`

4. **Install Required Packages**  
   `pip install -r requirements.txt`

5. **Set Up Environment Variables**  
   Edit `.env` and add your OpenAI API key in terminal:  
   `echo "OPENAI_API_KEY=YOUR_OPENAI_API_KEY" >> .env`

6. **Run the Chatbot Script**  
   Execute script to start the chatbot:  
   `python chatbot.py`

## How to Run and Test the Agent

### Query List for the Chatbot
In order to test the chatbot, you can edit the list `query` in `chatbot.py`. There are pre-set questions for the chatbot you can use. When you run `chatbot.py`, a loop will send a query each time to the bot and print both the customer question and AI assistance response.

The agent uses `orders.csv` for getting the order IDs status and `customers.csv` to save the customer contact details. The chatbot is designed to remember the history of the conversation; therefore, it can be asked about previous queries. For example: "What is the first order ID human asked?"

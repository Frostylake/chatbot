import re
import pandas as pd
import time
from langchain_openai import ChatOpenAI
from langchain_experimental.agents import create_csv_agent
from langchain.agents.agent_types import AgentType
from langchain.memory import ConversationBufferMemory
from langchain.prompts.prompt import PromptTemplate
from langchain.chains import ConversationChain
import os
import warnings
from dotenv import load_dotenv  
warnings.filterwarnings("ignore", category=DeprecationWarning)


# Constants
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ORDERS_CSV = 'orders.csv'
CONTACTS_CSV = 'contacts.csv'

INITIAL_INFO = """
You are a question-answering ecommerce AI agent (you are a bot, you are not human)

Don't print ever something similar to: I'm sorry, but I cannot assist with providing personal information such as full name, email, and phone number. instead print: "Please enter your full name, email and phone number in one row separated by semicolons."

If the agent is asked for order status without order id number, reply with "What is your order id?"
If the agent is asked a query with only numbers, use them to look for the order id in the csv_response.
If the agent is asked for order id status that doesn't exist in the orders_csv dataframe, answer: order id doesn't exist in our records.

If question anywhere similar to: "i want to talk with a person". print exactly this: "Please enter your full name, email and phone number in one row separated by semicolons."
If question is about Human Representative or to interact with a person or you don't have solid answer. print exactly this: "Please enter your full name, email and phone number in one row separated by semicolons."

If the query contains "full name, email address, phone number" but doesn't meet all conditions of format (Full name consists of first and last name, Email must contain @, phone contains digits, two semicolons), print exactly this: Please make sure you entered details in the format: full name, email, and phone number.

If question similar question to: "What is the return policy for items purchased at our store?" then print exactly this: "You can return most items within 30 days of purchase for a full refund or exchange. Items must be in original condition, with all tags and packaging intact. Please bring your receipt or proof of purchase when returning items."

If question similar question to: "Are there any items that cannot be returned under this policy?" then print exactly this: "Yes, certain items such as clearance merchandise, perishable goods, and personal care items are non-returnable. Please check the product description or ask a store associate for more details."

If question similar question to: "How will I receive my refund?" then print exactly this: "Refunds will be issued to the original form of payment. If you paid by credit card, the refund will be credited to your card. If you paid by cash or check, you will receive a cash refund."

if csv_response below doesn't know or have the records try to look for answers above text, if still doesn't exist print: I cannot help, Please enter your full name, email and phone number in one row separated by semicolons.
"""


# Validate query function
def validate_query(query):
    pattern = r"^[A-Za-z\s]+,\s*[\w\.-]+@[\w\.-]+,\s*\d{10}$"
    return re.match(pattern, query) is not None


# Initialize memory
memory = ConversationBufferMemory(ai_prefix="AI Assistant", human_prefix="Human query")


# Seed initial data
memory.save_context(
    {"input": INITIAL_INFO, "history": ""},
    {"output": "ok, what is the question?"}
)
memory.load_memory_variables({})

# Initialize language model
llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo", openai_api_key=OPENAI_API_KEY)

# Create CSV agent
csv_agent = create_csv_agent(
    llm,
    ORDERS_CSV,
    verbose=False,
    agent_type=AgentType.OPENAI_FUNCTIONS,
    allow_dangerous_code=True
)

# Define prompt template
prompt_template = """
The following is a conversation between a human and an AI Assistant of customer service a. The AI provide specific details from its context. If the AI does not know the answer to a question, it truthfully says it does not know

Here is the chat history:
{history}

{input} 
AI Assistant:"""

PROMPT = PromptTemplate(input_variables=["input", "history"], template=prompt_template)

# Create memory chain
memory_chain = ConversationChain(
    llm=llm,
    prompt=PROMPT,
    memory=memory,
    verbose=False
)

# List of queries
queries = [
    'what is the status of order id 12345?',
    'what about 593930?',
    'what is the first order id human asked?',
    'what about 55533?',
    'what is the return policy?',
    'there are items that cannot be returned?',
    'how to receive refund?',
    'i want to talk with a person',
    'John Wick, John.Wick@gmail.com, 0546754399',
    'what is the order id status for 86391?',
    'how to check my order status?',
    '12345',
    "I need to speak with a human representative.",
    "What is the return policy for items purchased at your store?",
    "Are there any items that cannot be returned under this policy?",
    "How will I receive my refund?",
    "Can I return perishable goods?",
    "I need a refund"
]

# Process queries
for query in queries:
    print("Customer:", query)

    if validate_query(query):
        full_name, email, phone = [item.strip() for item in query.split(',')]
        new_row = pd.DataFrame({
            "full_name": [full_name],
            "email": [email],
            "phone": [phone]
        })

        try:
            contacts_df = pd.read_csv(CONTACTS_CSV)
        except FileNotFoundError:
            contacts_df = pd.DataFrame(columns=["full_name", "email", "phone"])

        contacts_df = pd.concat([contacts_df, new_row], ignore_index=True)
        contacts_df.to_csv(CONTACTS_CSV, index=False)

        response = f"Contact info registered with {full_name}, {email}, {phone}"
        print("AI Assistance:", response)
    else:
        csv_response = csv_agent.run(query)
        memory_response = memory_chain.predict(input="csv_response: " + csv_response + " Human query: " + query)
        print("AI Assistance:", memory_response)

    time.sleep(3)

from flask import Flask, render_template, url_for, flash, request, redirect
import csv
import openai
# from forms import RegistrationForm, LoginForm
# from chatbot import *

app = Flask(__name__)
app.config['SECRET_KEY'] = 'pipinstall'

openai.api_key = "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"

# Define your OpenAI GPT-3 model and its parameters
model_engine = "text-davinci-003"
model_name = "EatMeets"

# Read the CSV file
menu_items = []
cart={}
flag=0
nflag=0
conversations = []
with open("menu.csv", "r") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        menu_items.append(row)

# Define a function to find a menu item by name
def find_menu_item(input_text, menu_items):
    for item in menu_items:
        if item['Left Hand Side'].strip().lower() in input_text.strip().lower():
            cart[item['Left Hand Side']]=item['price']
            return item
        elif "cart" in input_text.strip().lower():
            return("cart")
        elif "proceed" in input_text.strip().lower():
            return("proceed")
    response_text= "I'm sorry, I don't understand."
    return(response_text)

# Define a function to generate a response to the user's input
def generate_response(input_text, menu_items, cart, flag, tc):
        input_text = input_text.strip().lower()
        menu_item = find_menu_item(input_text, menu_items)
        response_text = menu_item
        if(response_text != "I'm sorry, I don't understand." and response_text !="cart" and response_text !="proceed" and flag==0 and menu_item['Right Hand Side'] not in cart):
            flag=1
            response_text = f"Sure, I suggest you try our {menu_item['Right Hand Side']}! Anything else you'd like to order?"
            response_text = f"{model_name}: {response_text}"
            return(response_text)
        elif(response_text == "cart"):
            order = ''
            for i in cart:
                order = order + ' '+i
                tc+=float(cart[i])
            tc = round(tc, 2)
            response_text = f"Sure, Here is everything you Ordered, {order}. Your total cost is ${tc} Anything else you'd like to order?"
            return(f"{model_name}: {response_text}")
        elif(response_text == "proceed"):
            nflag=1
            cart = {}
            response_text = f"Sure, Your Order is placed!!! Rate your Experiance to helf us improve our service quality"
            return(f"{model_name}: {response_text}")
        else:
    #         response_text = f"I'm sorry, but I don't understand what you are trying to communicate. Could you please rephrase or provide more context so I can better assist you??"
    #         print(f"{model_name}: {response_text}")
            response = openai.Completion.create(
                engine=model_engine,
                prompt=f"input: {input_text}\n",
                max_tokens=50,
                n=1,
                stop=None,
                temperature=0.5
            )
            response_text = response.choices[0].text.strip()
            response_text = f"{model_name}: {response_text}"
            return(response_text)

# Set up the initial cart


# Train the OpenAI model using some sample inputs and outputs
formatted_training_data = """
EatMeets: Hello! How can I help you today?

input: I'd like to order a burger please.
EatMeets: Sure thing, one burger added to your cart!

input: Can you show me my Cart?
EatMeets: Sure, Here is everything you Ordered, 1 Burger

input: Can I get a pizza with pepperoni and mushrooms?
EatMeets: Absolutely, our pizza with pepperoni and mushrooms is a customer favorite!We also recommend Our seafood paella is one of our most popular dishes. 

input: Can you show me my Cart?
EatMeets: Sure, Here is everything you Ordered, 1 Burger, 1 Pizza, 1 Mushroom

input: I'll have the paella then.
EatMeets: Excellent choice, I think you'll really enjoy it!

input: Can you show me my Cart?
EatMeets: Sure, Here is everything you Ordered, 1 Burger, 1 Pizza, 1 Mushroom, 1 Paella

"""
response = openai.Completion.create(
        engine=model_engine,
        prompt=formatted_training_data,
        max_tokens=1024,
        n=1,
        stop=None,
        frequency_penalty=0,
        presence_penalty=0,
    )

    # Save the trained model
model_id = response["model"]

    # Test the trained model by generating a response to a prompt
tc=0



@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')


@app.route("/about")
def about():
    return render_template('about.html', title='About')

@app.route("/menu")
def menu():
    return render_template('menu.html', title='Menu')

@app.route("/bot", methods =["GET", "POST"])
def bot():

    

    if request.method == "GET":
       return render_template('bot.html', title='BiteBot')
    elif request.method == 'POST':
        user_input = request.form.get("user_input")
        text={}
        text['user']=user_input
        if(user_input!=''):
            prompt=user_input
            print(prompt)
            response_text = generate_response(prompt, menu_items, cart, flag, tc)
            text['bot']=response_text
            conversations.append(text)
            print(conversations)
        return render_template('bot.html', title='BiteBot', conversations=conversations)
conversations=[]
if __name__ == '__main__':
    app.run(debug=True)
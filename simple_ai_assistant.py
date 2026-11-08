from json import tool
import json
from openai import OpenAI
from dotenv import load_dotenv
from tools import TOOLS, FUNCTION_NAME_TO_FUNCTION_MAP
import os
from tools import get_stock_price


load_dotenv()  #by default looks for .env file


client = OpenAI(
    base_url=os.getenv("BASE_URL"),  #Send my API requests to the Ollama server running on my computer.
    api_key=os.getenv("API_KEY")  
)

messages = []
#Safety Limit: the max number of model rounds for ONE user question to prevent infinite loops in case of unexpected behavior.
MAX_STEPS = 5

# messages.append(
#     {
#         "role": "system",
#         "content": "Act Like a very humble agent and response always under 20 words."
#     }
# )


while True:
    user_input = input("\nGAURAV:")

    if(user_input.lower() in ["exit","quit","bye","goodbye"]):
        break

    messages.append(
        {
            "role": "user",
            "content": user_input
         }
     )    
    #Chained tool calling
    for step in range(MAX_STEPS):
        response = client.chat.completions.create(
        model=os.getenv("MODEL"),
        messages=messages,
        tools=TOOLS,
        )

        msg = response.choices[0].message
        if not msg.tool_calls:
            break  #if no tool calls are present in the response from LLM model then break the loop
        messages.append(msg)

        for tool_call in msg.tool_calls:
            func_name = tool_call.function.name
            func_args = {}
            try:

                func_args = json.loads(tool_call.function.arguments or "{}")  #original arguments in stringified json format we convert into dict using json.loads

                fn = FUNCTION_NAME_TO_FUNCTION_MAP[func_name]
                result = fn(**func_args)

            except Exception as e:
                result = f"Error while running function {func_name}: {str(e)}"

            messages.append(
                {
                    "role":"tool",
                    "tool_id":tool_call.id,
                    "content": str(result)
                }
            )
    else:
        #In python, 'else' after a for loop runs only if the loop finishes normally, meaning it wasn't ended early by a break. 
        #MAX STEPS exahusted: Ran out of steps : The model never gave the final answer.
        fallback = "Sorry, I could not finish this within the step limits."
        messages.append(
            {
                "role":"assistant",
                "content": fallback
            }
        )
        print("Assistant:" + fallback)  #response from LLM model :qwen:1.7b
                
        
    messages.append(
        {
            "role":"assistant",
            "content": msg.content  #we can access variable outside the loop as well.
        }
    )

    print("Assistant:" + msg.content)  #response from LLM model :qwen:1.7b

    
   
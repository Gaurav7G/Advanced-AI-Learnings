from json import tool
import json
from openai import OpenAI
from dotenv import load_dotenv
from tools import TOOLS, FUNCTION_NAME_TO_FUNCTION_MAP
import os


load_dotenv()  #by default looks for .env file


client = OpenAI(
    base_url=os.getenv("BASE_URL"),  #Send my API requests to the Ollama server running on my computer.
    api_key=os.getenv("API_KEY")  
)
messages = []
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
    response = client.chat.completions.create(
        model=os.getenv("MODEL"),
        messages=messages,
        tools=TOOLS,

    )
    msg = response.choices[0].message
    if msg.tool_calls:
        messages.append(msg)

        for tool_call in msg.tool_calls:
            func_name = tool_call.function.name
            func_args = json.loads(tool_call.function.arguments or "{}")  #original arguments in stringified json format we convert into dict using json.loads

            fn = FUNCTION_NAME_TO_FUNCTION_MAP[func_name]
            result = fn(**func_args)
            messages.append(
                {
                    "role":"tool",
                    "tool_id":tool_call.id,
                    "content": str(result)
                }
            )
        #2nd call to LLM Api
        response = client.chat.completions.create(
            model=os.getenv("MODEL"),
            messages=messages
        )

        msg = response.choices[0].message
    messages.append(
        {
            "role":"assistant",
            "content": msg.content
        }
    )

    print("Assistant:" + msg.content)  #response from LLM model :qwen:1.7b

    # messages.append(
    #     {
    #         "role": "assistant",
    #         "content": response.choices[0].message.content
    #     }
    # )
    

    # print("Assistant:" + response.choices[0].message.content)  #response from LLM model :qwen:1.7b
   
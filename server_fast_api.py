from fastapi import FastAPI, HTTPException, UploadFile, File
import base64
import os
import uvicorn
from drug_interactions import *

app = FastAPI()

@app.post("/drug-interactions")
async def drug_interactions(drugs: dict):

    try:
        drugs = drugs["drugs"]
        if not isinstance(drugs, list):
            raise HTTPException(status_code=400, detail="Invalid payload. 'drugs' should be a list.")

        interactions = describe_interactions(drugs)

        if not interactions["pairs"]:

            return {
                "drug_interactions": False,
                "explanation": "No interactions found"
            }

        explanation = explain_interactions(interactions)

        return {
            "drug_interactions": True,
            "explanation": explanation
        }
    except:
        raise HTTPException(status_code=400, detail="Invalid payload. 'drugs' should be a list.")

@app.post("/image-extract")
async def upload_and_process_image(image: UploadFile = File(...)):
    image_bytes = await image.read()

    # Convert binary image data to base64
    base64_rotated_image = base64.b64encode(image_bytes).decode('utf-8')

    # You can now use base64_rotated_image for further processing or sending to the OpenAI API
    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
            # {
            #     "role": "system",
            #     "content": [
            #         {
            #             "type": "text",
            #             "text": "You will take a medicine box image from the user, and you will extract the text and the colors from the image and you will describe the medicine and how to use it.\nYour response should be a json.\n RESPOND ONLY WITH JSON WITHOUT ANY OTHER TEXT."
            #         }
            #     ]
            # },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "the image I provided is a picture of a medicine box respond with json with key 'text' text is any text visible inside the image and key colors is any colors visible in the image, and a key description with any description of the medicine and how to use. like this {'text': 'text here', 'colors': ['red', 'white'], 'description': 'description here'}.\nONLY RESPOND WITH JSON WITHOUT ANY OTHER TEXT."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpg;base64,{base64_rotated_image}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 300
    }
    headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.environ.get('OPENAI_API_KEY')}"
        }

    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="error")

        response = response.json()

        if "choices" not in response:
            raise HTTPException(status_code=400, detail="error")

        response = response["choices"][0]["text"]

        return response
    except:
        raise HTTPException(status_code=400, detail="error")


uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "8080")))
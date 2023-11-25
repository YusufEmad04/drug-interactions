from fastapi import FastAPI, HTTPException
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

uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "8080")))
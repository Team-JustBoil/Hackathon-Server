from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from fastapi import FastAPI
import pytesseract
from PIL import Image
import uvicorn

app = FastAPI()

class UserInput(BaseModel):
    text: str

def process_word(user_input: str):
    word_list = [word.strip() for word in user_input.split()]
    return {"count": len(word_list), "list": word_list}

def process_sentence(user_input: str):
    sentence_list = [sentence.strip() for sentence in user_input.split('.') if sentence.strip()]
    return {"count": len(sentence_list), "list": sentence_list}

@app.post('/ocr')
async def ocr(file: UploadFile = File(...)):
    image = Image.open(file.file)
    text = pytesseract.image_to_string(image, lang='kor')
    text = text.replace('\n', '')  # This line replaces newline characters with spaces
    text = text.replace('\f', '')
    print(text)
    return {'text': text}

@app.post("/process/word")
def read_root(user_input_data: UserInput):
    user_input = user_input_data.text
    return process_word(user_input)

@app.post("/process/sentence")
def read_root(user_input_data: UserInput):
    user_input = user_input_data.text
    return process_sentence(user_input)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080)
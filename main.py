from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from fastapi import FastAPI
import pytesseract
from PIL import Image
import uvicorn
from typing import List
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware
import heapq
from collections import defaultdict

app = FastAPI()

origins = [
    "*"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserInput(BaseModel):
    text: str

class BookmarkInput(BaseModel):
    list: List[str]
    bookmarks: List[int]

def find_top_keywords(list: List[str], bookmarks: List[int], num_keywords=3):
    selected_text = [list[i] for i in bookmarks]
    
    # 모든 단어를 소문자로 변환하고, 공백으로 분리하여 하나의 리스트로 결합
    words = " ".join(selected_text).lower().split()

    # 단어의 빈도수를 계산
    word_freq = defaultdict(int)
    for word in words:
        word_freq[word] += 1
    
    # 최대 힙을 사용하여 상위 num_keywords 개의 키워드 추출
    max_heap = []
    for word, freq in word_freq.items():
        heapq.heappush(max_heap, (-freq, word))  # 빈도수에 음수를 적용하여 최대 힙 행동 모방

    # 키워드 문자열만 반환 (빈도수가 높은 순으로)
    top_keywords = []
    for _ in range(num_keywords):
        freq, word = heapq.heappop(max_heap)
        top_keywords.append(word)

    return top_keywords[::-1]  # 역순으로 반환하여 빈도수가 가장 높은 순서로 만듦

@app.post("/top")
def find_top_keywords_route(bookmark_input_data: BookmarkInput):
    top_keywords = find_top_keywords(bookmark_input_data.list, bookmark_input_data.bookmarks)
    return {"keywords": top_keywords}

def divide_and_conquer_split(input_str, delimiter):
    if not input_str:
        return []

    # Divide
    delimiter_index = input_str.find(delimiter)
    if delimiter_index == -1:
        return [input_str.strip()]

    # Conquer
    first_part = input_str[:delimiter_index].strip()
    remaining_part = input_str[delimiter_index + len(delimiter):]

    # Combine
    return [first_part] + divide_and_conquer_split(remaining_part, delimiter) if first_part else divide_and_conquer_split(remaining_part, delimiter)

def process_word(user_input: str):
    word_list = divide_and_conquer_split(user_input, " ")
    return {"count": len(word_list), "list": word_list}

def process_sentence(user_input: str):
    sentence_list = divide_and_conquer_split(user_input, ".")
    sentence_list = [sentence.strip() for sentence in sentence_list if sentence.strip()]
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
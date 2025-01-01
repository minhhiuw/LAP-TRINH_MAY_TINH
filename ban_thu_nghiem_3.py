# -*- coding: utf-8 -*-
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
import pandas as pd

# Tạo chatbot
food_chatbot = ChatBot(
    "FoodBot",
    storage_adapter="chatterbot.storage.SQLStorageAdapter",
    logic_adapters=[
        'chatterbot.logic.BestMatch'
    ],
    database_uri='sqlite:///database.sqlite3'
)

# Tải dữ liệu từ file Excel
def load_food_data(file_path):
    try:
        data = pd.read_excel(file_path, engine='openpyxl')
        data = data.dropna(how='all')  # Loại bỏ các hàng rỗng
        print("\nDữ liệu đã tải thành công!")
        return data
    except Exception as e:
        print(f"Lỗi khi đọc dữ liệu: {e}")
        return None

# Huấn luyện chatbot
def train_chatbot(chatbot, data):
    conversation = []

    # Huấn luyện chatbot dựa trên các câu hỏi gợi ý
    for _, row in data.iterrows():
        if pd.notna(row['Món ăn']):
            # Ghi chú món ăn vào danh sách
            ingredient = str(row['Nguyên liệu']) if pd.notna(row['Nguyên liệu']) else ''
            food_list = data[data['Nguyên liệu'] == ingredient]['Món ăn'].dropna().tolist()
            
            # Chuyển tất cả phần tử thành chuỗi nếu cần
            food_list = [str(food) for food in food_list]
            
            conversation.append((
                f"Tôi muốn ăn {row['Nhu cầu hiện tại']} có nguyên liệu {ingredient}",
                f"Một số món {row['Nhu cầu hiện tại']} với nguyên liệu {ingredient} bao gồm: {', '.join(food_list)}."
            ))
            if pd.notna(row['Đặc điểm']):
                characteristics = str(row['Đặc điểm']).split(', ')
                for characteristic in characteristics:
                    characteristic = characteristic.strip()
                    # Tìm tất cả các món có đặc điểm này
                    matching_foods = set()
                    for _, food_row in data.iterrows():
                        if pd.notna(food_row['Đặc điểm']):
                            if characteristic in str(food_row['Đặc điểm']):
                                matching_foods.add(str(food_row['Món ăn']))
                                if matching_foods:  # Only add if there are matching foods
                                    conversation.append((
                                    f"Tôi muốn ăn {row['Nhu cầu hiện tại']} có đặc điểm {characteristic}",
                                    f"Các món {row['Nhu cầu hiện tại']} có đặc điểm {characteristic} bao gồm: {', '.join(matching_foods)}."
            ))
            conversation.append((
                f"Tôi muốn biết món ăn chính từ {row['Nguồn gốc']}",
                f"Một số món ăn chính từ {row['Nguồn gốc']} bao gồm: {', '.join(data[(data['Nguồn gốc'] == row['Nguồn gốc']) & (data['Nhu cầu hiện tại'] == 'ăn chính')]['Món ăn'].dropna().tolist())}."
            ))
            conversation.append((
                f"Món {row['Món ăn']} có đặc điểm gì?",
                f"Món {row['Món ăn']} có các đặc điểm là: {row['Đặc điểm'] if pd.notna(row['Đặc điểm']) else 'Không có đặc điểm cụ thể.'}"
            ))

    trainer = ListTrainer(chatbot)
    for question, answer in conversation:
        trainer.train([question, answer])
    print("\nChatbot đã được huấn luyện xong!")

# Giao tiếp với người dùng
def chat_with_user(chatbot):
    print("Xin chào! Tôi là Chatbot gợi ý món ăn. Hãy hỏi tôi về món ăn bạn muốn!")
    print("\nBạn có thể hỏi tôi những câu như:")
    print("- 'Tôi muốn ăn [nhu cầu] có nguyên liệu [tên nguyên liệu]'")
    print("- 'Tôi muốn ăn [nhu cầu] có đặc điểm [tên đặc điểm]'")
    print("- 'Tôi muốn biết món ăn chính từ [nguồn gốc]'")
    print("- 'Món [tên món ăn] có đặc điểm gì?'")
    print("\nHãy bắt đầu nào! (Gõ 'Tôi đã chọn xong' để hoàn thành chat.)")

    while True:
        user_input = input("\nBạn: ").strip()
        if user_input.lower() == 'tôi đã chọn xong':
            print("Chatbot: Rất vui được giúp đỡ, chúc bạn ăn ngon miệng 😊")
            break

        response = chatbot.get_response(user_input)
        print(f"Chatbot: {response}")

# Main function
def main():
    file_path = "C:/Users/maymo/Downloads/New folder (2)/BẢN SỬa.xlsx"
    data = load_food_data(file_path)

    if data is not None:
        # Huấn luyện chatbot
        train_chatbot(food_chatbot, data)
        # Giao tiếp với người dùng
        chat_with_user(food_chatbot)

if __name__ == "__main__":
    main()

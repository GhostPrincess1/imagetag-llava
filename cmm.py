import tkinter as tk
from tkinter import filedialog, Label, Entry, Button
import os
# from openai import OpenAI
import base64
import requests
import json



# 打开文件
prompt = '''
As an AI image tagging expert, please provide precise tags for these images to enhance CLIP model's understanding of the content. Employ succinct keywords or phrases, steering clear of elaborate sentences and extraneous conjunctions. Prioritize the tags by relevance. Your tags should capture key elements such as the main subject, setting, artistic style, composition, image quality, color tone, filter, and camera specifications, and any other tags crucial for the image. When tagging photos of people, include specific details like gender, nationality, attire, actions, pose, expressions, accessories, makeup, composition type, age, etc. For other image categories, apply appropriate and common descriptive tags as well. Recognize and tag any celebrities, well-known landmark or IPs if clearly featured in the image. Your tags should be accurate, non-duplicative, and within a 20-75 word count range. These tags will use for image re-creation, so the closer the resemblance to the original image, the better the tag quality. Tags should be comma-separated. Exceptional tagging will be rewarded with $10 per image.
'''

def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')


class Tagger():
    def __init__(self) -> None:
        
        pass

    def tag_one_image(self,image_path):
        # Getting the base64 string

        base64_image = encode_image(image_path) #这里的image_path是图片的绝对路径或者相对路径
        # response = self.client.chat.completions.create(
        #     model="gpt-4o",
        #     messages=[
        #         {
        #         "role": "user",
        #         "content": [
        #             {"type": "text", "text": f"{prompt}"},
        #             {
        #             "type": "image_url",
        #             "image_url": {
        #                 "url": f"data:image/jpeg;base64,{base64_image}",
        #                 "detail": "low"
        #             },
        #             },
        #         ],
        #         }
        #     ],
        #     max_tokens=400,
        # )
        url = 'http://10.1.51.239:1314/api/generate'
        payload = {
            "model": "llava",
            "prompt": prompt,
            "stream": False,
            "images": [f"{base64_image}"]
        }

        
        response = requests.post(url, json=payload)

        # 检查请求是否成功
        if response.status_code == 200:
            # 解析响应体中的 JSON 数据
            data = response.json()

            # 从解析后的 JSON 数据中提取 'response' 字段
            response_content = data.get('response')

            # 打印 'response' 字段的内容
            #print(response_content)
        else:
            print(f"请求失败，状态码：{response.status_code}")
            return "error"
            
        
        #return response.choices[0].message.content

        return response_content


        pass
def tag_image(image_path):
    tagger = Tagger()
    result = tagger.tag_one_image(image_path)
    return result
    pass

# Create the main window
root = tk.Tk()
root.title("图片重命名和推图")

# Create input fields and labels
Label(root, text="图片文件夹路径:").grid(row=0, column=0, padx=10, pady=10)
folder_path_entry = Entry(root, width=50)
folder_path_entry.grid(row=0, column=1, padx=10, pady=10)

Label(root, text="图片前缀:").grid(row=1, column=0, padx=10, pady=10)
file_prefix_entry = Entry(root, width=50)
file_prefix_entry.grid(row=1, column=1, padx=10, pady=10)

Label(root, text="Starting Number:").grid(row=2, column=0, padx=10, pady=10)
start_number_entry = Entry(root, width=50)
start_number_entry.grid(row=2, column=1, padx=10, pady=10)

Label(root, text="标签内容前缀:").grid(row=3, column=0, padx=10, pady=10)
prefix_entry = Entry(root, width=50)
prefix_entry.grid(row=3, column=1, padx=10, pady=10)

def prepend_to_txt_files(folder_path, content_to_prepend):
    """
    遍历指定文件夹中的所有txt文件，并在每个文件的开头添加指定内容。
    
    :param folder_path: 要遍历的文件夹路径
    :param content_to_prepend: 要添加到每个txt文件开头的内容
    """
    # 确保提供的路径是一个目录
    if not os.path.isdir(folder_path):
        print("提供的路径不是一个有效的文件夹。")
        return

    # 遍历文件夹中的所有文件
    for filename in os.listdir(folder_path):
        # 检查文件扩展名是否为txt
        if filename.endswith('.txt'):
            file_path = os.path.join(folder_path, filename)
            # 读取文件内容
            with open(file_path, 'r+', encoding='utf-8') as file:
                content = file.read()
                # 将文件指针移动到文件开头
                file.seek(0, 0)
                # 写入新内容，紧接着写入原内容，不添加空行
                file.write(content_to_prepend + content)
                # 截断文件，删除原内容之后的部分
                file.truncate()

def tag_files():
    
    folder_path = folder_path_entry.get()
    file_prefix = file_prefix_entry.get()
    start_number = int(start_number_entry.get())
    text_prefix = prefix_entry.get()

    if not folder_path or not file_prefix or not start_number:
        return

    try:
        for filename in os.listdir(folder_path):
            if filename.endswith('.png') or filename.endswith('.jpg'):
                new_name = f"{file_prefix}_{start_number}{os.path.splitext(filename)[1]}"
                os.rename(os.path.join(folder_path, filename), os.path.join(folder_path, new_name))
                start_number += 1
        tk.messagebox.showinfo("Success", "图片重命名成功，等待推图......")
    except Exception as e:
        tk.messagebox.showerror("Error", f"An error occurred: {e}")

    
    tagger = Tagger()
    image_files = [f for f in os.listdir(folder_path) if os.path.splitext(f)[1] in ['.jpg', '.png', '.jpeg','JPEG']]
    for image_file in image_files:
            #判断是否有image_file同名的.txt文件
            if os.path.exists(os.path.join(folder_path, os.path.splitext(image_file)[0] + '.txt')):
                        

                txt_file_path = os.path.join(folder_path, os.path.splitext(image_file)[0] + '.txt')
                with open(txt_file_path, 'r',encoding='utf-8') as txt_file:
                    txt_content = txt_file.read().strip()  # 读取并去除两端空白字符
                    #去除两端空白字符是为了确保读取到的内容不包含任何额外的空格、换行符或制表符等空白字符，这样可以更加精确地判断内容是否为空。在实际情况中，有时候文件中可能会包含一些不可见的空白字符，这些字符可能会导致误判。因此，通过去除两端的空白字符，可以确保判断内容为空时不会受到这些额外的空白字符的干扰。
                if txt_content:
                    continue
            image_path = os.path.join(folder_path, image_file)
            print(image_path)
            
            try:
                tags = tagger.tag_one_image(image_path)
            except Exception as e:
                print("图片有问题，删除了",image_path)
                os.remove(image_path)

                continue
            #tags = wdpredict.wd_predict(image_path)
            #将tags写入txt文件中，和image_file同名但扩展名不同，放在images_folder中
            with open(os.path.join(folder_path, os.path.splitext(image_file)[0] + '.txt'), 'w',encoding='utf-8') as f:
                f.write(tags)
                f.close()
    

    prepend_to_txt_files(folder_path, text_prefix + ',')
    print("all done")

# Add a button to start the renaming process
rename_button = Button(root, text="开始", command=tag_files)
rename_button.grid(row=4, column=1, pady=20)

# Run the GUI event loop
root.mainloop()

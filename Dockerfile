# Python को बेस इमेज प्रयोग गर्दै
FROM python:3.9

# एप्लिकेशनको लागि कार्य डाइरेक्टरी सेट गर्नुहोस्
WORKDIR /app

# वर्तमान डाइरेक्टरीका सबै फाइलहरूलाई Docker इमेजमा कपी गर्नुहोस्
COPY . .

# आवश्यक प्याकेजहरू इन्स्टल गर्नुहोस्
RUN pip install --no-cache-dir -r requirements.txt

# Python को प्याकेजहरू इन्स्टल भएको सुनिश्चित गर्न
RUN python -m ensurepip --upgrade

# एप्लिकेशन चलाउनको लागि कमाण्ड सेट गर्नुहोस्
CMD ["python", "main.py"]

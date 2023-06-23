# from PIL import Image
# import requests
# from io import BytesIO
# try:
#   response = requests.get("https://www.google.com.pk/images/srpr/logo3w.png")
#   with Image.open(BytesIO(response.content)) as img:
#     pass
#   imageFound = True
# except:
#   imageFound = False

# print(imageFound)

from PIL import Image
import requests

url = "https://www.google.com.pk/images/srpr/logo3w.png"
try:
  with Image.open(requests.get(url, stream=True).raw) as img:
    pass
  imageFound = True
except:
  imageFound = False

print(imageFound)
  
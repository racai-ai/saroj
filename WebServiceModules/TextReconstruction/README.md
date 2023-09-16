
# TextExtractor  
This module extracts tokens from a .docx file.  
  
## Prerequisites  
  
Before running the script, make sure you have the following installed:  
  
- Python 3.x  
- Flask library (install using `pip install Flask`)  

   
To quickly install the required Python libraries, you can use the provided `requirements.txt` file. Run the following command to install the dependencies:  
  
```bash  
pip install -r requirements.txt
```  
## How to Run  
Run the script:  
```  
python textReconstruction_api.py PORT [--SAVE_INTERNAL_FILES]  
```  
* _PORT_ (required): The port number to listen for incoming API requests.  
* _--SAVE_INTERNAL_FILES_ or -s (optional): Include this flag to save internal files, which can be useful for debugging. By default, this option is disabled.  
  
## Usage  
Once the API is running, you can interact with the following endpoints:  
  
### Process Text Endpoint:  
  
```bash  
POST http://localhost:PORT/process
```
  
This endpoint allows you to submit a POST request with a JSON payload containing the .docx file, coNLLU-P file and output path
text you want to anonymize. The API will return OK message or errors if exceptions are encountered.  
  
### Check Health Endpoint:  
  
```bash  
GET http://localhost:PORT/checkHealth
```  
This endpoint is used to check the health status of the API. It will return a response indicating that the API is up and running.  
  
## Example  
Run the following command to start the API on port 5000:  
```  
python textReconstruction_api.py 5000  
```  
Send a POST using CURL:  
```  
curl  POST -F "input={\"input\":\"../../input.conllup\",\"original\":\"../../text.docx\" \"output\":\"text_anon.docx\"}" http://localhost:5000/process  
```
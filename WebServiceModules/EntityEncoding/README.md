
# Entity Encoder  
This module encodes entities from a .conllup file.  
  
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
python entityEncoding_api.py PORT 
```  
* _PORT_ (required): The port number to listen for incoming API requests.  
  
## Usage  
Once the API is running, you can interact with the following endpoints:  
  
### Process Text Endpoint:  
  
```bash  
POST http://localhost:PORT/process
```
  
This endpoint allows you to submit a POST request with a JSON payload containing the coNLLU-P file, the mapping file (.map) and output path (.conllup)
 you want to encode. The API will return OK message or errors if exceptions are encountered.  
  
### Check Health Endpoint:  
  
```bash  
GET http://localhost:PORT/checkHealth
```  
This endpoint is used to check the health status of the API. It will return a response indicating that the API is up and running.  
  
## Example  
Run the following command to start the API on port 5000:  
```  
python entityEncoding_api.py 5000  
```  
Send a POST using CURL:  
```  
curl  POST -F "input={\"input\":\"../../input.conllup\",\"mapping\":\"../../ent.map\" \"output\":\"output.conllup\"}" http://localhost:5000/process  
```
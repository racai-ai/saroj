
# TextExtractor  
This module extracts tokens from a .docx file.  
  
## Prerequisites  
  
Before running the script, make sure you have the following installed:  
  
- Python 3.x  
- UDPipe library (install using `pip install ufal.udpipe`)  
- Flask library (install using `pip install Flask`)  
- spaCy library (install using `pip install spacy`)  
- CoNLL-U library (install using `pip install conllu`)  
  
  
To quickly install the required Python libraries, you can use the provided `requirements.txt` file. Run the following command to install the dependencies:  
  
```bash  
pip install -r requirements.txt
```  
## How to Run  
Run the script:  
```  
python textExtractor_api.py PORT [--RUN_ANALYSIS] [--SAVE_INTERNAL_FILES] [--udpipe_model UDPipeModelPath]  
```  
* _PORT_ (required): The port number to listen for incoming API requests.  
* _--RUN_ANALYSIS_ or -r (optional): Include this flag to enable text analysis using UDPipe. By default, text analysis is disabled.  
* _--SAVE_INTERNAL_FILES_ or -s (optional): Include this flag to save internal files, which can be useful for debugging. By default, this option is disabled.  
* _--udpipe_model_ (optional): Path to the UDPipe model file. If not _--RUN_ANALYSIS_ flag enable, UDPipe tokenization will be skipped.  
  
## Usage  
Once the API is running, you can interact with the following endpoints:  
  
### Process Text Endpoint:  
  
```bash  
POST http://localhost:PORT/process
```
  
This endpoint allows you to submit a POST request with a JSON payload containing the input text you want to analyze. The API will return the path to output file in JSON format, which includes tokenization and parts-of-speech tagging information.  
  
### Check Health Endpoint:  
  
```bash  
GET http://localhost:PORT/checkHealth
```  
This endpoint is used to check the health status of the API. It will return a response indicating that the API is up and running.  
  
## Example  
Run the following command to start the API on port 5000 and enable text analysis using UDPipe:  
```  
python textExtractor_api.py 5000 --RUN_ANALYSIS --udpipe_model udpipe_model_file.udpipe  
```  
Send a POST using CURL:  
```  
curl -X POST -H "Content-Type: application/json" -d "{\"input\":\"../../input.docx\", \"output\":\"output.conllup\"}" http://localhost:5000/process  
```
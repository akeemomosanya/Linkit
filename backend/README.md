# BACKEND

Backend for the linkit app built with fastapi

## Steps on how another developer can set it up on their local machine
1. Clone the repository using "git clone <repository-url>" then navigate to the project directory "cd <LINKIT>/backend"
2. Create and Activate a Virtual Environment. You can create a virtual environment using python3 -m venv linkitenv for Linux/Mac or Windows Operating system on your terminal.
Activate the environment using "source linkitenv/bin/activate" for Linux/Mac and "env\Scripts\activate for windows operating system"
3. Install Fastapi and uvicorn.
- To install fastapi in your environment , make sure that your environment is activated , run "pip install fastapi"
- To install uvicorn in your environment make sure that your environment is still activated then run "pip install uvicorn"
4. Run the Development Server using "uvicorn main:app --reload" on ur terminal with your environment still activated.The server will start at http://127.0.0.1:8000.
5. Access the API Documentation
FastAPI provides interactive API documentation:
Swagger UI: http://127.0.0.1:8000/docs 
You can just add /docs to the http://127.0.0.1:8000 on your web browser

### Setting up to check the account endpoint
If you want to set it up:
1. Clone the repository from GitHub
2. Activate your environment
3. Run `uvicorn main:app --reload`
4. Visit http://127.0.0.1:8000/docs to access the Swagger UI


#### Install Dependencies
Use the command below to install the necessary requirements 
```bash
pip install -r requirements.txt
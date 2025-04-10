![Lint-free](https://github.com/software-students-spring2025/4-containers-dataleak/actions/workflows/lint.yml/badge.svg)
![Machine Learning Client](https://github.com/software-students-spring2025/4-containers-dataleak/actions/workflows/ml.yml/badge.svg)
![Web App](https://github.com/software-students-spring2025/4-containers-dataleak/actions/workflows/web-app.yml/badge.svg)

# Virtual Fridge

## Project Description

Virtual Fridge is a food tracking application that helps users keep track of food they have at home. With a photo, this app can automatically categorize foods and store foods in a user's virtual fridge. User's will be able to create an account and login to view their virtual fridge wherever they go.

1. **Machine Learning Client**
   - Uses a pre-trained machine learning model to recognize different foods via the user's webcam.
2. **Web App**
   - Built with flask, it allows users to set up an account, add different foods, and view those foods.
3. **MongoDB**
   - Database for storing user information and food items.

## Team Members
- [Angel Serrano](https://github.com/a-ngels)
- [Melissa Kelly](https://github.com/melissalkelly)
- [Ava August](https://github.com/aaugust22)
- [Arkadiuz Mercado](https://github.com/ArionM27)

## Prerequisites

Before starting, ensure you have the following installed:

- [Docker](https://www.docker.com/products/docker-desktop/)
- [Docker Compose](https://docs.docker.com/compose/install/)
- Web browser with access to a camera

## Environment Variables

The following environment variables are required in the `.env` file:

```env
MONGO_URI='mongodb+srv://<username>:<password>@<connectionstring>/<databasename>?ssl=true&ssl_cert_reqs=CERT_NONE'
MONGO_DBNAME=<databasename>
CLARIFAI_API_KEY=<key>
```

## App Setup with Docker

1. Clone the repository:
```python
git clone [repository-url]
cd [repository name]
```

2. Start Docker Compose:
```python
docker-compose down --volumes --remove-orphans
docker-compose up --build
```

3. Access:
- **Web App:** [http://localhost:5000](http://localhost:5000)  
- **MongoDB Express:** [http://localhost:27017](http://localhost:27017)  
  _Login: `admin` / `pass`_

## Local App Setup

1. MongoDB:
```python
docker-compose up mongodb -d
```
2. Set up ML Client
```python
cd machine-learning-client
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python api.py
```
3. Set up Web App
```python
cd web-app
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
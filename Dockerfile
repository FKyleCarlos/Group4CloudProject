FROM python:3.11-slim
WORKDIR C:\Users\franc\OneDrive\Desktop\SAIT\Year2\Sem2\Cloud\Projects\Project1\Group4CloudProject
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "data_analysis_azure.py"]

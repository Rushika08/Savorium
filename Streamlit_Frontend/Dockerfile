FROM tensorflow/tensorflow:2.10.0

RUN mkdir -p app/frontend

COPY Streamlit_Frontend/requirements.txt /app/frontend/requirements.txt

WORKDIR /app/frontend

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "--server.fileWatcherType=auto"]

CMD ["HOME.py"]

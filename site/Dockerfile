FROM python:3.10.6
ENV APP_HOME /app
ENV GOOGLE_APPLICATION_CREDENTIALS=./sage-digisafe-svc-acct.json
WORKDIR $APP_HOME
COPY site/* sage-digisafe-svc-acct.json ./
EXPOSE 8501
RUN ls -l
RUN pip install -r requirements.txt
ENTRYPOINT ["streamlit", "run"]
CMD ["streamlit-app.py"]

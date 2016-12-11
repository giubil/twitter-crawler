FROM gcr.io/google_appengine/python

RUN virtualenv /env
ENV VIRTUAL_ENV /env
ENV PATH /env/bin:$PATH
ADD requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

ADD . /app

CMD python /app/main.py

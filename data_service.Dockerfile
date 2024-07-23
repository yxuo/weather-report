FROM python:3.12-slim

WORKDIR /app

COPY src /app


# Install virtualenv and create a virtual environment
RUN pip install --no-cache-dir virtualenv && virtualenv /env --python=python3.12
ENV PATH /env/bin:$PATH

# Install pip requirements
RUN /env/bin/pip install --no-cache-dir -r requirements.txt


# Expose
EXPOSE 5784
STOPSIGNAL SIGTERM

# run commands
CMD ["/bin/bash", "-c", "python -u -m data_service"]

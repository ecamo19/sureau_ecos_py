FROM python:3.12

WORKDIR /workspaces/sureau_ecos_py

COPY ./requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --upgrade pip


FROM python:3.9.18

WORKDIR /workspaces/sureau_ecos_py

COPY ./requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --upgrade pip


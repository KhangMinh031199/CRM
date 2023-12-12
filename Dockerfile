FROM centos:7
MAINTAINER TungHa "thomas@nextify.co"
RUN yum -y install epel-release && \
    yum -y install gcc gcc-c++ kernel-devel unixODBC-devel && \
    yum -y install python-devel libxslt-devel libffi-devel openssl-devel bzip2-devel && \
    yum -y install libcurl

COPY ./requirements.txt /app/requirements.txt
WORKDIR /app
RUN curl "https://bootstrap.pypa.io/get-pip.py" -o "get-pip.py"
RUN python2.7 get-pip.py
RUN pip install -U pip
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app
CMD [ "python", "new_cms.py" ]
FROM python:3.8

WORKDIR /opt/tmp
COPY . /opt/tmp
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

EXPOSE 80

CMD ["/bin/sh", "/opt/tmp/start.sh"]
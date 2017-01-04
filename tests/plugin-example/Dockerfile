FROM daocloud.io/python:2.7

RUN pip install tornado && \
    pip install https://github.com/DaoCloud/dce-plugin-sdk-py/archive/master.zip

LABEL io.daocloud.dce.plugin.name="SDK-Test"

ADD plugin.py /plugin.py

CMD ["python", "plugin.py"]
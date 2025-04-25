FROM hub-mirror.wps.cn/kas-open/base/nvidia/tritonserver:25.02-vllm-python-py3
ENV LANG=zh_CN.UTF-8
ENV LC_ALL=zh_CN.UTF-8
#RUN python -m pip install --upgrade pip
#RUN pip install git+https://github.com/huggingface/transformers.git -i https://pypi.mirrors.ustc.edu.cn/simple
#RUN pip install accelerate==0.24.0 -i https://mirrors.aliyun.com/pypi/simple
# RUN pip install filechunkio -i https://mirrors.aliyun.com/pypi/simple
COPY mcp-demo /work_dir/mcp-demo
COPY mcp-demo/bin/requirements.txt /work_dir/mcp-demo/bin/requirements.txt
RUN pip3 install --upgrade --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple \
        -r /work_dir/mcp-demo/bin/requirements.txt
# RUN pip install ks3sdk==1.5.11 -i https://mirrors.wps.cn/pypi/simple/
#RUN pip install pycryptodome -i https://mirrors.wps.cn/pypi/simple/
# RUN pip install prometheus-client==0.14.1 -i https://mirrors.wps.cn/pypi/simple/
WORKDIR /work_dir/mcp-demo
# COPY src /work_dir/src

RUN chmod u+x ./src/script/start.sh
CMD ./src/script/start.sh

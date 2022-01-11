FROM quay.io/cdis/anaconda3:2020.11

RUN useradd -m -s /bin/bash gen3
RUN chown -R gen3: /opt/conda

COPY --chown=gen3:gen3 . /home/gen3

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install -y \
        apt-utils \
        apt-transport-https \
        jq \
        procps \
        unzip \
        vim \
        zip \
    && apt-get clean

USER gen3
WORKDIR /home/gen3

ADD --chown=gen3:gen3 https://github.com/uc-cdis/cdis-data-client/releases/download/2021.01/dataclient_linux.zip /home/gen3/gen3/dataclient_linux.zip
RUN cd gen3 && unzip dataclient_linux.zip && rm dataclient_linux.zip
RUN conda init bash
RUN conda env create -f environment.yml 
RUN bash -i -c 'conda activate gen3-augur && python setup.py develop'

#
# Mount /gen3/credentials.json, 
#    /home/gen3/logs,
#    /home/gen3/data,
#    /home/gen3/results,
#    /home/gen3/auspice,
#
CMD [ "bash", "-i", "-c", "bash -i dockerrun.sh | tee logs/run_pipeline_$(date +%Y%m%d%H%M%S).log" ]

# python3.8-dev package is hosted only bionic apt repository.
FROM ubuntu:bionic

ENV LANG=C.UTF-8 LC_ALL=C.UTF-8
ENV PATH /opt/conda/bin:$PATH

RUN apt-get update --fix-missing && apt-get install -y wget bzip2 ca-certificates \
    libglib2.0-0 libxext6 libsm6 libxrender1 \
    git mercurial subversion

RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda2-4.5.11-Linux-x86_64.sh -O ~/miniconda.sh && \
    /bin/bash ~/miniconda.sh -b -p /opt/conda && \
    rm ~/miniconda.sh && \
    ln -s /opt/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh && \
    echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc && \
    echo "conda activate base" >> ~/.bashrc

RUN apt-get install -y curl grep sed dpkg && \
    TINI_VERSION=`curl https://github.com/krallin/tini/releases/latest | grep -o "/v.*\"" | sed 's:^..\(.*\).$:\1:'` && \
    curl -L "https://github.com/krallin/tini/releases/download/v${TINI_VERSION}/tini_${TINI_VERSION}.deb" > tini.deb && \
    dpkg -i tini.deb && \
    rm tini.deb && \
    apt-get clean


# Install other tools
RUN apt-get update --fix-missing && apt-get install -y git openssh-server nkf vim less wget curl zip unzip

# create a new conda environment named kaggle
RUN conda create -n kaggle -y -q Python=3.8
RUN sed -i -e 's/base/kaggle/g' /root/.bashrc

# install additional packages used by sample notebooks. this is optional
RUN ["/bin/bash", "-c", "source activate kaggle && conda install -y matplotlib"]

# install other library
RUN ["/bin/bash", "-c", "source activate kaggle && pip install pandas==1.1.2 numpy==1.18.5 scikit-learn joblib seaborn lightgbm xgboost catboost"]

# install prophet
RUN ["/bin/bash", "-c", "source activate kaggle && conda install -c conda-forge fbprophet"]

# install with conda from conda-forge
RUN ["/bin/bash", "-c", "source activate kaggle && conda install -c conda-forge jupyter jupyterlab"]

# generate jupyter configuration file
RUN ["/bin/bash", "-c", "source activate kaggle && mkdir ~/.jupyter && cd ~/.jupyter && jupyter notebook --generate-config"]

# set an emtpy token for Jupyter to remove authentication.
# this is NOT recommended for production environment
RUN echo "c.NotebookApp.password = u'sha1:7cf465f0ed5c:26aa862a0ba75cb7eee8ae3e958bbfa654565a3d'" >> ~/.jupyter/jupyter_notebook_config.py
RUN echo "c.Spawner.default_url = '/lab'" >> ~/.jupyter/jupyter_notebook_config.py

# open up port 8888 on the container
EXPOSE 8888

### Setup ssh
RUN mkdir /var/run/sshd
RUN echo "root:root" | chpasswd
RUN sed -i -e 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/g' /etc/ssh/sshd_config
ENV NOTVISIBLE "in users profile"
RUN echo "export VISIBLE=now" >> /etc/profile
EXPOSE 22

# start Jupyter notebook server on port 8888 when the container starts
ADD ./start.sh /
ADD ./packages.pth /opt/conda/envs/kaggle/lib/python3.8/site-packages
RUN chmod +x /start.sh
CMD ["/start.sh"]

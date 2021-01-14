# Docker環境の作り方


## 1. clone
```
mkdir -p ~/dev/projects
cd ~/dev/projects
git clone git@gitlab.datumstudio.jp:k.masuda/kaggle_titanic.git
```

## 2. docker-compose.ymlを編集

```
version: "2"
services:
  kaggle_titanic: #1
    container_name: kaggle_titanic  #2
    image: keitadev/kaggle_titanic:latest #3
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8003:8888"  #4
      - "10003:22"   #5
    volumes:         #6 
      - "~/dev/projects/vinx:/home/jovyan/dev/projects/vinx"
```

好きなように変更してほしいところ
* \#1 `サービス名`
* \#2 `container_name`
* \#3 `image`
* \#4&\#5 `ports`
  * ここはコロンの左側の数字のみ、コロンの右側の数字は変更しないこと
* \#6 `volumes` ローカルマシンとVMの共有ディレクトリ(:の左がローカル)

## 3. コンテナ起動

`docker-compose up -d`

## 4. 念のため確認
```
docker ps

[keita.masuda@RM0214 ~/test/kaggle_titanic]$ docker ps
CONTAINER ID        IMAGE                            COMMAND                  CREATED             STATUS              PORTS                                           NAMES
bc77fafbd64d        keitadev/kaggle_titanic:latest   "tini -g -- /start.sh"   2 minutes ago       Up 2 minutes        0.0.0.0:10009->22/tcp, 0.0.0.0:8009->8888/tcp   kaggle_titanic
```

## 4. Jupiterを確認

http://localhost:10003

10003は↑で設定したポート番号

パスワードはroot

## 5. コンテナにログインできるか確認
`docker exec -it [Container ID] /bin/bash`  

Or
  
```
$ ssh -p 10009 jovyan@localhost 

The authenticity of host '[localhost]:10009 ([::1]:10009)' can't be established.
ECDSA key fingerprint is SHA256:XxaXvQp50rAhXnRxPnPEtUT4cch1SX9ivhskZga2n5E.

Are you sure you want to continue connecting (yes/no)? yes
Warning: Permanently added '[localhost]:10009' (ECDSA) to the list of known hosts.

jovyan@localhost's password: jovyan

jovyan@bc77fafbd64d:~$ ログイン成功
```
10009は↑で設定したポート番号

# カスタムライブラリをAzure環境でimportし、実行する方法

ここではAzure環境に自作ライブラリを転送し、AzureMLが作るDocker環境にインストールし、Pipeline Script内でimportおよび実行する方法をまとめる。

## 1. スクリプトの追加/変更

以下にスクリプトファイルを作る、もしくは以下にある既存スクリプトを変更する。  
`/home/jovyan/dev/projects/vinx/work/lib/vinx_azure/vinx_azure_ml`

## 2. バージョンの変更

`/home/jovyan/dev/projects/vinx/work/lib/vinx_azure/setup.py`のバージョンを変更する。

```
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="vinx_azure_ml",
    version="0.0.4",  <------------------------------HERE!
    author="Keita Masuda",
    author_email="k.masuda@datumstudio.jp",
    description="A custom package used in model development in Azure ML",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
```

## 3. `azureml` Conda環境のアクティベーション

ローカルのvinx Docker環境内に入り、`azureml` conda環境をアクティベートする。  

`source activate azureml`

念の為pythonのバージョンを確認  

```
$python --version
Python 3.6.10 :: Anaconda, Inc.
```
3.6以上なはず

## 4. wheelファイルの作成

wheelファイルを作成

`cd /home/jovyan/dev/projects/vinx/work/lib/vinx_azure`  
`python setup.py sdist bdist_wheel`

以下のディレクトリに`.whl`ファイルが↑で書き換えたバージョン番号で存在するか確認  
`/home/jovyan/dev/projects/vinx/work/lib/vinx_azure/dist`

* `work/lib/vinx_azure/dist/vinx_azure_ml-0.0.1-py3-none-any.whl`

`0.0.1` -> バージョン  
`py3` -> python3

合ってるか確認。  

## 5. 最後に`defs.py`のwheelファイルのパスを書き換えて実行

以下の定数を↑で作成したファイルパスにすればOK
`WHL_VINX_AZURE_ML= LIB+'/vinx_azure/dist/vinx_azure_ml-0.0.4-py3-none-any.whl'`

これでPipelineのPythonScript内でカスタムモジュールが使えます。
※ Docker Imageが再生成されます。  
  
# sequential_run.pyの実行方法
sshでdockerコンテナにrootでログイン

`source activate azureml`を実行してazuremlの環境に入る

念のためにpythonのバージョンを確認
```
$python --version
Python 3.6.10 :: Anaconda, Inc.
```
と表示されていればok

`cd /home/jovyan/dev/projects/vinx/work/lib`
したのち
`python sequential_run.py`を実行すればconfig内にあるsequential_run_config.jsonを読み込み実行可能
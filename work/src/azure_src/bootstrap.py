import defs as d
import joblib
import azureml.core
from azureml.core import Workspace, Datastore, Environment
from azureml.core.compute import ComputeTarget, AmlCompute
from azureml.core.runconfig import RunConfiguration
from azureml.core.conda_dependencies import CondaDependencies
from azureml.core.authentication import InteractiveLoginAuthentication


def bootstrap(tenant='vx', compute_target=''):
  ws, compute = login(tenant, compute_target)
  run_config = base_run_config(ws, compute)

  return ws, compute, run_config


def login(tenant, compute_target):

  if tenant == 'vx':
    tenant_id = d.VINX_TENANT_ID
    target_name = d.VINX_COMPUTING
    config = d.VINX_CONFIG_PATH
  elif tenant == 'ds':
    if compute_target:
      target_name = compute_target
    else:
      target_name = d.DS_COMPUTING
    tenant_id = d.DS_TENANT_ID

    config = d.DS_CONFIG_PATH
  else:
    raise ValueError('tenant must be either on of vx or ds')

  interactive_auth = InteractiveLoginAuthentication(tenant_id=tenant_id)
  ws = Workspace.from_config(config)
  compute = AmlCompute(ws, target_name)

  return ws, compute


# Default run config
def base_run_config(ws, compute):

  whl_url = Environment.add_private_pip_wheel(workspace=ws, file_path=d.WHL_VINX_AZURE_ML, exist_ok=True)
  run_config = RunConfiguration()
  run_config.target = compute
  run_config.environment.docker.enabled = True
  run_config.environment.docker.base_image = 'mcr.microsoft.com/azureml/base:latest'
  run_config.environment.python.user_managed_dependencies = False
  run_config.environment.python.conda_dependencies = CondaDependencies.create(
    conda_packages=['tqdm', 'cython', 'matplotlib', 'scikit-learn', 'fbprophet'],
    pip_packages=['azureml-sdk', 'pandas', 'lightgbm', 'scipy==1.4.1', 'statsmodels', 'mlxtend', 'optuna', 'xgboost',
                  'CatBoost', 'tensorflow', 'keras', 'jpholiday', 'joblib'],
    pin_sdk_version=False
  )
  run_config.environment.python.conda_dependencies.add_pip_package(whl_url)

  return run_config


# Run config for SQL Managed Instance
def mi_run_config(ws, compute):
  whl_url = Environment.add_private_pip_wheel(workspace=ws, file_path=d.WHL_VINX_AZURE_ML, exist_ok=True)
  run_config = RunConfiguration()
  run_config.target = compute
  run_config.environment.docker.enabled = True
  run_config.environment.docker.base_image = None
  run_config.environment.docker.base_dockerfile = 'FROM mcr.microsoft.com/azureml/base:latest\nRUN apt-get update && apt-get -y install freetds-dev freetds-bin vim gcc'
  run_config.environment.python.user_managed_dependencies = False
  run_config.environment.python.conda_dependencies = CondaDependencies.create(
    conda_packages=['tqdm', 'cython', 'matplotlib', 'scikit-learn', 'fbprophet'],
    pip_packages=['azureml-sdk', 'pandas', 'lightgbm', 'scipy==1.4.1', 'statsmodels', 'mlxtend', 'optuna', 'xgboost',
                  'CatBoost', 'tensorflow', 'keras', 'jpholiday', 'joblib', 'pymssql==2.1.1'],
    pin_sdk_version=False
  )
  run_config.environment.python.conda_dependencies.add_pip_package(whl_url)

  return run_config
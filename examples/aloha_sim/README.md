# Run Aloha Sim

## With Docker

```bash
export SERVER_ARGS="--env ALOHA_SIM"
docker compose -f examples/aloha_sim/compose.yml up --build
```

## Without Docker

预配置

```bash
# Create virtual environment
uv venv --python 3.10 examples/aloha_sim/.venv
source examples/aloha_sim/.venv/bin/activate
uv pip sync examples/aloha_sim/requirements.txt
uv pip install -e packages/openpi-client

# Run the simulation
# MUJOCO_GL=egl python examples/aloha_sim/main.py 
```

Note: If you are seeing EGL errors, you may need to install the following dependencies:

```bash
sudo apt-get install -y libegl1-mesa-dev libgles2-mesa-dev
```

Terminal window 1:

```bash 
source examples/aloha_sim/.venv/bin/activate
# 通过绘图显示实时过程
python examples/aloha_sim/main.py --args.display True
```

Terminal window 2:

```bash
source examples/aloha_sim/.venv/bin/activate
# Run the server
XLA_PYTHON_CLIENT_MEM_FRACTION=0.85 uv run scripts/serve_policy.py --env ALOHA_SIM
```

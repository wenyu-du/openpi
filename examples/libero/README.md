# LIBERO Benchmark

This example runs the LIBERO benchmark: https://github.com/Lifelong-Robot-Learning/LIBERO

Note: When updating requirements.txt in this directory, there is an additional flag `--extra-index-url https://download.pytorch.org/whl/cu113` that must be added to the `uv pip compile` command.

具体实现方式：

```bash
uv pip compile requirements.in --extra-index-url https://download.pytorch.org/whl/cu113 > requirements.txt
```

| **文件**             | **功能**                                                                 | **用户操作**                              | **示例内容**                          |
|----------------------|-------------------------------------------------------------------------|------------------------------------------|--------------------------------------|
| **`requirements.in`** | **原始依赖声明文件**：手动编写，仅包含直接依赖项（顶层包），不需精确版本。          | 开发者直接编辑，添加/删除依赖。              | ```<br>numpy<br>torch>=2.0<br>```    |
| **`requirements.txt`** | **锁定依赖文件**：自动生成，包含所有直接和间接依赖项（子依赖）及**精确版本号**。      | 通过工具（如`pip-compile`）生成，禁止手动修改。 | ```<br>numpy==1.26.0<br>torch==2.0.1<br>``` |

💡 为什么推荐这种模式？\
安全性：避免依赖冲突（如A包需要numpy<2.0，B包需要numpy>=2.0）。\
可复现性：所有机器（开发/生产）安装相同版本的包。\
透明性：通过 .in 文件明确表达意图，通过 .txt 自动处理复杂性。

This example requires git submodules to be initialized. Don't forget to run:

```bash
git submodule update --init --recursive
```

## With Docker (recommended)

```bash
# Grant access to the X11 server:
sudo xhost +local:docker

# To run with the default checkpoint and task suite:
SERVER_ARGS="--env LIBERO" docker compose -f examples/libero/compose.yml up --build

# To run with glx for Mujoco instead (use this if you have egl errors):
MUJOCO_GL=glx SERVER_ARGS="--env LIBERO" docker compose -f examples/libero/compose.yml up --build
```

You can customize the loaded checkpoint by providing additional `SERVER_ARGS` (see `scripts/serve_policy.py`), and the LIBERO task suite by providing additional `CLIENT_ARGS` (see `examples/libero/main.py`).
For example:

```bash
# To load a custom checkpoint (located in the top-level openpi/ directory):
export SERVER_ARGS="--env LIBERO policy:checkpoint --policy.config pi05_libero --policy.dir ./my_custom_checkpoint"

# To run the libero_10 task suite:
export CLIENT_ARGS="--args.task-suite-name libero_10"
```

## Without Docker (not recommended)

Terminal window 1:

```bash
# Create virtual environment
uv venv --python 3.8 examples/libero/.venv
source examples/libero/.venv/bin/activate
uv pip sync examples/libero/requirements.txt third_party/libero/requirements.txt --extra-index-url https://download.pytorch.org/whl/cu113 --index-strategy=unsafe-best-match
uv pip install -e packages/openpi-client
uv pip install -e third_party/libero
export PYTHONPATH=$PYTHONPATH:$PWD/third_party/libero

# Run the simulation
python examples/libero/main.py

# To run with glx for Mujoco instead (use this if you have egl errors):
MUJOCO_GL=glx python examples/libero/main.py
```

Terminal window 2:

```bash
# Run the server
uv run scripts/serve_policy.py --env LIBERO
```

## Results

If you want to reproduce the following numbers, you can evaluate the checkpoint at `gs://openpi-assets/checkpoints/pi05_libero/`. This
checkpoint was trained in openpi with the `pi05_libero` config.

| Model | Libero Spatial | Libero Object | Libero Goal | Libero 10 | Average |
|-------|---------------|---------------|-------------|-----------|---------|
| π0.5 @ 30k (finetuned) | 98.8 | 98.2 | 98.0 | 92.4 | 96.85

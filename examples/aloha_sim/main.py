import dataclasses
import logging
import pathlib

import matplotlib.pyplot as plt
import numpy as np
import tyro

import env as _env
from openpi_client import action_chunk_broker, websocket_client_policy
from openpi_client.runtime import runtime as _runtime
from openpi_client.runtime import subscriber as _subscriber
from openpi_client.runtime.agents import policy_agent as _policy_agent
import saver as _saver


class ActionPrinterSubscriber(_subscriber.Subscriber):
    """一个订阅者，用于打印机械臂接收到的动作指令。"""

    def on_episode_start(self) -> None:
        logging.info("ActionPrinter: 开始新回合。")

    def on_step(self, observation: dict, action: dict) -> None:
        logging.info(f"机器人接收到的动作: {action}")

    def on_episode_end(self) -> None:
        logging.info("ActionPrinter: 回合结束。")


class ImageDisplayerSubscriber(_subscriber.Subscriber):
    """一个订阅者，使用 matplotlib 实时显示观测图像。"""

    def __init__(self, window_name="实时仿真画面"):
        self._window_name = window_name
        self._fig = None
        self._ax = None
        self._im = None

    def on_episode_start(self) -> None:
        """在回合开始时，打开交互模式并创建图像窗口。"""
        if self._fig is None:
            plt.ion()  # 打开交互模式
            self._fig, self._ax = plt.subplots()
            self._fig.canvas.manager.set_window_title(self._window_name)

    def on_step(self, observation: dict, action: dict) -> None:
        """在每一步更新显示的图像。"""
        img_chw = observation["images"]["cam_high"]
        img_hwc = np.transpose(img_chw, (1, 2, 0))  # 转换为 (H, W, C) 格式

        if self._im is None:
            # 第一次，创建图像
            self._im = self._ax.imshow(img_hwc)
            self._ax.axis('off')  # 关闭坐标轴
            plt.tight_layout()
        else:
            # 后续步骤，只更新图像数据
            self._im.set_data(img_hwc)

        # 暂停一小段时间以允许图像更新
        plt.pause(0.001)

    def on_episode_end(self) -> None:
        """在回合结束时不执行任何操作，以保持窗口打开。"""
        pass

    def close(self):
        """关闭 matplotlib 窗口。"""
        if self._fig is not None:
            plt.ioff()
            plt.close(self._fig)


@dataclasses.dataclass
class Args:
    out_dir: pathlib.Path = pathlib.Path("data/aloha_sim/videos")
    task: str = "gym_aloha/AlohaTransferCube-v0"
    seed: int = 0
    action_horizon: int = 10
    host: str = "0.0.0.0"
    port: int = 8000
    display: bool = True  # 控制是否显示实时图像
    num_episodes: int = 5
    max_episode_steps: int = 500


def main(args: Args) -> None:
    # 初始化订阅者列表，默认包含视频保存器和动作打印器
    subscribers = [
        _saver.VideoSaver(args.out_dir),
        ActionPrinterSubscriber(),
    ]

    # 根据 display 参数决定是否添加图像显示器
    displayer = None
    if args.display:
        displayer = ImageDisplayerSubscriber()
        subscribers.append(displayer)

    runtime = _runtime.Runtime(
        environment=_env.AlohaSimEnvironment(
            task=args.task,
            seed=args.seed,
        ),
        agent=_policy_agent.PolicyAgent(
            policy=action_chunk_broker.ActionChunkBroker(
                policy=websocket_client_policy.WebsocketClientPolicy(
                    host=args.host,
                    port=args.port,
                ),
                action_horizon=args.action_horizon,
            )
        ),
        subscribers=subscribers,
        max_hz=50,
        num_episodes=args.num_episodes,
        max_episode_steps=args.max_episode_steps,
    )

    try:
        runtime.run()
    finally:
        # 确保在程序结束时关闭显示窗口
        if displayer:
            displayer.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, force=True)
    tyro.cli(main)

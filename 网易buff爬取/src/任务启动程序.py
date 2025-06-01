import subprocess
import time


def start_task():
    return subprocess.Popen(['python', '04-修改冗余.py'])


def main():
    while True:
        # 启动任务
        process = start_task()
        print(f"Started task with PID: {process.pid}")
        # 等待两个小时（7200秒）
        time.sleep(600)
        process.terminate()
        process.wait()
        print(f"Terminated task with PID: {process.pid}")
        # 稍作等待，确保任务完全关闭
        time.sleep(5)


if __name__ == "__main__":
    main()

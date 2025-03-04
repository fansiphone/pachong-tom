import re
import datetime
import logging
from typing import Set, Optional
import requests
from fetch import raw2fastly, session, LOCAL

logging.basicConfig(level=logging.INFO)

def safe_get(url: str, max_retries: int = 3) -> Optional[requests.Response]:
    for _ in range(max_retries):
        try:
            response = session.get(url, timeout=15)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            logging.error(f"请求失败: {url}, 错误: {e}")
    return None

def sharkdoor() -> Set[str]:
    url = datetime.datetime.now().strftime(
        'https://api.github.com/repos/sharkDoor/vpn-free-nodes/contents/node-list/%Y-%m?ref=master')
    res = safe_get(url)
    if not res:
        return set()
    
    res_json = res.json()
    latest_file = res_json[-1]['download_url']
    res_content = safe_get(raw2fastly(latest_file))
    if not res_content:
        return set()
    
    nodes = set()
    for line in res_content.text.split('\n'):
        if '://' in line:
            parts = line.split('|')
            if len(parts) >= 3:
                nodes.add(parts[-2].strip())
    return nodes

def peasoft() -> Set[str]:
    res = safe_get("https://gist.githubusercontent.com/peasoft/8a0613b7a2be881d1b793a6bb7536281/raw/")
    return set(res.text.splitlines()) if res else set()

AUTOFETCH = [sharkdoor, peasoft]

if __name__ == '__main__':
    logging.info("启动节点抓取...")
    all_nodes = set()
    for func in AUTOFETCH:
        try:
            nodes = func()
            all_nodes.update(nodes)
            logging.info(f"{func.__name__} 抓取成功: {len(nodes)} 节点")
        except Exception as e:
            logging.error(f"{func.__name__} 抓取失败: {e}")
    
    logging.info(f"总计抓取节点: {len(all_nodes)}")
    # 示例：保存到文件
    with open("nodes.txt", "w") as f:
        f.write("\n".join(all_nodes))

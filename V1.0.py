from pymem import Pymem
import struct

logo = """
=====================================================

微本绕过无法登录问题
支持版本:3.9.12.57
by: 响应云安全
公众号: 响应云SRC
我发现有人拿这玩意卖钱，以防割韭菜
关注公众号软件会面会更新
=======================================================
=======================================================
此版本下载地址: https://upfile.live/zh-cn/files/3927e486
链接失效扣后台
========================================================
"""

print(logo)


def fix_wechat_version():
    process_name = "WeChat.exe"
    # 只需要匹配文件名部分
    target_module_part = "wechatwin.dll"
    
    search_value = 0x63090C39
    replace_value = 0xF254160E

    try:
        # 1. 连接进程
        pm = Pymem(process_name)
        print(f"已成功连接到 {process_name}")

        # 2. 查找模块 (修改了匹配逻辑)
        module = None
        print("正在检索模块列表...")
        for m in pm.list_modules():
            # 使用 .lower() 并检查是否以目标字符串结尾
            if m.filename.lower().endswith(target_module_part):
                module = m
                break
        
        if not module:
            print(f"错误：未能在进程中找到 {target_module_part}")
            print("当前加载的部分模块如下(供调试):")
            for m in list(pm.list_modules())[:5]: # 只打印前5个看下路径格式
                print(f" - {m.filename}")
            return

        base_address = module.lpBaseOfDll
        module_size = module.SizeOfImage
        print(f"找到模块: {module.filename}")
        print(f"基址: {hex(base_address)}, 大小: {module_size}")

        # 3. 准备搜索数据
        search_bytes = struct.pack('<I', search_value)
        replace_bytes = struct.pack('<I', replace_value)

        # 4. 扫描并修改
        print(f"开始在模块范围内搜索 {hex(search_value)} ...")
        
        found_count = 0
        # 为了提高效率，直接读取整个模块内存到 Python 处理但这里维持逐个读取以保持稳定
        current_addr = base_address
        end_addr = base_address + module_size

        while current_addr < end_addr - 4:
            try:
                # 读取 4 字节
                content = pm.read_bytes(current_addr, 4)
                if content == search_bytes:
                    pm.write_bytes(current_addr, replace_bytes, 4)
                    print(f"成功修改地址: {hex(current_addr)}")
                    found_count += 1
                current_addr += 4 # 4字节对齐扫描
            except:
                current_addr += 4
                continue

        if found_count == 0:
            print("扫描完成，但没有发现匹配的版本号。可能已经修改过，或者该版本内存特征不同。")
        else:
            print(f"修改成功！共替换了 {found_count} 处特征码。")
            print("现在请尝试在微信中扫码登录。")

    except Exception as e:
        print(f"运行出错: {e}")
        print("提示：请确保以【管理员身份】运行终端/编辑器。")

if __name__ == "__main__":
    fix_wechat_version()

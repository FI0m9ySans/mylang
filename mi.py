#!/usr/bin/env python3
import sys
import os
import shutil
import urllib.request
import tempfile
import zipfile

def get_package_dir():
    package_dir = os.path.join(os.path.expanduser("~"), ".mylang", "packages")
    os.makedirs(package_dir, exist_ok=True)
    return package_dir

def install_from_file(filename, version=None):
    package_dir = get_package_dir()
    
    if not os.path.exists(filename):
        print(f"错误: 文件 '{filename}' 不存在")
        return 1
    
    # 提取包名
    package_name = os.path.basename(filename)
    if package_name.endswith('.mylang'):
        package_name = package_name[:-7]  # 移除 .mylang 扩展名
    
    # 确定目标文件名
    if version:
        target_name = f"{package_name}-{version}.mylang"
    else:
        target_name = f"{package_name}.mylang"
    
    target_path = os.path.join(package_dir, target_name)
    
    try:
        shutil.copy2(filename, target_path)
        print(f"成功安装包: {package_name}" + (f" 版本 {version}" if version else ""))
        return 0
    except Exception as e:
        print(f"安装失败: {e}")
        return 1

def install_from_url(url, version=None):
    package_dir = get_package_dir()
    
    try:
        # 下载文件
        with urllib.request.urlopen(url) as response:
            content = response.read()
        
        # 提取包名
        package_name = os.path.basename(url)
        if package_name.endswith('.mylang'):
            package_name = package_name[:-7]
        elif package_name.endswith('.zip'):
            package_name = package_name[:-4]
        
        # 处理ZIP文件
        if url.endswith('.zip'):
            with tempfile.TemporaryDirectory() as temp_dir:
                zip_path = os.path.join(temp_dir, "package.zip")
                with open(zip_path, 'wb') as f:
                    f.write(content)
                
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                
                # 查找 .mylang 文件
                mylang_files = [f for f in os.listdir(temp_dir) if f.endswith('.mylang')]
                if not mylang_files:
                    print("错误: ZIP文件中没有找到 .mylang 文件")
                    return 1
                
                # 安装所有 .mylang 文件
                for file in mylang_files:
                    source_path = os.path.join(temp_dir, file)
                    target_name = file
                    if version and not file.endswith(f"-{version}.mylang"):
                        name_without_ext = file[:-7]  # 移除 .mylang
                        target_name = f"{name_without_ext}-{version}.mylang"
                    
                    target_path = os.path.join(package_dir, target_name)
                    shutil.copy2(source_path, target_path)
                    print(f"成功安装包: {file}" + (f" 版本 {version}" if version else ""))
        else:
            # 直接安装 .mylang 文件
            target_name = f"{package_name}.mylang"
            if version:
                target_name = f"{package_name}-{version}.mylang"
            
            target_path = os.path.join(package_dir, target_name)
            with open(target_path, 'wb') as f:
                f.write(content)
            
            print(f"成功安装包: {package_name}" + (f" 版本 {version}" if version else ""))
        
        return 0
    except Exception as e:
        print(f"安装失败: {e}")
        return 1

def main():
    if len(sys.argv) < 2:
        print("用法: mi <包文件或URL> [版本号]")
        print("示例:")
        print("  mi math.mylang")
        print("  mi math.mylang 1.0")
        print("  mi https://example.com/packages/math.mylang")
        print("  mi https://example.com/packages/math.zip 1.0")
        return 1
    
    target = sys.argv[1]
    version = sys.argv[2] if len(sys.argv) > 2 else None
    
    if target.startswith('http://') or target.startswith('https://'):
        return install_from_url(target, version)
    else:
        return install_from_file(target, version)

if __name__ == "__main__":
    sys.exit(main())
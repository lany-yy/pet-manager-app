[app]

# 应用标题
title = 猫狗宠物管理系统

# 应用名称（包名）
package.name = petmanager

# 包组织
package.domain = com.petmanager

# 版本信息
version = 1.0.0

# 源代码目录
source.dir = .

# 应用入口点
source.include_exts = py,png,jpg,kv,atlas

# 主模块
main = main.py

# 需求文件
requirements = python3,kivy>=2.1.0,kivymd>=1.1.1,pillow,matplotlib,plyer

# 窗口配置
fullscreen = 0
orientation = portrait

# Android配置
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,CAMERA

# Android API级别
android.minapi = 21
android.api = 30

# 支持的架构
android.archs = arm64-v8a,armeabi-v7a

# 打包输出目录
bin_dir = bin

android.accept_sdk_license = True

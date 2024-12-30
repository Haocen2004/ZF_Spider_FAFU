# ZF_Spider_FAFU

## 简介
这是一个用Python写的正方教务抢课脚本，由于每个学校的教务系统可能存在改动，所以不一定可用。  
本Repo进行修改以适配Fafu教务系统  
一次只能选一门课，如需多门课程请多开脚本，`session`可以共用，不会冲突。

## 使用方法
复制 `config.json.sport.example` 或者 `config.json.public.example` 为 `config.json` 并填写内容
- `config.json.sport.example` 为体育选课  
- `config.json.public.example` 为公选课选课

安装运行依赖 `pip install requests pillow bs4`  
运行 `python main.py`

## 配置文件说明
```json
{
    "url":"http://jwgl.fafu.edu.cn/", // 选课用教务系统网址 内外网均可
    "student_number":"",  // 学号
    "password":"",  // 密码
    "gnmkdm":"N121205",  // 选课界面网络请求头里有该字段 自行抓包获取
    "sub_class_type":"板块（9）", // 选课界面name为ddl_xqbs的select的对应value
    "class_type": 1 // 0 为体育抢课  1 为公选课抢课
}
```

## 关于
原文博客地址：https://vhyz.github.io/2018/06/12/用Python实现模拟登录正方教务系统抢课/
